# Discord Robinhood Stockbot
### Discord stock bot that utilizes an unofficial Robinhood API (pyrh) and discord API for market enthusiasts. 

### Discord commands

Command prefix = '.'

#### Price checker - provide ticker names to receive the current price quickly.
***********
    Ex: .p (arg1)
    EX: .p (arg1), (arg2), ... (argN)

    .p estc aapl msft spy 
    ESTC: $91.47     +2.02%
    AAPL: $459.63    -0.09%
    MSFT: $208.9     +0.1%
    SPY: $336.84     +0.01%

#### Portfolio status - check the current balance of the signed in user's portfolio. **TODO: Allow only-owner privillages. 
***********
    Ex: .port 

    .port 
    Current port: $87,239.96

### Inital build

- [x] Connect to pyrh
- [x] Create a discord bot
- [x] Have the discord bot output something onto discord.
- [x] Discord bot use pyrh to output something.
- [x] Create a discord command "priceCheck" that triggers on '.p'. Should output the ticker, current price, and percentage difference since market open. 
- [x] Create a discord command "priceCheckList" that triggers on '.pp'. Performs "priceCheck" on a list of tickers. Produces output in a single message. 
- [x] Implement eastern time for hours, minutes, day.
- [ ] Create a background loop, once the bot starts to outprint SPY price to a channel and the console with a timestamp every 15m during market hours.
- [x] have background loop account for holiday days (do not post any automatic stock messages on holidays)


### Next steps

- [ ] Allow priceChecker to diffrentiate the current time to output different results depending on if market is open or not. If market is closed, it should outprint the open price, close price, percent difference, after hours price, and percent difference since market close. 
- [ ] Add an additional condition check to priceCheck/priceCheckList to validate if the ticker exists. Currently an alphabetical combination of 1-4 characters is allowed, a stock such as TVIX can cause an exception to pop. 

