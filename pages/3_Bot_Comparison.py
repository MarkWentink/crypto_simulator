import os
import joblib
import pandas as pd

import streamlit as st
import plotly.express as px


st.set_page_config(page_title="Bot Comparisons", page_icon="🔍")


st.title("Bot Comparison")
st.write('''Once you have created some trading bots, you can compare their performance here.
         For comparison, we have pre-made a 'hold BTC only' bot and a 'hold an even split of everything' bot. ''')


bots = [joblib.load('bots/'+file_name) for file_name in os.listdir('bots/')]

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


st.subheader('Performance over time')

plot_data = pd.DataFrame()
for bot in bots:
    plot_data = pd.concat([plot_data, pd.DataFrame(bot.value_history(), columns=[bot.name])])

fig = px.line(plot_data)
fig.update_xaxes(rangeslider_visible = True,
                    rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
))
fig.update_layout(legend_title_text='Portfolio', width=750)

st.plotly_chart(fig)


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