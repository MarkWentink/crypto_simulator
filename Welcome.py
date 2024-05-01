import streamlit as st

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

st.write("# Build-a-Bot Trading Simulator")

st.write('Welcome to Build-a-Bot!')

st.write('''Are you curious about how various trading strategies play out on the crypto-market? 
         Interested in tinkering around with different scenarios?''')
st.write('''In this app, you can try out various portfolio allocations and trading strategies, and track their performance over time.
         By tracking annualised return and volatility, you can get a sense of how profitable and risky a certain approach would have been.''')


st.markdown(
    """
    
    ## How to use

    👈 From the sidebar, you can:
    - **Have a peek into the data under Market Overview**, including latest prices and correlation analysis.
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

    - Alternative visuals in the Market Overview that lend themselves better to currency comparisons
    - Cross-validate annualised return and volatility on different time windows
    - Expand rules-based strategies to allow for multiple buy and sell triggers
    - Add model-based strategies, that will buy and sell based on predictive modelling
    - Add detailed logs of what trades a bot has made, how many of them were profitable, and by how much
    - Add model-updating capabilities to avoid models going stale over time
    - Build functionality to automatically explore a wide range of trading strategy parameters. 

"""
)