
# Imports
import pandas as pd
import joblib
import json

import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime


from crypto_bots_classes import Portfolio, StrategyHold, StrategyRules, load_data, load_tokens


# streamlit Configs
st.set_page_config(page_title="Bot Creator", page_icon="🤖")

# Firestore log file config
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="build-a-bot-traffic-log")

# doc_ref = db.collection("bot_creation").document('test2')
# st.write(str(datetime.today()))
# # doc_ref.set({'foo':'bar'})
# doc_ref.set({'timestamp':datetime.today(),
#              'bot_name':'Omega',
#              'strategy':'Hold',
#              'allocation':{'USD':1000},
#              'roi':3.24,
#              'volatility':2.11})

# Introduction
st.title("Bot Creator")

st.write('Time to experiment! Here, you can create simulated portfolios and trading bots.')
st.markdown(
    '''
    - Start by giving your bot a name, so we know what to call it!
    - Pick a trading strategy. This determines how your bot decides to buy and sell currencies.
    - Pick a portfolio allocation. If you're defining a rules-based strategy, your bot simply starts with $1000 cash,
         but you can still select which currencies you want your bot to consider when making trades.
    - Review the details of your bot, and click **save**.
''')
st.write("Once created, you can compare your bots performance against others on the 'Bot Comparison' page")


# Load data
prices = load_data("data/prices.csv")


# Load list of considered tokens
tokens = load_tokens('data/token_list.txt')


# Name your bot
st.subheader('Name your bot')
with st.columns(2)[0]:
    bot_name = st.text_input('Name', value='my_bot')


# Trade strategies
st.divider()
st.subheader('Trading Strategy')

valid_bot = False # if the trading strategy section is filled in correctly, the bot summary section appears

with st.columns(2)[0]:
    strategy = st.selectbox('Choose a trading strategy', options = ['HOLD', 'RULES'])

if strategy == 'HOLD':
    st.write('''A HOLD strategy does not perform any trades. 
             It simply holds on to the initially defined portfolio split, and tracks its value over time.''')
    hold = StrategyHold()

    st.divider()
    st.subheader('Portfolio Allocation')
    
    alloc = st.selectbox('You can evenly spread the money over a selection of coins, or manually define an allocation.', 
                         options = ['Even', 'Manual'])
    # Even allocation
    if alloc == 'Even':
        st.write('Select which tokens to include in your portfolio:')

        cols = st.columns(5)
        i = 0
        for token in tokens:
            with cols[i%5]:    
                globals()[token[:-4]] = st.checkbox(token[:-4], value = (i < 4))
            i += 1
        alloc_tokens = [x for x in tokens if globals()[x[:-4]]==True]
        allocation = {x: 1/len(alloc_tokens) for x in alloc_tokens}
        bot = Portfolio(bot_name, allocation, '2023-01-01', 1000, prices, hold)
        valid_bot = True

    # Manual allocation
    elif alloc == 'Manual':
        st.write('Fill in a dollar amount for the tokens you want in your portfolio. The total must add up to $1000.')

        cols = st.columns(5)
        i = 0
        for token in tokens:
            with cols[i%5]:
                globals()[token[:-4]] = st.number_input(token[:-4], 0, 1000, 0, step=50)
            i+= 1
        st.write(f'**You have ${1000-sum([globals()[x[:-4]] for x in tokens])} left to allocate before you can continue**')
        if sum([globals()[x[:-4]] for x in tokens]) == 1000:
            allocation = {x:globals()[x[:-4]]/1000 for x in tokens if globals()[x[:-4]] != 0}
            bot = Portfolio(bot_name, allocation, '2023-01-01', 1000, prices, hold)
            valid_bot = True

