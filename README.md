# Algorthmic-Trading---Stock-Buying-Strategies

The app is currently hosted in heroku and could be accessed here : https://stock-buying-strategies.herokuapp.com/

<b>Quantitative analysis</b> and <b>algorthic trading</b> have been growing exponentially for the past few years. Its growth could be attributed to the growing awareness about investments among the public, improvement in technology and resources, easy trade data maintenance and scalability. Algorthmic trading market size is projected to reach <b>31.48 billion dollars by 2028.</b> 

There are various ways to pick stocks  like trend based strategies, mathematical model based strategies. This project is a basic demonstration of how stocks are picked during alogrthmic trading. The strategies used here are:

1) S&P 500 
2) Momentum Investing strategy
3) Value Investing strategy

<b>S&P 500</b>

This is a very simple strategy. There is a index named S&P 500 which tracks the performance of 500 large companies listed on the stock exchange. Based on the investment amount you are willing to invest the strategy splits the amount equally on all stocks and gives the no of shares to buy in each stock listed.

<b>Momentum Investing Strategy</b>

This strategy is a trend based strategy that capitalizes on the stocks currently witnessing higher demand.  A metric is calculated that combines 1,3,6,month and 1 year returns of the stock and the top 50 stocks based on this metric is selected. The amount you are willing to invest is equally split among these 50 stocks.

<b>Value Investing Strategy</b>

This strategy used the fundamentals of a company to buy stocks. A metric is calculated combining the value based analysis metrics such as PE ratio, PB ratio, EBITDA etc and the top 50 stocks based on this metric is selected. The amount you are willing to invest is equally split among these 50 stocks.

Stock related information is collected form <b>AlphaVantage api</b> and <b>IEX cloud API</b>. The stocks analysed are <b>US based stocks</b>.
