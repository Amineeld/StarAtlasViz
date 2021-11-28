import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
import pandas as pd
from pycoingecko import CoinGeckoAPI
import numpy as np
from datetime import datetime


from werkzeug.middleware.dispatcher import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple

server = flask.Flask(__name__)
app = dash.Dash(__name__, server = server, url_base_pathname='/dashboard/')

@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/dashboard/')
def render_dashboard():
    return flask.redirect('/dash1')


##There are twelve columns in one row dash template


## Import Data, build functions to process data
cg = CoinGeckoAPI()
coin_list = cg.get_coins_list()
df = pd.DataFrame(data=coin_list)


def getPricesOverPeriod(token, period, currency):
    df_prices = pd.DataFrame(np.array(cg.get_coin_market_chart_by_id(token,currency, period)['prices']), columns=['date', 'price'])
    df_prices['date']=pd.to_datetime(df_prices['date'],unit='ms')
    return df_prices
def getMarketCapOverPeriod(token, period, currency):
    df_prices = pd.DataFrame(np.array(cg.get_coin_market_chart_by_id(token,currency, period)['market_caps']), columns=['date', 'price'])
    df_prices['date']=pd.to_datetime(df_prices['date'],unit='ms')
    return df_prices

def getTotalVolumesOverPeriod(token, period, currency):
    df_prices = pd.DataFrame(np.array(cg.get_coin_market_chart_by_id(token,currency, period)['total_volumes']), columns=['date', 'price'])
    df_prices['date']=pd.to_datetime(df_prices['date'],unit='ms')
    return df_prices
