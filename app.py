import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore
from dash import Dash,dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input,Output

stocksDF=pd.read_csv('sp500.csv')

from secret import IEX_CLOUD_API_TOKEN


symbol='AAPL'
base_url='https://sandbox.iexapis.com/stable' ##'stable' gets the latest stable api version and 'latest' gets the latest beta api version
url=f"{base_url}/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}"


# chunks function splits the list into certains chunks. Here the list of 500 stock symbols is splitted into 100 each.

def chunks(lst,n):
    for i in range(0,len(lst),n):
        yield lst[i:i+n]

symbols100=list(chunks(stocksDF['Symbol'],100))

stockSymbols=[]
for i in symbols100:
    stockSymbols.append(','.join(i))

app=Dash(__name__)
server=app.server

strategies=[{'label':'S&P 500 Equal Weightage Strategy','value':'sp_500_equal_weightage_strategy'},
           {'label':'Momentum Investing Strategy','value':'momentum_investing_strategy'},
           {'label':'Value Investing Strategy','value':'value_investing_strategy'}]

app.layout=html.Div([html.H1(children='Stock Picking Strategies',
           style={'textalign':'center'}),
    html.Br(),
    dcc.Dropdown(id='dropdown',options=strategies,placeholder='Select a Strategy',value='sp_500_equal_weightage_strategy'),
    html.Br(),
    dcc.Input(id="input1", type="number", placeholder="Enter the amount you are willing to invest. Eg : 10000,1000,500000. (Currently the amount is 100000)", 
              style={'marginRight':'10px','width':'100%'},debounce=True),
    html.Br(),
    html.Div([html.H3(children='Based on the investment amount and the strategy the  no of stocks to buy is calculated')]),
    html.Br(),
    html.H3(children='Top 50 stocks based on the selected strategy',
           style={'textalign':'center'}),
    html.Div(id="table1")
                    ])

@app.callback(Output('table1','children'),
              [Input('dropdown','value'),
              Input('input1','value')])

