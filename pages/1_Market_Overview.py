
# Imports
import math
import numpy as np
import seaborn as sns
import plotly.express as px

import streamlit as st

from crypto_bots_classes import load_data, load_tokens, formatted_plotter

# Configs
st.set_page_config(page_title="Market Overview", page_icon="📈")


# Introduction
st.title("Market Overview")

st.write('''Here, you can get a quick overview of the major crypto-currencies. 
         You will find up to date daily prices, as well as a brief correlation analysis over the whole of the time range.''')
st.write('Use the checkboxes on the left to select which coins you are interested in. ')

# Load data, round to 5 significant figures, and rename some clumsy column names
df = load_data("data/prices.csv")

# Import list of token names, filter out stable coins, and match naming convention above
tokens = load_tokens('data/token_list.txt')

# Sidebar
# Create checkboxes for the considered tokens, store them as global boolean variables, set the first 5 as True
st.sidebar.subheader('select coins')
side_cols = st.sidebar.columns(2)
i = 0
for token in tokens:
    with side_cols[i%2]:
        globals()[token[:-4]] = st.checkbox(token[:-4], value = (i < 6))
    i += 1

# Prices dataframe
st.subheader('Daily prices in USD')
df = df[[x for x in tokens if globals()[x[:-4]]==True]]
df.columns = [x[:-4] for x in df.columns]
st.dataframe(df, height = 300, use_container_width=True)


# Historical Prices - absolute
st.divider()
st.subheader('Historical Prices - Absolute')
st.write('''As well as selecting coins in the left sidebar, 
         you can click their label in the graph legend to include or exclude them.
         This can help if you need a quick look at one particular, or a pair of currencies.''')
st.plotly_chart(formatted_plotter(df))


# Historical Prices - normalised
st.subheader('Historical Prices - Normalised')
st.write('''Below, all prices have been normalised to start at 1, so that relative change can be more easily visualised.
         For example, although Bitcoin (BTC) has the highest absolute price, it's Solana (SOL) and Stacks (STX) that have seen
         the highest relative growth since 2023, currently worth about 10-15 times what they were back then.''')
norm_df = df.divide(df.iloc[0])
st.plotly_chart(formatted_plotter(norm_df))


# Correlation heatmap
st.subheader("Correlation Analysis")
st.write('The heatmap below shows the correlation coefficients of pairs of crypto-currencies.') 
st.write('''A correlation score close to 1 would indicate very similar price fluctuation behaviour between the coins.
         Scores close to 0 indicate there is no relationship between how two coins fluctuate, 
         while a negative number would indicate an opposing relationship: when one goes up, the other goes down.
         ''')

sns.set_style(rc={'axes.facecolor':'#D6D5C9', 'figure.facecolor':'#D6D5C9'})
# heatmap
corr_fig = sns.heatmap(df.corr(), 
                       cmap=sns.diverging_palette(220, 3, as_cmap=True,s=61, l=25), 
                       center=0, 
                       vmax=1, 
                       annot=True, 
                       mask = np.triu(df.corr()))
st.pyplot(corr_fig.figure)
