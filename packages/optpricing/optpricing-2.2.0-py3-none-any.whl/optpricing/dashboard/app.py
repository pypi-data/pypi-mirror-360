import streamlit as st

st.set_page_config(
    page_title="optpricing Library Showcase",
    layout="wide",
)

st.title("Welcome to the optpricing Library Showcase!")
st.sidebar.success("Select a tool above to begin.")

# ruff: noqa: E501
st.markdown(
    """
    This application is a showcase for a comprehensive, high-performance
    quantitative finance library built in Python.

    **Select a tool from the sidebar** to see different features in action:

    - **Calibration:** Calibrate models to market data and visualize the results.
    - **Pricer and Greeks:** An interactive tool to price options with any model/technique and see the effect of changing parameters.
    - **Financial Tools:** Utilities for pricing interest rate derivatives and analyzing put-call parity.

    This entire application is built on a robust, library with a focus
    on speed, accuracy, and extensibility.
    """
)
