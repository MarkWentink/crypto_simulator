import os
import joblib
import pandas as pd

import streamlit as st
import plotly.express as px

from crypto_bots_classes import formatted_plotter


st.set_page_config(page_title="Bot Comparisons", page_icon="🔍")
if 'bots' not in st.session_state:
    st.session_state['bots'] = [joblib.load('bots/'+file_name) for file_name in os.listdir('bots/')]

st.title("Bot Comparison")
st.write('''Once you have created some trading bots, you can compare their performance here.
         For comparison, we have pre-made a 'hold BTC only' bot and a 'hold an even split of everything' bot. ''')

bots = st.session_state['bots']

# Generate a summary table of bot metrics
bot_dict = {'Start Value': [],
'Current value' : [],
'Total return': [],
'Days held': [],
'Annualised return %':[],
'Volatility':[]}

for bot in bots:
    bot_dict['Start Value'].append(bot.start_value)
    bot_dict['Current value'].append(bot.valuate())
    bot_dict['Total return'].append(bot.valuate()-bot.start_value)
    bot_dict['Days held'].append(len(bot.values.index))
    bot_dict['Annualised return %'].append(round(bot.roi(), 1))
    bot_dict['Volatility'].append(round(bot.volatility(), 2))

comparison_df = pd.DataFrame.from_dict(bot_dict, orient='columns')
comparison_df.index=[bot.name for bot in bots]

st.subheader('Summary Table')
st.dataframe(comparison_df[['Current value', 'Total return', 'Annualised return %', 'Volatility']].sort_values(by='Annualised return %', ascending=False))


st.write('''**Note**: Volatility is calculated as the standard deviation of daily percentage changes.''')
st.write('''**Warning**: Although annualised returns are likely to be very high, this is not represented of the crypto market. 
         2023-01-01 happened to be a good time to get into the market.
         Future versions of this app will seek to cross-validate strategies with multiple starting points.''')


# portfolio comparison over time
st.subheader('Performance over time')
st.plotly_chart(formatted_plotter(bots))


# Delete bots button
m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #902923;
        color:#ffffff;
    }
    </style>""", unsafe_allow_html=True)
deleting = st.button('Delete all created bots')
if deleting:
    for path in ['bots/'+file_name for file_name in os.listdir('bots/') if file_name not in ['0_BTC only.pkl', '0_split all.pkl']]:
        os.remove(path)