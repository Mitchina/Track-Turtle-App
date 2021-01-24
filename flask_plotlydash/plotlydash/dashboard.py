# being called in __init__.py
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import geopandas as gpd
import json
import plotly.graph_objects as go
#import plotly.offline as py

#import numpy as np
#import pyproj as pj
#import datetime as dt
#from collections import Counter
#import matplotlib.pyplot as plt
#import matplotlib as mpl
#import seaborn as sns
#import shapely
#import descartes #to plotting polygons in geopandas
#import plotly.express as px
#from plotly.subplots import make_subplots

#import io
#import base64




# Flask app into Dash as server
def init_dashboard(server): # or create_dashboard
    
    # didn't need to be assets folder, static works well
    # I changed the name to assets to see if it sees all files in it
    # external_stylesheets = ["/static/assets/style_withdash.css"]
    external_stylesheets = [dbc.themes.BOOTSTRAP]

    # try to create a function that call another file with this function

    # assume you have a "long-form" data frame # see https://plotly.com/python/px-arguments/ for more options
    #df = pd.DataFrame({
    #"Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    #"Amount": [4, 1, 2, 2, 4, 5],
    #"City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    #})

    #fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    #-------------------------------------------------------------------------
    """Create a Plotly Dash dashboard."""
    # Single function which contains the entirety of a Plotly Dash app in itself

    dash_app = dash.Dash(
        server=server,
        # Creating a route for Dash # of course, we could always pass / as our prefix
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=external_stylesheets
        )
    dash_app.css.append_css({
        "external_url":'https://codepen.io/chriddyp/pen/bWLwgP.css',
        "external_url":"/static/assets/style_withdash.css"
        })


    #""""""""""""""""""""""""""""""""""""""""""""""""""""
    # The final Layout of the page will be NavBar + Body
    # Before the Layout let's create separately each of them

    #""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 1st - Creating a NavBar with dropdown Items
    # Create the components that goes in the NavBar

    # make a reusable navitem for the different examples
    nav_item = dbc.NavItem(dbc.NavLink("example - Dash Udemy Course", href="https://www.udemy.com"))

    # make a reusable dropdown for the different examples
    dropdown = dbc.DropdownMenu(
        children=[
        dbc.DropdownMenuItem("Plotly / Dash", href='https://dash.plot.ly/'),
        dbc.DropdownMenuItem("Dash Bootstrap", href='https://dash-bootstrap-components.opensource.faculty.ai/')
        ],
        nav=True,
        in_navbar=True,
        label="Important Links"
        )

    # Navbar Layout
    navbar = dbc.Navbar(

        dbc.Container(
            [

            # A is a link element
            html.A(

                dbc.Row(
                    [
                    dbc.Col(html.H2("Track Turtle App", className= 'ml-2')),
                    dbc.Col(html.Img(src="/static/images/{2}.loggerhead_turtle.jpg", alt="Caretta caretta", height="50px")),
                    ],
                    align='center',
                    no_gutters=True
                ),

                href=('/'),
            ),

            dbc.NavbarToggler(id="navbar-toggler2"),

            dbc.Collapse(

                dbc.Nav(
                    [nav_item, 
                    dropdown
                    ],
                    className="ml-auto",
                    navbar=True
                ),

                id="navbar-collapse2",
                navbar=True
            )

            ]
        ),

        color="dark",
        dark=True,
        className="mb-5"
    )

    #""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 2nd - Creating the body
    # Individuals components of the Graphs first
    ##urlDataPath = ('https://github.com/Juunicacio/Track-Turtle-App/tree/gh-pages/flask_plotlydash/static/data/')
    
    # url of the shapefiles as csv 
    ##url_depthPointsDegree = 'https://raw.githubusercontent.com/Juunicacio/Track-Turtle-App/gh-pages/flask_plotlydash/static/data/%7B4%7D.degree_Acquisition_Time_Depth_Points_Tag_333A_Sept.csv'
    ##url_gpsPoints = 'https://raw.githubusercontent.com/Juunicacio/Track-Turtle-App/gh-pages/flask_plotlydash/static/data/%7B5%7D.reproj_Track_GPS_Points_Tag_333A_Sept.csv'

    # path for the shp files
    path_depthPointsDegree = r"/static/data/{3}.degree_Acquisition_Time_Depth_Points_Tag_333A_Sept_4326.shp"
    path_gpsPoints = r"/static/data/{6}.degree_Track_GPS_Points_Tag_333A_Sept_4326.shp"
    
    #depthPointsDegree = pd.read_csv(path_depthPointsDegree)
    #gpsPoints = pd.read_csv(path_gpsPoints)

    # Depth Lon and Lat in degrees
    #xDegreeDepth = depthPointsDegree.geometry.x
    #yDegreeDepth = depthPointsDegree.geometry.y

    # GPS Lon and Lat in degrees
    #xDegreeGps = gpsPoints['GPS Longit']
    #yDegreeGps = gpsPoints['GPS Latitu']

    # Convert it to a geojson


    # Column Acquisition time of both
    textDepth = depthPointsDegree['Acquisitio']
    textGps = gpsPoints['Acquisitio']

    # Assigning variables for max and min values in layer 1 percentage
    maxPercLay1 = depthPointsDegree['Layer 1 Pe'].max() # it is a float numberminPercLay1 = depthPointsDegree['Layer 1 Pe'].min()
    minPercLay1 = depthPointsDegree['Layer 1 Pe'].min()

    # List of float percentages in layer 1
    layer1Depths = depthPointsDegree['Layer 1 Pe']

    # Converted Decimals to Percentage just to use in the hovertext, for visualization, it don't work with the markers
    layer1DepthsInPercentage = layer1Depths.apply(lambda x: '{:1.2f}%'.format(100 * x))

    # Making an histogram data for layer 1
    gohistlayer1 = [go.Histogram(x=layer1DepthsInPercentage, #y=layer1Depths,
                         opacity=0.4,
                         marker=dict(color='orange'))]
    layout = go.Layout(barmode='overlay',
                                 title='Layer 1 histogram',
                                 yaxis_title='Count',
                                 xaxis_title='Layer 1 occurrence in %') # or 'Percentage (%) of occurrence in Layer 1'
    fig = go.Figure(
            {"data": gohistlayer1,
             "layout": layout})
    #py.iplot(fig, filename='Layer 1 histogram') 
    ################

    dash_app.layout = html.Div ([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or',
                html.A('Select Files')
                ]),
                style={
                'with': '100%',
                'height': '60px', #etc
                },
                # Allow multiple files to be uploaded
                multiple=True
        ),
        html.Div(id='output-data-upload'),
        ]
    )

    html.Div([
        html.H1(children='Hello Dash'),
        html.Div(children= 'Dash: A web application framework for Python'),
        dcc.Graph(
            id='example-graph',
            figure=fig
        )],
        id='dash-container'
    )

    #def parse_data(contents, filename):
    #content_type, content_string = contents.split(',')

    #decoded = base64.b64decode(content_string)
    #try:
        #if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            #df = pd.read_csv(
                #io.StringIO(decoded.decode('utf-8')))
        #elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            #df = pd.read_excel(io.BytesIO(decoded))
        #elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            #df = pd.read_csv(
                #io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    #except Exception as e:
        #print(e)
        #return html.Div([
            #'There was an error processing this file.'
       #])

    #return df #html.Div([
        #dcc.Graph(
            #id='example-graph',
            #figure=fig
            #)
        #])







    
    # Create Dash Layout #... Layout stuff
    ###dash_app.layout = html.Div([

        ###html.Div([
            ###html.Div([html.H2("Track Turtle App")
                ###], className= 'left_column'),
            ###html.Div([html.Img(src="/static/images/{2}.loggerhead_turtle.jpg", alt="Caretta caretta")
                ###], className= 'right_column')
            ###], className='banner clear'),
        ###], className=' container_dashpage clear')

    #(id='dash-container', children=[
        #html.H1(children='Hello Dash'),
        #html.Div(children= 'Dash: A web application framework for Python'),
        #dcc.Graph(
            #id='example-graph',
            #figure=fig
        #)
    #])          

    # Initialize callbacks after our app is loaded
    # Pass dash_app as a parameter
    ##init_callbacks(dash_app)

    return dash_app.server # app is loaded

#def init_callbacks(dash_app):
    #@app.callback(
    # Callback input/output
    #)

    #def update_graph(rows):
        # Callback logic