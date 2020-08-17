# Discord Robinhood Stockbot
### Discord stock bot that utilizes an unofficial Robinhood API (pyrh) and discord API for market enthusiasts. 

### Discord commands:

Command prefix = '.'

#### Price checker - provide ticker names to receive the current price quickly.
***********
    Ex: .p (arg1)
    EX: .p (arg1), (arg2), ... (argN)

    [during market hours]
    .p estc aapl msft spy 
    ESTC: $91.47     +2.02%
    AAPL: $459.63    -0.09%
    MSFT: $208.9     +0.1%
    SPY: $336.84     +0.01%

    [during after hours]
    .p estc aapl msft spy
    ESTC:    $91.47   +2.02%    |    AH: $91.47    +0.0%
    AAPL:   $459.63   -0.09%    |    AH: $459.29    -0.07%
    MSFT:    $208.9   +0.1%     |    AH: $208.8    -0.05%
    SPY:    $336.84   +0.0%     |    AH: $336.6    -0.07%

#### Portfolio status - check the current balance of the signed in user's portfolio. Currently set to ONLY allow the discord account associated with the ROBINHOOD_USER_ACCOUNT use this command. 
***********
    Ex: .port 

    .port 
    Current port: $87,239.96

### Features:

#### Background Loop - Displays SPY ticker price every 15m between market hours. Not displayed before or after, as well as not on weekends or holidays. 


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

- [x] Allow priceChecker to differentiate the current time to output different results depending on if market is open or not. If market is closed, it should outprint the open price, close price, percent difference, after hours price, and percent difference since market close. 
- [ ] Add an additional condition check to priceCheck/priceCheckList to validate if the ticker exists. Currently an alphabetical combination of 1-4 characters is allowed, a stock such as TVIX can cause an exception to pop. 
- [ ] Begin adding technical analysis to certain stocks (SPY, AAPL, MSFT, AMZN) and shoutout to the channel any extremities. 
