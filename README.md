# Discord Robinhood Stockbot
### Discord stock bot that utilizes an unofficial Robinhood API (robin_stocks) and discord API for market enthusiasts. 

### Discord commands:

Command prefix = '.'

#### Price checker - provide ticker names to receive the current price quickly. Condensed to allow mobile users to view it on one line. 
***********
    Ex: .p (arg1)
    EX: .p (arg1), (arg2), ... (argN)

    [during market hours]
    .p estc aapl msft spy 
    ESTC:  $92.31  +0.92% |L: 91.40   H: 93.59
    AAPL: $460.45  +0.18% |L: 455.86  H: 464.36
    MSFT: $210.20  +0.62% |L: 208.91  H: 211.19
    SPY:  $338.10  +0.37% |L: 336.85  H: 338.34

    [during after hours]
    .p estc aapl msft spy
    ESTC:  $91.47  +0.34% |AH: 91.47   +0.00%
    AAPL: $459.63  -0.19% |AH: 455.29  -0.07%
    MSFT: $210.22  +0.63% |AH: 208.82  -0.05%
    SPY:  $338.14  +0.39% |AH: 336.63  -0.07%
#### Find option - Displays stock option information based on ticker, type (call or put), and expiration. Auto generates closest 'monthly' expiration if expiration is not provided. Also, option type is defaulted to call. 
***********
    Ex: .f [stock], [strike]
    Ex: .f [stock], [strike], [type]
    Ex: .f [stock], [strike], [type], [expiration]

    .f aapl 470
    AAPL 08-21 C $2.19 -18.28%
    Vol:27K OI:16K IV:30% BE:472.19

    .f fb 260 p
    FB 08-21 P $2.20 -22.26%
    Vol:8K  OI:4K IV:34% BE:257.80
    
    .f fb 260 c 2020-08-28
    FB 08-28 C $7.45 +14.97%
    Vol:4K  OI:1K IV:35% BE:267.45
    
#### Portfolio status - check the current balance of the signed in user's portfolio. Currently set to ONLY allow the discord account associated with the ROBINHOOD_USER_ACCOUNT use this command. 
***********
    Ex: .port 

    .port 
    Current Balance:  $87239.96   +2,225.16    +2.62%
    Buying power: $13,242.81
    Option positions:

#### Most mentioned stocks - maintains a record of mentioned stocks (currently on a csv, [stocks_mentioned.csv] updated every 10 minutes) and outputs the top 5 most used stock tickers. 
***********
    Ex: .used

    .used
    Most mentioned stocks:
    AAPL = 29 
    SPY = 29 
    SQ = 20 
    ESTC = 14 
    TSLA = 13

### Features:

#### Background Loop - Displays a sorted list of specified stocks by gain every 15m between market hours. Not displayed before or after, as well as not on weekends or holidays. Stocks pulled through background loop are not added to 'most mentioned stocks'.  
***********
    [15M pull] 
    AMZN: $3294.32 +3.52% |L: 3205.82 H: 3296.96
    NFLX: $492.61  +2.13% |L: 482.88  H: 492.79
    GOOGL:$1532.81 +1.09% |L: 1522.00 H: 1536.00
    AAPL: $461.64   +0.7% |L: 456.03  H: 462.00
    SPY:  $338.41  +0.15% |L: 336.61  H: 339.07
    FB:   $260.30  -0.33% |L: 259.26  H: 262.62


### Initial build

- [x] Connect to pyrh
- [x] Create a discord bot
- [x] Have the discord bot output something onto discord.
- [x] Discord bot use pyrh to output something.
- [x] Create a discord command "priceCheck" that triggers on '.p'. Should output the ticker, current price, and percentage difference since market open. 
- [x] Create a discord command "priceCheckList" that triggers on '.pp'. Performs "priceCheck" on a list of tickers. Produces output in a single message. 
- [x] Implement eastern time for hours, minutes, day.
- [x] Create a background loop, when the bot starts up it will print out the SPY price to a channel and the console with a timestamp every 15m during market hours.
- [x] Have background loop account for holiday days (do not post any automatic stock messages on holidays)


### Next steps

- [x] Tweak priceChecker formatting to enhance the aesthetic and allow all information to be posted on a single line. 
- [x] Allow priceChecker to differentiate the current time to output different results depending on if market is open or not. If market is closed, it should outprint the open price, close price, percent difference, after hours price, and percent difference since market close. 
- [x] Implement csv read to 'stocks mentioned' on load up and csv write every 20 minutes while bot is running.
- [x] Add comments and clean up code.
- [ ] Add sudo groups for lists of stock tickers. 
- [ ] Add an additional condition check to priceCheck/priceCheckList to validate if the ticker exists. Currently an alphabetical combination of 1-4 characters is allowed, a stock such as TVIX can cause an exception to pop. 
- [ ] Set up a database that the bot can use to store information such as discord's most used tickers.
- [ ] Fix port command, so stock and option positions that the user has is displayed.  
- [ ] Add the '.f' command which displays friday expiry options (if not provided a date) for the call side (if not provided a side). 
- [ ] Add a command for implied IV and move for options.
- [ ] Add an alert anomaly detection for implied sudden changes to stock ticker price.
- [ ] Add an alert anomaly detection for implied sudden changes to a stock's near expiry options [unusual activity].
- [ ] Begin adding technical analysis to certain stocks (SPY, AAPL, MSFT, AMZN) and shoutout to the channel any extremities. 

