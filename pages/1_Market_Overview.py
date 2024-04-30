

import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import joblib
import math
import plotly.express as px
st.set_page_config(page_title="Market Overview", page_icon="📈")


st.title("Market Overview")

st.write('''Here, you can get a quick overview of the major crypto-currencies. 
         You will find up to date daily prices, as well as a brief correlation analysis over the whole of the time range.''')
st.write('Use the checkboxes on the left to select which coins you are interested in. ')

@st.cache_data # <- add decorators after tried running the load multiple times
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("prices.csv")
df = df.set_index('Date')
df = df.map(lambda x: round(x, 4 - int(math.floor(math.log10(abs(x))))))
df = df.rename(columns={'UNI7083-USD':'UNI-USD', 'STX4847-USD':'STX-USD'})


#st.sidebar.subheader("Usage filters")


with open('token_list.txt') as f:
    token_list = [x.strip() for x in f.readlines()]
tokens = [x for x in token_list if x not in ['USD', 'USDT-USD', 'USDC-USD', 'DAI-USD', 'SHIB-USD']]
tokens.remove('UNI7083-USD')
tokens.remove('STX4847-USD')
tokens.extend(['UNI-USD', 'STX-USD'])




st.sidebar.subheader('select coins')
side_cols = st.sidebar.columns(2)
i = 0
for token in tokens:
    with side_cols[i%2]:
        globals()[token[:-4]] = st.checkbox(token[:-4], value = (i < 6))
    i += 1
st.subheader('Daily prices in USD')
df = df[[x for x in tokens if globals()[x[:-4]]==True]]
df.columns = [x[:-4] for x in df.columns]
st.dataframe(df, height = 300, use_container_width=True)



#######################################################################################################################################
### Line graph
st.divider()
st.subheader('Historical Prices - Absolute')
st.write('''As well as selecting coins in the left sidebar, 
         you can click their label in the graph legend to include or exclude them.
         This can help if you need a quick look at one particular, or a pair of currencies.''')

fig = px.line(df)
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
st.plotly_chart(fig)


st.subheader('Historical Prices - Normalised')
st.write('''Below, all prices have been normalised to start at 1, so that relative change can be more easily visualised.
         For example, although Bitcoin (BTC) has the highest absolute price, it's Solana (SOL) and Stacks (STX) that have seen
         the highest relative growth since 2023, currently worth about 10-15 times what they were back then.''')
norm_df = df.divide(df.iloc[0])
fig = px.line(norm_df)
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
st.plotly_chart(fig)

#######################################################################################################################################
### DATA ANALYSIS & VISUALIZATION

### B. Add filter on side bar after initial bar chart constructed



### A. Add a bar chart of usage per hour

st.subheader("Correlation Analysis")
st.write('The heatmap below shows the correlation coefficients of pairs of crypto-currencies.') 
st.write('''A correlation score close to 1 would indicate very similar price fluctuation behaviour between the coins.
         Scores close to 0 indicate there is no relationship between how two coins fluctuate, 
         while a negative number would indicate an opposing relationship: when one goes up, the other goes down.
         ''')
# set background colour from main theme
#sns.set_style(rc={'axes.facecolor':'#D6D5C9', 'figure.facecolor':'#D6D5C9'})
colours = sns.diverging_palette(220, 3, as_cmap=True,s=61, l=25)
corr_fig = sns.heatmap(df.corr(), cmap=colours, center=0, vmax=1, annot=True, mask = np.triu(df.corr()))
st.pyplot(corr_fig.figure)

# st.write('''**Warning**: The following pairs of tokens are very strongly correlated. 
#          Including both in your portfolio might create a false sense of diversification:''')
# for pair in [ x for x in list(zip(np.where(np.triu(df.corr()>0.9))[0], np.where(np.triu(df.corr()>0.9))[1])) if x[0] != x[1]]:
#     st.write(f'{df.columns[pair[0]]} and {df.columns[pair[1]]}')