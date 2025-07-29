import pandas as pd
import streamlit as st

from optpricing.atoms import Option, OptionType, Rate, Stock
from optpricing.models import (
    BatesModel,
    BSMModel,
    CEVModel,
    CGMYModel,
    HestonModel,
    HyperbolicModel,
    KouModel,
    MertonJumpModel,
    NIGModel,
    SABRJumpModel,
    SABRModel,
    VarianceGammaModel,
)
from optpricing.techniques import (
    AmericanMonteCarloTechnique,
    ClosedFormTechnique,
    CRRTechnique,
    FFTTechnique,
    IntegrationTechnique,
    LeisenReimerTechnique,
    MonteCarloTechnique,
    PDETechnique,
    TOPMTechnique,
)

st.set_page_config(layout="wide", page_title="optpricing | Pricer")
st.title("On-Demand Pricer & Greek Analysis")
# ruff: noqa: E501
st.caption(
    "Price any option with any model and technique. Manually set all parameters to see their effect."
)

# Model and Technique Selection
MODEL_MAP = {
    "Bates": BatesModel,
    "Black-Scholes-Merton (BSM)": BSMModel,
    "Constant Elasticity of Variance (CEV)": CEVModel,
    "Carr-Geman-Madan-Yor (CGMY)": CGMYModel,
    "Heston": HestonModel,
    "Hyperbolic": HyperbolicModel,
    "Kou Double-Exponential": KouModel,
    "Merton Jump-Diffusion": MertonJumpModel,
    "Normal Inverse Gaussian (NIG)": NIGModel,
    "SABR": SABRModel,
    "SABR Jump": SABRJumpModel,
    "Variance Gamma (VG)": VarianceGammaModel,
}

TECHNIQUE_MAP = {
    "Analytic/Closed-Form": ClosedFormTechnique,
    "Integration": IntegrationTechnique,
    "FFT": FFTTechnique,
    "Monte Carlo": MonteCarloTechnique,
    "PDE": PDETechnique,
    "Leisen-Reimer": LeisenReimerTechnique,
    "CRR": CRRTechnique,
    "TOPM": TOPMTechnique,
}

col1, col2 = st.columns(2)
with col1:
    model_name = st.selectbox("Select Model", list(MODEL_MAP.keys()))

# Get the selected model class and create a dummy instance to check its properties
model_class = MODEL_MAP[model_name]
try:
    dummy_model_instance = model_class()
except TypeError:
    dummy_model_instance = model_class.__new__(model_class)

# Dynamic Technique Selector
supported_techs = []
if dummy_model_instance.has_closed_form:
    supported_techs.append("Analytic/Closed-Form")
if dummy_model_instance.supports_cf:
    supported_techs.extend(["Integration", "FFT"])

mc_supported = (
    dummy_model_instance.supports_sde
    or getattr(dummy_model_instance, "is_pure_levy", False)
    or getattr(dummy_model_instance, "has_exact_sampler", False)
)

if mc_supported and model_name != "Hyperbolic":
    supported_techs.append("Monte Carlo")

if dummy_model_instance.supports_pde:
    supported_techs.append("PDE")
if model_name == "Black-Scholes-Merton (BSM)":
    supported_techs.extend(["Leisen-Reimer", "CRR", "TOPM"])

with col2:
    selected_index = 0
    if supported_techs and st.session_state.get("technique_name") in supported_techs:
        selected_index = supported_techs.index(st.session_state.technique_name)

    if not supported_techs:
        st.warning(f"No pricing techniques available for {model_name}.")
        technique_name = None
    else:
        technique_name = st.selectbox(
            "Select Technique",
            supported_techs,
            index=selected_index,
            key="technique_name",
        )

    exercise_style = "European"

    american_supported_techs = [
        "Leisen-Reimer",
        "CRR",
        "TOPM",
        "Monte Carlo",
    ]

    if technique_name in american_supported_techs:
        exercise_style = st.radio(
            "Exercise Style",
            ["European", "American"],
            horizontal=True,
            key="exercise_style",
        )

