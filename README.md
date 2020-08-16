# Discord Stockbot
### Discord stock bot that utilizes an unofficial Robinhood API (pyrh) and discord API for market enthusiasts. 

### Inital build

- [x] Connect to pyrh
- [x] Create a discord bot
- [x] Have the discord bot output something onto discord.
- [x] Discord bot use pyrh to output something.
- [x] Create a discord command "priceCheck" that triggers on '.p'. Should output the ticker, current price, and percentage difference since market open. 
- [ ] Create a time based event that prints out the "priceChecker" of SPY every 15m during market hours.
- [ ] Create a discord command "priceCheckList" that performs "priceCheck" on a list of tickers. 

### Next steps

- [ ] Allow priceChecker to diffrentiate the current time to output different results depending on if market is open or not. If market is closed, it should outprint the open price, close price, percent difference, after hours price, and percent difference since market close. 
- [ ] Create a time based event that prints out the "priceChecker" of SPY every 15m during market hours.
