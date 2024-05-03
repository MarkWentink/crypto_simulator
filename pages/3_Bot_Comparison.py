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

# Delete bots button
m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #902923;
        color:#ffffff;
    }
    </style>""", unsafe_allow_html=True)
if st.button('Delete all created bots'):
    st.session_state['bots'] = [joblib.load('bots/'+file_name) for file_name in os.listdir('bots/')]
    st.experimental_rerun()



# portfolio comparison over time
st.subheader('Performance over time')
st.plotly_chart(formatted_plotter(bots))




# Deep dive
st.subheader('Trade log')
with st.columns(3)[0]:
    deep = st.selectbox('Bot', options = tuple([bot for bot in bots]), format_func=lambda x : x.name)

if deep.trades_log.shape[0] > 0:
    st.dataframe(deep.trades_log, use_container_width=True)
    st.write(f"**{deep.trades_log.shape[0]}** trades were made, **{sum(deep.trades_log['profit']>0)}** of which were profitable and **{sum(deep.trades_log['profit'].isna())}** remain open.")
    st.write(f"The average profit per trade is **\${round(deep.trades_log['profit'].mean(), 2)}** or **{round((deep.trades_log['profit']/deep.trades_log['buy_value']).mean(), 2)}**\%.")
    st.write(f"The best trade made **\${round(deep.trades_log['profit'].max(), 2)}** and the worst **\${round(deep.trades_log['profit'].min(), 2)}**")
else:
    st.write('No trades were made. This was the original dollar allocation:')
    initial = pd.DataFrame(deep.values.iloc[0, :])
    initial.index = [x[:-4] if x != 'USD' else x for x in initial.index]
    st.dataframe(initial)