# Parameter Inputs
st.subheader("Market Parameters")
cols = st.columns(4)
spot = cols[0].number_input("Spot Price", value=100.0, step=1.0)
strike = cols[1].number_input("Strike Price", value=100.0, step=1.0)
maturity = cols[2].number_input("Maturity (Years)", value=1.0, min_value=0.01, step=0.1)
rate_val = cols[3].number_input("Risk-Free Rate", value=0.05, step=0.01, format="%.2f")
div_val = cols[0].number_input("Dividend Yield", value=0.02, step=0.01, format="%.2f")
option_type = cols[1].selectbox("Option Type", ("CALL", "PUT"))

# Dynamic Model Parameter Inputs
st.subheader(f"{model_name} Model Parameters")
params = {}

if hasattr(dummy_model_instance, "default_params"):
    param_defs = getattr(dummy_model_instance, "param_defs", {})

    num_cols = 4
    cols = st.columns(num_cols)

    for i, (p_name, p_default_value) in enumerate(
        dummy_model_instance.default_params.items()
    ):
        p_def = param_defs.get(p_name, {})

        # Skip technical/non-user-facing parameters
        if p_name in ["max_sum_terms"]:
            continue

        params[p_name] = cols[i % num_cols].number_input(
            label=p_def.get("label", p_name.replace("_", " ").title()),
            value=float(p_default_value),
            min_value=p_def.get("min"),
            max_value=p_def.get("max"),
            step=p_def.get("step", 0.01),
            format="%.4f",
            key=f"{model_name}_{p_name}",  # Unique key to avoid widget state issues
        )

if st.button("Calculate Price & Greeks"):
    # Instantiate Objects
    stock = Stock(spot=spot, dividend=div_val)
    rate = Rate(rate=rate_val)
    option = Option(
        strike=strike, maturity=maturity, option_type=OptionType[option_type]
    )

    # merge UI params with non-UI default params
    full_params = model_class.default_params.copy()
    full_params.update(params)

    model = model_class(params=full_params)
    is_american_flag = exercise_style == "American"

    if technique_name == "Monte Carlo" and is_american_flag:
        technique = AmericanMonteCarloTechnique()
        st.info("Using Longstaff-Schwartz for American Monte Carlo.")
    else:
        try:
            technique = TECHNIQUE_MAP[technique_name](is_american=is_american_flag)
        except TypeError:
            technique = TECHNIQUE_MAP[technique_name]()

    # Prepare kwargs for techniques that need extra info (e.g., Heston's v0)
    pricing_kwargs = full_params.copy()

    # Calculate and Display
    with st.spinner("Calculating..."):
        try:
            results_data = {}

            results_data["Price"] = technique.price(
                option, stock, model, rate, **pricing_kwargs
            ).price

            skip_mc_greeks = model.has_jumps and isinstance(
                technique, MonteCarloTechnique
            )

            if skip_mc_greeks:
                st.info(
                    "Note: Greeks for jump-diffusion models under Monte Carlo are unstable and not displayed."
                )
                results_data["Delta"] = "N/A"
                results_data["Gamma"] = "N/A"
                results_data["Vega"] = "N/A"
                results_data["Theta"] = "N/A"
                results_data["Rho"] = "N/A"

            else:
                results_data["Delta"] = technique.delta(
                    option,
                    stock,
                    model,
                    rate,
                    **pricing_kwargs,
                )
                results_data["Gamma"] = technique.gamma(
                    option,
                    stock,
                    model,
                    rate,
                    **pricing_kwargs,
                )
                results_data["Vega"] = technique.vega(
                    option,
                    stock,
                    model,
                    rate,
                    **pricing_kwargs,
                )
                results_data["Theta"] = technique.theta(
                    option,
                    stock,
                    model,
                    rate,
                    **pricing_kwargs,
                )
                results_data["Rho"] = technique.rho(
                    option,
                    stock,
                    model,
                    rate,
                    **pricing_kwargs,
                )

            st.dataframe(pd.DataFrame([results_data]))

        except Exception as e:
            st.error(f"Calculation failed: {e}")
            st.exception(e)
