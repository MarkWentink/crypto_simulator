import streamlit as st

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

st.write("# Trading Bot Simulator")

st.write('Curious about how various trading strategies would have played out on the crypto-market? ')

st.markdown(
    """
    
    ## How to use

    👈 From the sidebar, you can:
    - **Get an overview of the crypto market**, including latest prices and correlation analysis.
    - **Create a crypto bot** which will simulate a specific portfolio allocation and trading strategy.
    - **Compare the performace of your bots** along with some examples.
"""
)



st.divider()

st.markdown(
    """
    **Version Notes**

    This is v.1 : It contains limited options in terms of defining trading strategies. 
    The focus is on getting the infrastructure in place so that it can be easily expanded on.

    **Future Features**

    - Cross-validate annualised return and volatility on different time windows
    - Expand rules-based strategies to allow for multiple buy and sell triggers
    - Add model-based strategies, that will buy and sell based on predictive modelling
    - Add detailed logs of what trades a bot has made, how many of them were profitable, and by how much

"""
)