elif strategy == 'RULES':
    st.write('''A rules-based strategy will buy and sell currency based on specified conditions. 
             Use the fields below to define your trading strategy: ''')
    st.write('')
    rules_cols = st.columns(2, gap='medium')

    # Buy rules
    with rules_cols[0]:
        st.write('**1. Define a BUY rule:**')
        buy_rule = st.selectbox('Consecutive or window?', options = ['consecutive', 'window'])
        
        if buy_rule == 'consecutive':
            st.write('A consecutive rule will require an increase in price over a number of consecutive days before buying.')
            buy_period = st.number_input('number of consecutive days', 1, 100, 2, 1)
            #buy_signal = st.number_input(' minimal \% increase. Put 0 for any', 0, 100, 0)
            exposure = st.number_input('Max share of portfolio in \%', 1, 100, 10)
            buy_rule_string = f'BUY up to **{exposure}\%** of total portfolio value of a coin if its price has gone up on at least **{buy_period}** consecutive days.'

        elif buy_rule == 'window':
            st.write('A window rule will require a certain percent increase in price over a specified time window')
            buy_period = st.number_input('time window in days', 1, 100, 3, 1)
            buy_signal = st.number_input('percent increase required', 1, 100, 10, 1)
            exposure = st.number_input('Max share of portfolio in \%', 1, 100, 20)
            buy_rule_string = f'BUY up to **{exposure}\%** of total portfolio value of a coin if its price has gone up by at least **{buy_signal}\%** in the last **{buy_period}** days.'
    
    # sell rules
    with rules_cols[1]:
        st.write('**2. Define a SELL rule**')
        sell_rule = st.selectbox('hold or reversal?', options = ['hold', 'reversal']) 

        if sell_rule == 'hold':
            st.write('A hold rule will hold on to a currency for a specified amount of time before selling again.')
            sell_days = st.number_input('How many days to hold for?', 1, 100, 1, 1)
            sell_rule_string = f"SELL a coin once it's been held for **{sell_days}** days."

        elif sell_rule == 'reversal':
            st.write('A reversal rule will hold on to a coin until its price starts dropping on X consecutive days.')
            sell_days = st.number_input('patience: sell after how many consecutive drops?', 1, 100, 2, 1)
            sell_rule_string = f"SELL a coin once its price has dropped on **{sell_days}** consecutive days."

    # Rule summary
    st.write('**Defined rules**')
    st.write(buy_rule_string)
    st.write(sell_rule_string)

    trend = StrategyRules(buy_rule, buy_period, 0, sell_rule, sell_days, exposure)
    
    st.divider()
    st.subheader('Portfolio Allocation')
    st.write('For a rules based strategy, your bot will start with a $1000 in cash, and no crypto-currencies.')
    st.write('''Below, you can select which coins you want to consider in your strategy. 
             Those not ticked will be ignored even if they meet the buy rule. ''')

    st.write('Select which tokens to consider in your portfolio:')

    cols = st.columns(5)
    i = 0
    for token in tokens:
        with cols[i%5]:    
            globals()[token[:-4]] = st.checkbox(token[:-4], value = (i < 4))
        i += 1
    alloc_tokens = [x for x in tokens if globals()[x[:-4]]==True]
    allocation = {x: 0 for x in alloc_tokens}
    allocation['USD'] = 1
    bot = Portfolio(bot_name, allocation, '2023-01-01', 1000, prices, trend)
    valid_bot = True


# Summary section
if valid_bot:

    st.divider()
    st.subheader('Bot Summary')
    st.write("When you're ready, save your bot, and compare its performance against others on the Bot Comparison page")

    summary_cols = st.columns(3)
    # High level overview and save button
    with summary_cols[0]:
        st.markdown('__Bot Details__:')
        st.write('__Bot name__:',bot.name )
        st.write('__Start Date__:', bot.holdings.index[0].date())
        st.write('__Start Amount__:', bot.start_value)
        st.write('')

        # Export bot button
        m = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #902923;
                color:#ffffff;
            }
            </style>""", unsafe_allow_html=True)
        save = st.button('Save bot')

        def save_bot(bot, prices, db):
            bot.new_simulate_update(prices)

            doc_ref = db.collection("bot_creation").document('test3')
            doc_ref.set({'timestamp':datetime.today(),
                         'bot_name':bot_name,
                         'strategy':bot.strategy.description,
                         'allocation':bot.initial_split,
                         'roi':bot.roi(),
                         'volatility':round(bot.volatility(), 2)})
            joblib.dump(bot, './bots/'+bot_name+'.pkl')
            st.write('Bot Saved')
        
        if save:
            save_bot(bot, prices, db)

            
    # strategy summary
    with summary_cols[1]:
        st.write('__Trading Strategy:__')
        if strategy == 'HOLD':
            st.write('__HOLD__')
            st.write('No trades are performed. The start allocation is maintained')
        elif strategy == 'RULES':
            st.write('__RULES__')
            st.write(buy_rule_string)
            st.write(sell_rule_string)
    # Allocation summary
    with summary_cols[2]:
        st.write('__Start allocation__:')
        allocation_df = pd.DataFrame(bot.values.iloc[0])
        allocation_df.columns = ['USD allocated']
        allocation_df.index = [x[:-4] if len(x)>4 else x for x in allocation_df.index]
        st.write(allocation_df)

    