def crosscorr(datax, datay, lag=0, wrap=False):
    """ Lag-N cross correlation. 
    Shifted data filled with NaNs 
    
    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    if wrap:
        shiftedy = datay.shift(lag)
        shiftedy.iloc[:lag] = datay.iloc[-lag:].values
        return datax.corr(shiftedy)
    else: 
        return datax.corr(datay.shift(lag))



# font_awesome = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
# meta_tags = [{"name": "viewport", "content": "width=device-width"}]
# external_stylesheets = [meta_tags, font_awesome]


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('STlogo.jpg'),
                     id = 'logo',
                     style = {'height':'150px',
                              'width':'auto',
                              'margin-bottom':'25px'})
            ],className = 'one-third column'),
        
            html.Div([
                
                    html.H3('Star Atlas tokens Dashboard', style={'margin-bottom':'0px', 'color':'white'}),
                    html.H5('Monitor asset\'s valuation', style={'margin-bottom':'0px', 'color':'white'})
                      
            ], className='one-half column', id='title'),
            
            html.Div([
                dcc.Interval(id = 'update_date_time',
                    disabled=False,
                     interval = 60000,
                     n_intervals = 0,
                     max_intervals=-1
                     ),
                html.H6(id = 'last_update',style={'color':'white'})
                
            ],className = 'one-third column', id='title1'),
            
            
        
    ], id = 'header', className='row flex-display', style={'margin-bottom':'25px'}),
    
    dcc.Interval(id = 'update_cards',
            disabled=False,
                interval = 30000,
                n_intervals = 0,
                max_intervals=-1
                ),
                       
    html.Div([
        
    ],id = 'assets_cards',className='row flex-display'),
    
    
    html.Div([
            
            html.Div([
                dcc.Graph(id = 'pie_chart_marketShare', config={'displayModeBar': 'hover'}
                    )
            ], className='card_container three columns'),
            html.Div([
                dcc.Graph(id = 'pie_chart_volumeShare', config={'displayModeBar': 'hover'}
                    )
            ], className='card_container three columns'),
            html.Div([
                dcc.Graph(id = 'line_chart3', config={'displayModeBar': 'hover'})
        ], className='card_container six columns')
            
    ], className='row flex-display'),       
    html.Div([
        html.Div([
                html.P('Select Token:', className='fix_label', style={'color': 'white'}),
                dcc.Dropdown(id = 'token',multi = False,searchable= True,value='Atlas',placeholder= 'Select token',
                         options= [{'label': c, 'value': c}
                                   for c in ['Atlas', 'Polis']], className='dcc_compon')
            ])
    ], className='row flex-display') ,
    html.Div([
        html.Div([
            dcc.Graph(id = 'line_chart', config={'displayModeBar': 'hover'})
        ], className='create_container twelve columns')
    ], className='row flex-display'), 
    html.Div([
        html.Div([
            dcc.Graph(id = 'line_chart2', config={'displayModeBar': 'hover'})
        ], className='create_container twelve columns')
    ], className='row flex-display'), 
    html.Div([
        html.Div([
            dcc.Graph(id = 'bar_chart4', config={'displayModeBar': 'hover'})
        ], className='create_container 6 columns')
    ], className='row flex-display'), 
    html.Div([
        html.Div([
            html.P('Studying correlation and synchronicity between Atlas and Polis tokens.'+
                   'The Idea is to find out which token is leading the other one.' +
                   'However even when finding the leader, this is true only the selected period, at least for now .... to continue', className='fix_label', style={'color': 'white'})
        ], className='create_container ten columns'),
        html.Div([
            html.P('Time window (lag)', className='fix_label', style={'color': 'white'}),
            dcc.Input(id = 'input_window',type='number',value=1,min=1,max=1000)
        ], className='create_container two columns')
    ], className='row flex-display'), 
    html.Div([
        html.Div([
            dcc.Graph(id = 'correlation_chart', config={'displayModeBar': 'hover'})
        ], className='create_container 6 columns')
    ], className='row flex-display'),
    html.Div([
        html.Div([
            dcc.Graph(id = 'correlation_chart2', config={'displayModeBar': 'hover'})
        ], className='create_container 6 columns')
    ], className='row flex-display'),
              
              
                       
], id = 'mainContainer', style={'display':'flex', 'flex-direction':'column'})


@app.callback(Output('pie_chart_marketShare', 'figure'),[Input('update_cards', 'n_intervals')])
def update_graph(n_intervals):
    
    data_atlas= cg.get_price('star-atlas', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   
    data_polis= cg.get_price('star-atlas-dao', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   

    market_cap_atlas = data_atlas['star-atlas']['usd_market_cap']        
    market_cap_polis = data_polis['star-atlas-dao']['usd_market_cap']

    return {
        'data': [go.Pie(
            labels=['Polis', 'Atlas'],
            values=[market_cap_polis,market_cap_atlas],
            marker=dict(colors=['black','gold']),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': 'Market Cap share: ',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': '#00FFFF',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7}

        )
    }
    
@app.callback(Output('pie_chart_volumeShare', 'figure'),[Input('update_cards', 'n_intervals')])
def update_graph(n_intervals):
    print(n_intervals, 'camembert')
    data_atlas= cg.get_price('star-atlas', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   
    data_polis= cg.get_price('star-atlas-dao', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   

    volume_24h_atlas = data_atlas['star-atlas']['usd_24h_vol']
    volume_24h_polis = data_polis['star-atlas-dao']['usd_24h_vol']
        
    return {
        'data': [go.Pie(
            labels=['Polis', 'Atlas'],
            values=[volume_24h_polis,volume_24h_atlas],
            marker=dict(colors=['black','gold']),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': 'Volume share over 24h: ',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': '#00FFFF',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7}

        )
    }

@app.callback(Output('line_chart', 'figure'),
              [Input('token','value')])
def update_graph(token):
    if token == 'Atlas': token ='star-atlas' 
    else : token = 'star-atlas-dao'
    data_price = getPricesOverPeriod(token, 60, 'usd')
    data_volume = getTotalVolumesOverPeriod(token,60, 'usd')


    return {
        'data': [go.Bar(
            x=data_volume['date'],
            y=data_volume['price'],
            yaxis='y1',
            name='Trade volume',
            marker=dict(color='orange'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data_volume['date'].astype(str) + '<br>' +
            '<b>Trade volume</b>: ' + [f'{x:,.2e}' for x in data_volume['price']] + '<br>'
            ),
            go.Scatter(
                x=data_price['date'],
                y=data_price['price'],
                yaxis='y2',
                mode='lines',
                name='Token price',
                line=dict(width=2, color='#00FFFF'),
                hoverinfo='text',
                hovertext=
                '<b>Date</b>: ' + data_price['date'].astype(str) + '<br>' +
                '<b>token Price</b>: ' + [f'{x:,.3f}' for x in data_price['price']] + '<br>'
            )],

        'layout': go.Layout(
            title={'text': 'Price evolution of ' + (token),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Trade Volume</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
            ),
            yaxis2=dict(title='<b>Token price</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       ),
                       side='right',
                       overlaying='y'
                       )
        )
    }
    
@app.callback(Output('line_chart2', 'figure'),
              [Input('token','value')])
def update_graph(token):

    data_atlas = getPricesOverPeriod('star-atlas', 60, 'usd')
    data_polis = getPricesOverPeriod('star-atlas-dao', 60, 'usd')



    return {
        'data': [go.Scatter(
            x=data_atlas['date'],
            y=data_atlas['price'],
            yaxis='y2',
            name='Atlas price',
            line=dict(width=2, color='gold'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data_atlas['date'].astype(str) + '<br>' +
            '<b>Atlas Price</b>: ' + [f'{x:,.3f}' for x in data_atlas['price']] + '<br>'
            ),
            go.Scatter(
                x=data_polis['date'],
                y=data_polis['price'],
                yaxis='y1',
                mode='lines',
                name='Polis price',
                line=dict(width=2, color='black'),
                hoverinfo='text',
                hovertext=
                '<b>Date</b>: ' + data_polis['date'].astype(str) + '<br>' +
                '<b>Polis Price</b>: ' + [f'{x:,.2f}' for x in data_polis['price']] + '<br>'
            )],

        'layout': go.Layout(
            title={'text': 'Price evolution of Star Atlas tokens' ,
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Polis price</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       ),
            yaxis2=dict(title='<b>Atlas Price</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       ),
                       side='right',
                       overlaying='y'
                       )
        )
    }

@app.callback(Output('line_chart3', 'figure'),
              [Input('token','value')])
def update_graph(token):
    
    if token == 'Atlas': token ='x_share' 
    else : token = 'y_share'
    atlas = getMarketCapOverPeriod('star-atlas', 60, 'usd').groupby(getMarketCapOverPeriod('star-atlas', 60, 'usd')['date'].dt.date)['price'].mean().reset_index()
    polis = getMarketCapOverPeriod('star-atlas-dao', 60, 'usd').groupby(getMarketCapOverPeriod('star-atlas-dao', 60, 'usd')['date'].dt.date)['price'].mean().reset_index()

    data = atlas.merge(polis, how='left', on = 'date')
    data['total'] = data.loc[:,['price_x','price_y']].sum(axis=1)
    data['x_share'] = round(data['price_x'].div(data['total'])*100,2)
    data['y_share'] = round(data['price_y'].div(data['total'])*100,2)


    return {
        'data': [
            go.Bar(
            x=data['date'],
            y=data['price_x'],
            yaxis='y1',
            name='Market Cap: Atlas share',
            marker=dict(color='gold'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data['date'].astype(str) + '<br>' +
            '<b>Atlas share</b>: ' + [f'{x:,.3f}' for x in data['x_share']] + '<br>'
            ),
                go.Bar(
            x=data['date'],
            y=data['price_y'],
            yaxis='y1',
            name='Market Cap: Polis share',
            marker=dict(color='black'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data['date'].astype(str) + '<br>' +
            '<b>Atlas share</b>: ' + [f'{x:,.3f}' for x in data['y_share']] + '<br>'
            ),
                go.Scatter(
            x=data['date'],
            y=data[token],
            yaxis='y2',
            mode='lines',
            name='Token MarketCap percentage',
            line=dict(width=3, color='red'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data['date'].astype(str) + '<br>' +
            '<b>Token Market Cap percentage</b>: ' + [f'{x:,.3f}' for x in data[token]] + '<br>'
            )],
            

        'layout': go.Layout(
           
            title={'text': 'Market Cap. Share ',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Market Cap</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       ),
            barmode = 'stack',
            yaxis2=dict(title='<b>Token Market Cap %</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       ),
                       side='right',
                        overlaying='y'
                       )
        )
    }

@app.callback(Output('bar_chart4', 'figure'),
              [Input('token','value')])
def update_graph(token):
    
    if token == 'Atlas': 
        token ='price_atlas' 
        color = 'gold'
        token_name = 'Atlas' 
    else : 
        token = 'price_polis'
        color= 'black'
        token_name = 'Polis'

    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    data_atlas=getPricesOverPeriod('star-atlas', 60, 'usd')
    data_atlas['day_name']=data_atlas['date'].dt.day_name()
    data_atlas=data_atlas.groupby(data_atlas['day_name'])['price'].mean().reindex(days)
    
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    data_polis=getPricesOverPeriod('star-atlas-dao', 60, 'usd')
    data_polis['day_name']=data_polis['date'].dt.day_name()
    data_polis=data_polis.groupby(data_polis['day_name'])['price'].mean().reindex(days)
    
    data_atlas=data_atlas.rename('price_atlas')
    data_polis=data_polis.rename('price_polis')
    
    data = pd.concat([data_atlas,data_polis], axis=1)
    
    return {
        'data': [
            go.Bar(
            x=data.index,
            y=data[token],
            yaxis='y1',
            name='Average price by week day',
            marker=dict(color=color),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + data.index + '<br>' +
            '<b>Atlas share</b>: ' + [f'{x:,.3f}' for x in data[token]] + '<br>'
            )],
            

        'layout': go.Layout(
           
            title={'text': 'Average '+(token_name)+' price by weekday',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Week Day</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Average price by weekday</b>',
                       color='white',
                       showline=True,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       range = [min(data[token])-min(data[token])/50, max(data[token])],
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       ),
            
        )
    }

@app.callback(Output('correlation_chart', 'figure'),
              [Input('input_window','value')])
def update_graph(input_window):

    atlas = getPricesOverPeriod('star-atlas', 60, 'usd').groupby(getPricesOverPeriod('star-atlas', 60, 'usd')['date'])['price'].mean().reset_index()
    polis = getPricesOverPeriod('star-atlas-dao', 60, 'usd').groupby(getPricesOverPeriod('star-atlas-dao', 60, 'usd')['date'])['price'].mean().reset_index()
    atlas = atlas.resample('H', on='date').mean()
    polis = polis.resample('H', on='date').mean()
    atlas.rename(columns={'price': 'price_atlas'}, inplace=True)
    polis.rename(columns={'price': 'price_polis'}, inplace=True)

    data_hour= pd.concat([atlas, polis], axis = 1)
    
    # Set window size to compute moving window synchrony.
    r_window_size = input_window
    # Compute rolling window synchrony
    rolling_r = data_hour['price_atlas'].rolling(window=r_window_size, center=True).corr(data_hour['price_polis']).fillna(0)

    return {
        'data': [go.Scatter(
            x=data_hour.index,
            y=rolling_r,
            yaxis='y2',
            name='Tokens pearson correalation',
            line=dict(width=1, color='gold'),
            hoverinfo='text',
            hovertext=
            '<b>Window</b>: ' + data_hour.index.astype(str) + '<br>' +
            '<b>Tokens\' correlation</b>: ' + [f'{x:,.3f}' for x in rolling_r] + '<br>'
            ),
            ],

        'layout': go.Layout(
            title={'text': 'Star Atlas Pearson Rollling Correalation' ,
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Polis price</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )
        )
    }        

@app.callback(Output('correlation_chart2', 'figure'),
              [Input('input_window','value')])
def update_graph(input_window):

    atlas = getPricesOverPeriod('star-atlas', 60, 'usd').groupby(getPricesOverPeriod('star-atlas', 60, 'usd')['date'])['price'].mean().reset_index()
    polis = getPricesOverPeriod('star-atlas-dao', 60, 'usd').groupby(getPricesOverPeriod('star-atlas-dao', 60, 'usd')['date'])['price'].mean().reset_index()
    atlas = atlas.resample('H', on='date').mean()
    polis = polis.resample('H', on='date').mean()
    atlas.rename(columns={'price': 'price_atlas'}, inplace=True)
    polis.rename(columns={'price': 'price_polis'}, inplace=True)

    data_hour= pd.concat([atlas, polis], axis = 1)
    
    d1 = data_hour['price_atlas']
    d2 = data_hour['price_polis']
    lags =range(-int(input_window),int(input_window)+1)
    rs = [crosscorr(d1,d2, lag) for lag in lags]
    data = pd.DataFrame(data={'lags':lags,'r':rs})
    

    return {
        'data': [go.Scatter(
            x=data['lags'],
            y=data['r'],
            yaxis='y',
            name='Tokens pearson correalation',
            line=dict(width=1, color='gold'),
            hoverinfo='text',
            hovertext=
            '<b>Window</b>: ' + data['lags'].index.astype(str)+ '<br>' +
            '<b>Tokens\' correlation</b>: ' +  [f'{x:,.5f}' for x in data['r']]+ '<br>'
            ),
            ],

        'layout': go.Layout(
            title={'text': 'Star Atlas Pearson Rollling Correlation' ,
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#571364',
            plot_bgcolor='#571364',
            # legend={'orientation': 'h',
            #         'bgcolor': '#571364',
            #         'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Atlas leading <----- | -----> Polis leading </b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Pearson correlation coef.</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )
        )
    }        


@app.callback(Output('last_update', 'children'),
              [Input('update_date_time', 'n_intervals')])
def update_graph(n_intervals):
    print(n_intervals, 'update datetime')    
    data_atlas= cg.get_price('star-atlas', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   
    now = data_atlas['star-atlas']['last_updated_at']
    dt_string = str(datetime.fromtimestamp(now).strftime('%d %B, %Y at %H:%M'))

    return ('Last Update on : '+dt_string)

@app.callback(Output('assets_cards', 'children'),
              [Input('update_cards', 'n_intervals')])
def update_graph(n_intervals):
    print("updating cards 1")
    #if n_intervals == 0:
     #   raise PreventUpdate
    #else:
    print(n_intervals)
    data_atlas= cg.get_price('star-atlas', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   
    data_polis= cg.get_price('star-atlas-dao', 'usd',include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)   


    price_atlas = data_atlas['star-atlas']['usd']
    market_cap_atlas = data_atlas['star-atlas']['usd_market_cap']
    volume_24h_atlas = data_atlas['star-atlas']['usd_24h_vol']

    
    
    price_polis = data_polis['star-atlas-dao']['usd']
    market_cap_polis = data_polis['star-atlas-dao']['usd_market_cap']
    volume_24h_polis = data_polis['star-atlas-dao']['usd_24h_vol']
    
    total_volume_24h = volume_24h_atlas +  volume_24h_polis     
    total_martCap = market_cap_polis + market_cap_atlas
    
    color = '#00FFFF'

    return [
        html.Div([
            html.H6(children='Atlas Price', style={'text-align':'center', 'color':color}),
            html.P(f"{price_atlas:,.3f}" + " $",style={'textAlign': 'center','color': 'gold','fontSize': 40}),
            html.P('All Time High/Low: ' + f"{getPricesOverPeriod('star-atlas', 30, 'usd')['price'].max():,.3f}"
                   + ' / ' + f"{getPricesOverPeriod('star-atlas', 30, 'usd')['price'].min():,.3f}",
                   style={'textAlign': 'center','color': 'white','fontSize': 15,'margin-top': '-18px'})
        ],className='card_container three columns'),
        
        html.Div([
            html.H6(children='Polis Price', style={'text-align':'center', 'color':color}),
            html.P(f"{price_polis:,.2f}" + " $",style={'textAlign': 'center','color': 'black','fontSize': 40}),
            html.P('All Time High/Low: ' + f"{getPricesOverPeriod('star-atlas-dao', 30, 'usd')['price'].max():,.3f}"
                   + ' / ' + f"{getPricesOverPeriod('star-atlas-dao', 30, 'usd')['price'].min():,.3f}",
                   style={'textAlign': 'center','color': 'white','fontSize': 15,'margin-top': '-18px'})
        ],className='card_container three columns'),
        
        html.Div([
            html.H6(children='Market Cap', style={'text-align':'center', 'color':color}),
            html.P(f"{total_martCap:,.0f}"+" $",style={'textAlign': 'center','color': 'white','fontSize': 40}),
            html.P('ToT: ' + f"{getMarketCapOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1] - getMarketCapOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-2]:,.0f}"
                   + ' (' + str(round(((getMarketCapOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1] - getMarketCapOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-2]) /
                                   getMarketCapOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1]) * 100, 2)) + '%)',
                   style={'textAlign': 'center','color': 'white','fontSize': 15,'margin-top': '-18px'})
        ],className='card_container three columns'),
        html.Div([
            html.H6(children='Total Volumes over 24h', style={'text-align':'center', 'color':color}),
            html.P(f"{total_volume_24h:,.0f}"+" $",style={'textAlign': 'center','color': 'white','fontSize': 40}),
            html.P('ToT: ' + f"{getTotalVolumesOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1] - getTotalVolumesOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-2]:,.0f}"
                   + ' (' + str(round(((getTotalVolumesOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1] - getTotalVolumesOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-2]) /
                                   getTotalVolumesOverPeriod('star-atlas', 30, 'usd')['price'].iloc[-1]) * 100, 2)) + '%)',
                   style={'textAlign': 'center','color': 'white','fontSize': 15,'margin-top': '-18px'})
        
        ],className='card_container three columns')
    ]



appp = DispatcherMiddleware(server, {
    '/dash1': app.server,

})

run_simple('0.0.0.0', 8080, appp, use_reloader=True, use_debugger=True)

