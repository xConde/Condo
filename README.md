Condo 
<img src="https://www.emoji.co.uk/files/twitter-emojis/animals-nature-twitter/10664-monkey.png" width="100" height="100">
========================
#### Condo utilizes an unofficial Robinhood API (robin_stocks), discord API, and various other tools/imports to create a user-friendly environment for market enthusiasts. 


Table of Contents
=================

<!--ts-->
   * [Discord Commands](#discord-commands)
      * [Commands](#commands)
      * [Price Checker](#price-checker)
      * [Options](#options)
          * [Find Specific Option](#find-specific-option)
          * [Check Option Chain](#check-option-chain)
          * [Read Option Side](#read)
      * [Top/Bottom 5 S&P performing stocks](#top/bottom-5-s&p-performing-stocks)
      * [Portfolio status](#portfolio-status)
      * [Most mentioned stocks](#most-mentioned-stocks)
      * [Personal Watchlists](#personal-watchlists)
      * [Trending on Stocktwits](#trend)
      * [Ark Investments](#ark)
   * [Features](#features)
      * [Background Loop](#background-loop)
      * [Checking S&P Anomalies](#anomalies)
<!--te-->

Discord commands
=================

Command prefix = '.'

<a name="commands"></a>
##### Commands - 
Display directory of commands.
***********
    Ex: .commands

    ============== Stocks ==============
    - Price checker: Receive the current price on a stock
    EX: .p (arg1), (arg2), ... (argN)
    
    - Top/Bottom 5 S&P performing stocks
    Ex: .spyup
    Ex: .spydown
    
    - Most mentioned stocks: Maintains a record of mentioned stocks.
    Ex: .used
    
    - Watchlist: Maintains a record of unique watchlists to each user
    Ex: .wl
    Ex: .wl (arg1), (arg2), ... (argN)
    Ex: .wl reset
    Ex. .wl @Discord_user
    
    ============== Options ==============
    - Option: Displays stock option information based on ticker, strike, type (call or put), and expiration.
    Ex: .option [stock], [strike]
    Ex: .option [stock], [strike], [type]
    Ex: .option [stock], [strike], [type], [expiration]
    
     - Option chain: Displays stock option chain information based on ticker, type (call or put), and expiration.
    Ex: .f [stock]
    Ex: .f [stock], [type]
    Ex: .f [stock], [type], [expiration](YYYY-MM-DD)
    
    - Read Option Info: Displays closest valued options for a ticker with which side is dominating and top 5 most valued strikes.
    Ex. .read [stock]

<a name="price-checker"></a>
##### Price checker - 
Receive the current price on a stock quickly. Condensed to allow mobile users to view it on one line. 
***********
    Ex: .p (arg1)
    EX: .p (arg1), (arg2), ... (argN)

    {during market hours}
    .p estc aapl msft spy 
    ESTC:  $92.31  +0.92% |L: 91.40   H: 93.59
    AAPL: $460.45  +0.18% |L: 455.86  H: 464.36
    MSFT: $210.20  +0.62% |L: 208.91  H: 211.19
    SPY:  $338.10  +0.37% |L: 336.85  H: 338.34

    {during after hours}
    .p estc aapl msft spy
    ESTC:  $91.47  +0.34% |AH: 91.47   +0.00%
    AAPL: $459.63  -0.19% |AH: 455.29  -0.07%
    MSFT: $210.22  +0.63% |AH: 208.82  -0.05%
    SPY:  $338.14  +0.39% |AH: 336.63  -0.07%
<a name="find-specific-option"></a>
##### Find specific option - 
Displays stock option information based on ticker, type (call or put), and expiration. Auto generates closest 'monthly' expiration if expiration is not provided. Also, option type is defaulted to call. Defaults an incorrect provided parameter (type, expiration, strike), notifies the user on the specific wrong input (expiration and strike), and displays a format example.
***********
    Ex: .option [stock], [strike]
    Ex: .option [stock], [strike], [type]
    Ex: .option [stock], [strike], [type], [expiration]

    .option aapl 470
    AAPL 08-21 C $2.19 -18.28%
    Vol:27K OI:16K IV:30% BE:472.19

    .option fb 260 p
    FB 08-21 P $2.20 -22.26%
    Vol:8K  OI:4K IV:34% BE:257.80
    
    .option fb 260 c 2020-08-28
    FB 08-28 C $7.45 +14.97%
    Vol:4K  OI:1K IV:35% BE:267.45
    
    .option fb 265 c 2020-08-282
    Defaulted expiration date to 2020-08-21. YYYY-MM-DD
    Ex: .f [stock], [strike]
    Ex: .f [stock], [strike], [type]
    Ex: .f [stock], [strike], [type], [expiration]
    
    FB 08-21 C $2.44 +26.42%
    Vol:34K  OI:8K IV:37% BE:267.44
    
    .option aapl 230
    Strike price 250 did not exist for AAPL.
    Defaulted strike to 495 (1 ITM).
    
    AAPL 09-18 495C $24.80 +147.26%
    Vol:7K  OI:1K IV:42% BE:519.80
<a name="check-option-chain"></a>
##### Check Option Chain - 
Utilizes an optimized way of discovering option strike prices relative to the stock. Prints out 1 ITM (In-The-Money) option and 3 OTM (Out-The-Money). Works with calls and puts. 
***********
    Ex: .f [stock]
    Ex: .f [stock], [type]
    Ex: .f [stock], [type], [expiration] *Expiration = monthlies only for accurate results.

    .f aapl
    Option chain for AAPL:
    [ITM] AAPL 09-18 495C $24.80 +147.26%
    Vol:7K  OI:1K IV:42% BE:519.80
    ------------------------------------
    1 OTM. AAPL 09-18 500C $22.50 +157.73%
    Vol:22K OI:24K IV:43% BE:522.50
    ------------------------------------
    2 OTM. AAPL 09-18 505C $20.38 +169.93%
    Vol:3K  OI:1K IV:43% BE:525.38
    ------------------------------------
    3 OTM. AAPL 09-18 510C $18.53 +181.61%
    Vol:3K  OI:3K IV:43% BE:528.53
    ------------------------------------

    .f fb p
    Option chain for FB:
    [ITM] FB 09-18 270P $11.63  +11.29%
    Vol:2K  OI:2K IV:33% BE:258.37
    ------------------------------------
    1 OTM. FB 09-18 265P $9.10   +12.62%
    Vol:642 OI:14K IV:34% BE:255.90
    ------------------------------------
    2 OTM. FB 09-18 260P $7.00   +13.27%
    Vol:452 OI:14K IV:34% BE:253.00
    ------------------------------------
    3 OTM. FB 09-18 255P $5.35   +13.83%
    Vol:772  OI:3K IV:35% BE:249.65
    ------------------------------------
    
    .f fb p 2020-10-16
    Option chain for FB:
    [ITM] FB 10-16 270P $16.03   +6.87%
    Vol:67 OI:642 IV:34% BE:253.97
    ------------------------------------
    1 OTM. FB 10-16 265P $13.53   +5.29%
    Vol:75 OI:12K IV:35% BE:251.47
    ------------------------------------
    2 OTM. FB 10-16 260P $11.53   +7.46%
    Vol:188  OI:4K IV:35% BE:248.47
    ------------------------------------
    3 OTM. FB 10-16 255P $9.55    +8.15%
    Vol:266  OI:1K IV:36% BE:245.45
    ------------------------------------
<a name="read"></a>
##### Read Option Info - 
Displays closest valued options for a ticker with which side is dominating and top 5 most valued strikes.
***********
    Ex: .read [stock]

    .read spy
    Valued SPY (2020-12-18, 2021-01-15, 2021-02-19) options
    Puts are dominating (109M > 42.4M)
    [75 DTE] 330P = $13.8M
    [13 DTE] 360P = $9.06M
    [75 DTE] 365P = $7.72M
    [75 DTE] 345P = $6.99M
    [75 DTE] 360P = $6.24M
<a name="top/bottom-5-s&p-performing-stocks"></a>
##### Top/Bottom 5 S&P performing stocks - 
Displays out top 5 S&P performers/sinkers for the day. Sorts by market performance, not extended hours.
***********
    Ex: .spyup
    Ex: .spydown

    .spyup
    TGT:  $154.22 +12.65% |AH: $155.24 +0.66%
    FCX:   $14.94  +3.68% |AH: $14.97  +0.2%
    CTL:   $11.29  +3.58% |AH: $11.40 +0.97%
    NCLH:  $15.68  +3.16% |AH: $15.76 +0.51%
    LYV:   $51.56  +2.46% |AH: $51.56  +0.0%

    .spydown
    JKHY: $172.22 -12.87% |AH: $172.88 +0.38%
    TJX:   $54.36  -5.38% |AH: $54.50 +0.26%
    GILD:  $65.70  -4.87% |AH: $65.80 +0.15%
    ROST:  $90.26  -4.28% |AH: $90.26  +0.0%
    REG:   $40.20  -3.87% |AH: $40.20  +0.0%
<a name="portfolio-status"></a>
##### Portfolio status - 
Checks the current balance of the signed in user's portfolio. Currently set to ONLY allow the discord account associated with the ROBINHOOD_USER_ACCOUNT use this command. 
***********
    Ex: .port 

    .port 
    Current Balance:  $87239.96   +2,225.16    +2.62%
    Buying power: $13,242.81
    Option positions:
<a name="most-mentioned-stocks"></a>
##### Most mentioned stocks -
Maintains a record of mentioned stocks (currently on a csv, [stocks_mentioned.csv] updated every 10 minutes) and outputs the top 5 most used stock tickers. 
***********
    Ex: .used

    .used
    Most mentioned stocks:
    FB = 237 
    SPY = 225 
    NFLX = 211 
    TSLA = 145 
    SPCE = 111 
<a name="personal-watchlists"></a>
##### Personal Watchlists -
Maintains a record of unique watchlists to each user per server to be initialized, pulled, and added through a single command. 
***********
    Ex: .wl
    -- No watchlist

    To create a personal watchlist use the command ".wl" followed by stock tickers.
    Example: .wl estc net
    To view other user's watchlists use the command ".wl @user"
    To remove a stock use the command ".wl rm"
    To remove watchlist use the command ".wl refresh"

    Ex: .wl
    -- Watchlist that has been created by the user saved indefinitely. 
    
    Conde's Watchlist
    ---------------------------------
    HOME:  $19.14  +1.54% |AH: $19.19   +0.26%
    ROOT:  $17.23  +1.29% |AH: $17.36   +0.75%
    CAN:   $5.75   -9.73% |AH: $5.81   +1.04%
    SOLO:  $8.27   -3.39% |AH: $8.26   -0.12%
    FLWS:  $24.97  +5.58% |AH: $24.97    +0.0%
    
    
    Ex: .wl home
    -- Watchlist attempting to add a duplicate stock.
    
    Watchlist had no unique stock tickers to add
    
    Conde's Watchlist
    ---------------------------------
    HOME:  $19.14  +1.54% |AH: $19.19   +0.26%
    ROOT:  $17.23  +1.29% |AH: $17.36   +0.75%
    CAN:   $5.75   -9.73% |AH: $5.81   +1.04%
    SOLO:  $8.27   -3.39% |AH: $8.26   -0.12%
    FLWS:  $24.97  +5.58% |AH: $24.97    +0.0%
    
    Ex: .wl reset
    -- Remove user's watchlist
    
    Watchlist instance successfully removed for Conde#9779
    
    Ex. .wl @MAGA
    -- Access other discord user's watchlist instance
    
    Looking for a pullback's Watchlist
    ---------------------------------
    TSLA: $585.76  +2.05% |AH: $584.50   -0.22%
    AAPL: $116.59  +0.48% |AH: $116.46   -0.11%
    FB:   $277.81  +0.81% |AH: $276.70    -0.4%
    ZM:   $471.61  +6.29% |AH: $474.00   +0.51%
    SPY:  $363.67  +0.28% |AH: $363.67    +0.0%
    QQQ:  $299.01  +0.92% |AH: $299.01    +0.0%
    BABA: $276.48  -0.45% |AH: $276.90   +0.15%
    GE:    $10.40  -0.95% |AH: $10.41    +0.1%
    F:     $9.09   +0.11% |AH: $9.10   +0.11%
    
    Ex. .wl @MAGA estc
    -- Blocks any modification to other user's watchlists.
    
    Cannot modify other watchlists
    
    Looking for a pullback's Watchlist
    ---------------------------------
    TSLA: $585.76  +2.05% |AH: $584.50   -0.22%
    AAPL: $116.59  +0.48% |AH: $116.46   -0.11%
    FB:   $277.81  +0.81% |AH: $276.70    -0.4%
    ZM:   $471.61  +6.29% |AH: $474.00   +0.51%
    SPY:  $363.67  +0.28% |AH: $363.67    +0.0%
    QQQ:  $299.01  +0.92% |AH: $299.01    +0.0%
    BABA: $276.48  -0.45% |AH: $276.90   +0.15%
    GE:    $10.40  -0.95% |AH: $10.41    +0.1%
    F:     $9.09   +0.11% |AH: $9.10   +0.11%
<a name="trend"></a>
##### Trend -
Displays a price roster of the top 10 trending stock tickers from Stocktwits. 
*********** 
    Ex: .trend

    Stocktwits Trending Stock Tickers
    ---------------------------------
    RIDE:  $14.78 -16.54% |AH: $15.18   +2.71%
    GBTC:  $50.00  -4.36% |AH: $50.00    +0.0%
    LLY:  $208.08   +1.4% |AH: $211.00    +1.4%
    SYX:   $37.88  -0.16% |AH: $37.88    +0.0%
    KWR:  $247.30  -0.31% |AH: $247.30    +0.0%
    ASO:   $25.70   +2.8% |AH: $25.70    +0.0%
    RACE: $195.81  -0.51% |AH: $195.81    +0.0%
    ADES:  $5.75    +0.0% |AH: $5.75    +0.0%
    ---------------------------------
<a name="ark"></a>
##### Ark -
Displays a scraped excerpt from Ark investments recent buy/sells between multiple ETFs. 
***********   
    Ex: .ark

    ARK Orders
    ---------------------------------
    ticker        date  shares  weight  fund direction
       TER  2021-03-12  139619  0.0640  ARKK       Buy
       BLI  2021-03-12   50512  0.0112  ARKK       Buy
      TDOC  2021-03-12  162624  0.1281  ARKK       Buy
     NTDOY  2021-03-12   97801  0.0908  ARKW      Sell
       DDD  2021-03-12  243893  0.2130  ARKQ       Buy
      AONE  2021-03-12    1223  0.0004  ARKQ       Buy
       CAT  2021-03-12   20705  0.1345  ARKQ      Sell
     KMTUY  2021-03-12   12300  0.0114  ARKQ      Sell
      ESLT  2021-03-12   17055  0.0690  ARKQ       Buy
       TSM  2021-03-12    5700  0.0198  ARKQ      Sell
        DE  2021-03-12    3800  0.0409  ARKQ      Sell
      KSPI  2021-03-12    9199  0.0158  ARKF       Buy
      PSTI  2021-03-12   22034  0.0012  ARKG      Sell
      IONS  2021-03-12   79806  0.0432  ARKG       Buy
       TER  2021-03-11  133982  0.0629  ARKK       Buy
      TDOC  2021-03-11  270500  0.2199  ARKK       Buy
      SKLZ  2021-03-11  632223  0.2163  ARKW       Buy
     NTDOY  2021-03-11  108109  0.1000  ARKW      Sell
     KMTUY  2021-03-11   14000  0.0128  ARKQ      Sell
      AONE  2021-03-11   50607  0.0175  ARKQ       Buy
      ESLT  2021-03-11      98  0.0004  ARKQ       Buy
    ---------------------------------

Features
=================
<a name="background-loop"></a>
##### Background Loop -
Displays a sorted list of specified stocks by gain every 15m between market hours. Not displayed before or after, as well as not on weekends or holidays. Stocks pulled through background loop are not added to 'most mentioned stocks'.  
***********
    -- Market hours
   
    [15M pull] Intraday @ 14:45 EST
    QQQ:  $299.01  +0.92% |L: 297.90  H: 300.17
    VXX:   $17.51  +0.69% |L: 17.10   H: 17.64
    SPY:  $363.67  +0.28% |L: 362.58  H: 364.18
    ----------
    NFLX: $491.36  +1.31% |L: 481.85  H: 493.25
    GOOGL:$1787.02  +1.3% |L: 1764.54 H: 1797.01
    FB:   $277.81  +0.81% |L: 274.82  H: 279.13
    MSFT: $215.23  +0.64% |L: 214.04  H: 216.27
    AAPL: $116.59  +0.48% |L: 116.22  H: 117.48
    AMZN: $3195.34 +0.32% |L: 3190.28 H: 3216.19
    NVDA: $530.45   +0.2% |L: 526.88  H: 536.30
    JPM:  $121.22  -0.66% |L: 121.09  H: 122.34
    
    -- Pre market and after hours pull
    
    [15M pull] After-hours @ 17:15 EST
    SPY:  $326.54  -1.04% |AH: $327.30   +0.23%
    QQQ:  $269.38  -2.54% |AH: $269.55   +0.06%
    VXX:   $26.53  +3.03% |AH: $26.50   -0.11%
    ----------
    GOOGL:$1616.11  +3.8% |AH: $1618.50   +0.15%
    JPM:   $98.04   +0.9% |AH: $98.10   +0.06%
    NFLX: $475.74  -5.65% |AH: $475.99   +0.05%
    AMZN: $3036.15 -5.45% |AH: $3036.00   +-0.0%
    MSFT: $202.47   -1.1% |AH: $202.30   -0.08%
    NVDA: $501.36  -3.76% |AH: $500.02   -0.27%
    AAPL: $108.86   -5.6% |AH: $108.51   -0.32%
    FB:   $263.11  -6.31% |AH: $262.20   -0.35%
<a name="anomalies"></a>
##### Checking S&P Anomalies -
Scans the S&P option chain for any irregular changes over the past 3 minutes and alerts the chat if any are found. Parses through the 3 closest dates [friday, monthly expiration, next monthly expiration] and checks for a static number change (volume * premium) > X over the course of 3 minutes. If something pops it alerts the discord.
*********** 
    Found large cash movement in past 3 min. 
    Current SPY price @ 358.54
    2DTE 358C = +$547K   Price: $239   Vol: 569   Gamma: 7.45
    2DTE 359C = +$649K   Price: $188   Vol: 1959   Gamma: 7.5
    2DTE 360C = +$563K   Price: $144   Vol: 1446   Gamma: 7.36