def update_graph(strategy,totalAmount):
    
    columns=['symbol','price','market_cap']
    stocksInfoDF=pd.DataFrame(columns=columns)
    for symbols in stockSymbols:
        batch_api_url=f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbols}&token={IEX_CLOUD_API_TOKEN}'
        stockInfo=requests.get(batch_api_url).json()
        for ticker in symbols.split(','):
            price=stockInfo[ticker]['quote']['latestPrice']
            marketCap=stockInfo[ticker]['quote']['marketCap']
            stocksInfoDF=stocksInfoDF.append({'symbol':ticker,'price':price,'market_cap':marketCap},ignore_index=True)
            
    if not totalAmount:
        totalAmount=100000
    
    amountPerStock=totalAmount/len(stocksInfoDF)

    noOfStocks=[]
    for price in stocksInfoDF['price']:
        noOfStocks.append(math.floor(amountPerStock/price))
    stocksInfoDF['no_of_stocks_to_buy']=noOfStocks
        
    if not strategy:
        return dash_table.DataTable(
                                   data=stocksInfoDF.to_dict('records'),
                                   columns=[{'name':i,'id':i} for i in stocksInfoDF.columns],
                                   page_current=0,page_size=10,
            style_data_conditional=[
        {
            'if': {
                'column_id': 'no_of_stocks_to_buy',
            },
            'backgroundColor': 'dodgerblue',
            'color': 'white'
        }]
        )
    
    if strategy=='sp_500_equal_weightage_strategy':
        return dash_table.DataTable(
                                   data=stocksInfoDF.to_dict('records'),
                                   columns=[{'name':i,'id':i} for i in stocksInfoDF.columns],
                                    page_current=0,page_size=10,
        style_data_conditional=[
        {
            'if': {
                'column_id': 'no_of_stocks_to_buy',
            },
            'backgroundColor': 'dodgerblue',
            'color': 'white'
        }]
        )
    
    
    elif strategy=='momentum_investing_strategy':
        
        columns=['symbol','price',
         'one_year_return','one_year_return_percentile',
         'six_months_return','six_months_return_percentile',
         'three_months_return','three_months_return_percentile',
         'one_month_return','one_month_return_percentile',
        'no_of_stocks_to_buy']

        hqmStocksDF=pd.DataFrame(columns=columns)
        for symbols in stockSymbols:
            batch_api_url=f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbols}&token={IEX_CLOUD_API_TOKEN}'
            stockInfo=requests.get(batch_api_url).json()
            for ticker in symbols.split(','):
                price=stockInfo[ticker]['quote']['latestPrice']
                one_year_return=stockInfo[ticker]['stats']['year1ChangePercent']
                six_months_return=stockInfo[ticker]['stats']['month6ChangePercent']
                three_months_return=stockInfo[ticker]['stats']['month3ChangePercent']
                one_month_return=stockInfo[ticker]['stats']['month1ChangePercent']
                hqmStocksDF=hqmStocksDF.append({'symbol':ticker,
                                        'price':price,
                                        'one_year_return':one_year_return,'one_year_return_percentile':'N/A',
                                        'six_months_return':six_months_return,'six_months_return_percentile':'N/A',
                                       'three_months_return':three_months_return,'three_months_return_percentile':'N/A',
                                        'one_month_return':one_month_return,'one_month_return_percentile':'N/A',
                                       'no_of_stocks_to_buy':'N/A'},ignore_index=True)
        for col in ['one_year_return','six_months_return','three_months_return','one_month_return']:
            for row in range(len(hqmStocksDF)):
                score=hqmStocksDF[col][row]
                percentileScore=percentileofscore(hqmStocksDF[col],score)
                hqmStocksDF.loc[row,f'{col}_percentile']=percentileScore
        
        hqm_scores=[]
        for row in range(len(hqmStocksDF)):
            hqm_score=0
            for col in ['one_year_return_percentile','six_months_return_percentile','three_months_return_percentile','one_month_return_percentile']:
                hqm_score+=hqmStocksDF[col][row]
            mean_hqm_score=hqm_score/4
            hqm_scores.append(mean_hqm_score)
    
        hqmStocksDF['hqm_score']=hqm_scores
        
        hqmStocksDF.sort_values(by='hqm_score',ascending=False,inplace=True)
        hqmStocksDF.reset_index(inplace=True)
        hqmStocksDF.drop('index',axis=1,inplace=True)
        hqmStocksDF=hqmStocksDF[:50]
        
        amountPerStock=totalAmount/len(hqmStocksDF)
        
        for row in range(len(hqmStocksDF)):
            priceOfStock=hqmStocksDF['price'][row]
            hqmStocksDF.loc[row,'no_of_stocks_to_buy']=math.floor(amountPerStock/priceOfStock)
        
        return dash_table.DataTable(
                                   data=hqmStocksDF[['symbol','price','hqm_score','no_of_stocks_to_buy']].to_dict('records'),
                                   columns=[{'name':i,'id':i} for i in hqmStocksDF[['symbol','price','hqm_score','no_of_stocks_to_buy']].columns],
                                   page_current=0,page_size=10,
        style_data_conditional=[
        {
            'if': {
                'column_id': 'no_of_stocks_to_buy',
            },
            'backgroundColor': 'dodgerblue',
            'color': 'white'
        }]
        )
    elif strategy=='value_investing_strategy':
        columns=['symbol','price','pe_ratio','pb_ratio','ps_ratio','ev','ebitda','ev_to_ebitda','ev_to_grossProfit']
        valueAdvancedStocksDF=pd.DataFrame(columns=columns)
        for symbols in stockSymbols:
            batch_api_url=f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=advanced-stats,quote&symbols={symbols}&token={IEX_CLOUD_API_TOKEN}'
            stockInfo=requests.get(batch_api_url).json()
            for ticker in symbols.split(','):
                price=stockInfo[ticker]['quote']['latestPrice']
                peRatio=stockInfo[ticker]['quote']['peRatio']
                pbRatio=stockInfo[ticker]['advanced-stats']['priceToBook']
                psRatio=stockInfo[ticker]['advanced-stats']['priceToSales']
                ev=stockInfo[ticker]['advanced-stats']['enterpriseValue']
                ebitda=stockInfo[ticker]['advanced-stats']['EBITDA']
                grossProfit=stockInfo[ticker]['advanced-stats']['grossProfit']
                try:
                    ev_to_ebitda=round((ev/ebitda),2)
                except TypeError:
                    ev_to_ebitda=np.NaN
                try:
                    ev_to_grossProfit=round((ev/grossProfit),2)
                except:
                    ev_to_grossProfit=np.NaN
                valueAdvancedStocksDF=valueAdvancedStocksDF.append({'symbol':ticker,
                                                            'price':price,
                                                            'pe_ratio':peRatio,
                                                            'pb_ratio':pbRatio,
                                                            'ps_ratio':psRatio,
                                                            'ev':ev,
                                                             'ebitda':ebitda,
                                                             'ev_to_ebitda':ev_to_ebitda,
                                                              'ev_to_grossProfit':ev_to_grossProfit},ignore_index=True)
        valueAdvancedStocksDF['pe_ratio']=valueAdvancedStocksDF['pe_ratio'].astype('float64')
        valueAdvancedStocksDF['pb_ratio']=valueAdvancedStocksDF['pb_ratio'].astype('float64')
        valueAdvancedStocksDF['ps_ratio']=valueAdvancedStocksDF['ps_ratio'].astype('float64')
        valueAdvancedStocksDF['ev']=valueAdvancedStocksDF['ev'].astype('float64')
        valueAdvancedStocksDF['ebitda']=valueAdvancedStocksDF['ebitda'].astype('float64')
        for col in valueAdvancedStocksDF.select_dtypes('float').columns:
            valueAdvancedStocksDF[col].fillna(valueAdvancedStocksDF[col].mean(),inplace=True)
        for col in ['pe_ratio','pb_ratio','ps_ratio','ev_to_ebitda','ev_to_grossProfit']:
            for row in range(len(valueAdvancedStocksDF)):
                score=valueAdvancedStocksDF[col][row]
                percentileScore=percentileofscore(valueAdvancedStocksDF[col],score)
                valueAdvancedStocksDF.loc[row,f'{col}_percentile']=percentileScore
        percentileColumns=valueAdvancedStocksDF.columns[valueAdvancedStocksDF.columns.str.contains('percentile')]
        for row in range(len(valueAdvancedStocksDF)):
            meanOfMetrics=np.mean(valueAdvancedStocksDF.loc[row][percentileColumns])
            valueAdvancedStocksDF.loc[row,'valueMetric']=meanOfMetrics
        valueAdvancedStocksDF.sort_values(by='valueMetric',ascending=False,inplace=True)
        valueAdvancedStocksDF.reset_index(drop=True,inplace=True)
        valueAdvancedStocksDF=valueAdvancedStocksDF[:50]
        amountPerStock=totalAmount/len(valueAdvancedStocksDF)

        for row in range(len(valueAdvancedStocksDF)):
            valueAdvancedStocksDF.loc[row,'no_of_stocks_to_buy']=int(amountPerStock/valueAdvancedStocksDF.loc[row,'price'])
            
        return dash_table.DataTable(
                                   data=valueAdvancedStocksDF[['symbol','price','valueMetric','no_of_stocks_to_buy']].to_dict('records'),
                                   columns=[{'name':i,'id':i} for i in valueAdvancedStocksDF[['symbol','price','valueMetric','no_of_stocks_to_buy']].columns],
                                   page_current=0,page_size=10,
        style_data_conditional=[
        {
            'if': {
                'column_id': 'no_of_stocks_to_buy',
            },
            'backgroundColor': 'dodgerblue',
            'color': 'white'
        }]
        )

if __name__ == '__main__':
    app.run_server()






