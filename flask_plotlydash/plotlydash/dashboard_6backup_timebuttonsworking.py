# being called in __init__.py
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import requests
import plotly.graph_objects as go
import plotly.express as px # for the 2nd graph
from datetime import datetime
#import plotly.offline as py --------- using when debugging in jupyter notebook

'''-------------------- Functions ------------------------------- 
1. Function to return all the variables I need from the Depth data

    1.1 Looping through Layer

    1.2 Assigning variables for max and min float values in layer percentage

    1.3 Converted Decimals of Layer to Percentage just to use in the hovertext, for visualization, it don't work with the markers

    1.4 returning Layer values (float), minimum Layer value (float), maximum Layer value (float), Layer values in Percentage

2. Function to make an histogram data for Layer 

3. Function to make Go Map for Layer

4. Making Go Scatter for Layer 1 

    4.1 add trace to Go Scatter

'''
COLOR_LAYER1 = 'orange'
COLOR_LAYER2 = 'red'
COLOR_LAYER3 = 'green'
COLOR_LAYER4 = 'magenta'
COLOR_LAYER5 = 'grey'
COLOR_LAYER6 = 'brown'
COLOR_LAYER7 = 'blue'
COLOR_LAYER8 = 'purple'
COLOR_LAYER9 = 'navy'
COLOR_LAYER10 = 'black'

def loadLayerData(LayerColumn,JsonDepthData): # 1

    jlayerDepths = [] 
    for i in JsonDepthData['features']:
        layer = i['properties'][LayerColumn]
        jlayerDepths.append(layer) # 1.1     
    
    jminPercLay = min(feature["properties"][LayerColumn] for feature in JsonDepthData['features']) # 1.2
    jmaxPercLay = max(feature["properties"][LayerColumn] for feature in JsonDepthData['features']) # 1.2
    
    jlayerDepthsInPercentage = []
    for i in JsonDepthData['features']:
        intNum = i['properties'][LayerColumn]*100
        percSymbol = '{:.2f}%'.format( intNum )
        jlayerDepthsInPercentage.append(percSymbol) # 1.3

    return jlayerDepths,jminPercLay,jmaxPercLay,jlayerDepthsInPercentage #1.4

def generateHistogramGraph(LayerValueInPercentage, LayerNumber): # 2
    
    results = [v for v in LayerValueInPercentage if float(v.strip('%')) > 1.0]
    jgohistlayer = [go.Histogram(x=results, 
                         opacity=0.4,
                         nbinsx=20,
                         marker=dict(color='orange'))]
    jlayout = go.Layout(barmode='overlay',
                                #width= 800,
                                #height= 400,
                                #title=f'Layer {LayerNumber} histogram',
                                xaxis={'range':[1,100], 'title':f'Layer {LayerNumber} occurrence in %'},
                                yaxis={'range':[0,500], 'title':'Count'})                                
    jfig = go.Figure(
            {"data": jgohistlayer,
             "layout": jlayout})

    return jfig

def generateBoxGraph(LayerNumber, jlayerDepthsInPercentage, color):
    results = [v for v in jlayerDepthsInPercentage if float(v.strip('%')) > 1.0]
    jboxdata = go.Box(name= f' Layer {LayerNumber}', y=results, fillcolor=color)   
    jboxlayout =  go.Layout(#width=400, height=400, 
        yaxis_range=[0,100])
    jbox =go.Figure(
            {"data":jboxdata,
            "layout":jboxlayout})

    return jbox

def generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage, lineColor):

    dates = []

    for dt in jacquisitionDepth:
        dates.append(datetime.strptime(dt, "%Y.%m.%d %H:%M:%S"))

    jlinedata = [go.Scatter(
                        x=dates,
                        y=jlayerDepthsInPercentage,
                        #xaxis_title='Datetime',
                        #yaxis_title='Occurrence in %',
                        #yaxis_range=[0,100],
                        line = dict(
                            width = 1,
                            color = lineColor)
                    )]
    jlinelayout = go.Layout(#width=800, height=400, 
                            xaxis={'autorange':True,
                                'range': ['x'[0], 'x'[-1]],
                                'rangeselector': {
                                    'buttons' : [
                                        #{'count':2, 'step':"hour", 'stepmode':"todate", 'label':"2h"},
                                        #{'count':24, 'step':"hour", 'stepmode':"todate", 'label':"24h"},
                                        {'count':25, 'step':"hour", 'stepmode':"todate", 'label':"1d"},
                                        #{'count':7, 'step':"day", 'stepmode':"backward", 'label':"1w"},
                                        #{'count':14, 'step':"day", 'stepmode':"backward", 'label':"2w"},
                                        #{'count':1, 'step':"month", 'stepmode':"backward", 'label':"1m"},
                                        #{'step':"all"}
                                    ]},
                                'rangeslider_visible':True, 
                                'type':'date',
                                'tickformat':'%Y.%m.%d %H:%M:%S', # use <br> if want to separate in 2 lines
                                'tick0': str(dates[0]),
                                'dtick':7200000.0, # Converting one day time to milliseconds (86400000.0) (7200000.0 to 2hr)
                                'fixedrange':True},
                            yaxis={'range':[0,100],
                                'fixedrange':True}
                    )

    #config = dict(displayModeBar=False, scrollZoom=False )

    jline = go.Figure(
            {"data":jlinedata,
            "layout":jlinelayout})
            #"config":config})             
    
    return jline

def generateGeoMap (jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths, 
    jmaxPercLay, jminPercLay, jlayerDepthsInPercentage, LayerNumber): # 3
    
    jgomaptraceLayer = go.Figure(go.Scattermapbox(
                                    lat=jyDegreeGps,
                                    lon=jxDegreeGps,
                                    name = 'GPS Data',
                                    mode="markers+lines",
                                    marker = {'size': 8, 'color': 'yellow'}, # changed the size
                                    text = jacquisitionGps,
                                    hoverinfo='text'
                                ))
    jgomaptraceLayer.add_trace(go.Scattermapbox(
                                    lat=jyDegreeDepth,
                                    lon=jxDegreeDepth,
                                    name = 'Depth data from 0 to -5 meters deep', #############
                                    mode = "markers+lines",
                                    text = jlayerDepths,
                                    marker = {        
                                        'colorscale':[[0, 'green'], [1, 'rgb(0, 0, 255)']],
                                        'color': jlayerDepths,
                                        'cmax':jmaxPercLay,
                                        'cmin':jminPercLay,
                                        'size': jlayerDepths,
                                        'sizemin':0.1,
                                        'sizemode': 'area',
                                        'sizeref': jmaxPercLay / 6 **2,
                                        'showscale':True,
                                        'colorbar': {
                                            'title': f'Layer {LayerNumber} occurrence in %', # including a colorbar
                                            'titleside':'top',
                                            'x': 0,
                                            'y': 0.5,
                                            'tickformat': ".0%", # Formating tick labels to percentage on color bar
                                            'tickfont': {
                                                'color': '#000000',
                                                'family':"Open Sans",
                                                'size': 14
                                            }
                                        }
                                    },   
                                    hoverinfo='text',
                                    hovertext = jlayerDepthsInPercentage,  #100 * x), #(lambda x: '{0:1.2f}%'.format(x)#{:. n%} 
                                    opacity = 1
                                ))
    jgomaptraceLayer.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                showlegend=False, # change if you want to see the legend *
                mapbox = {        
                    'style': "stamen-terrain",
                    'center': {'lon': 10, 'lat': 37},
                    'zoom': 5})

    return jgomaptraceLayer

def generateScatterGraph(): # 4

    jgoscattermapLayer = go.Figure()
        
    jgoscattermapLayer.update_xaxes(
        rangeslider_visible=True,        
        rangeselector= dict(
                            buttons = list([
                                dict(count=1, step="hour", stepmode="todate", label="1h"),
                                dict(count=1, step="day", stepmode="todate", label="1d"),
                                dict(count=1, step="month", stepmode="todate", label="1m"),
                                dict(count=2, step="month", stepmode="todate", label="2m"),
                                dict(count=3, step="month", stepmode="backward", label="3m"),
                                dict(step="all")
                            ])
        ),
        #type='date'
    )

    jgoscattermapLayer.update_layout(#title='Depth Occurrence',
                        legend = {'orientation': 'h', 'x': 0.1 ,'y':1.4},
                        showlegend=True, # change if you want to see the legend *
                        xaxis={'title': 'Datetime'},
                        yaxis={'title': 'Occurrence in %', 'range': [0,100]}
    )

    return jgoscattermapLayer

def addScatterGraphTrace(jgoscattermap,jacquisitionDepth,jlayerDepthsInPercentage,LayerNumber,UpperDepthLayerRange,LowerDepthLayerRange, lineColor):
    jgoscattermap.add_trace( # 4.1
        go.Scatter(
            x = jacquisitionDepth,
            y = jlayerDepthsInPercentage,
            name=f'Layer {LayerNumber}: between {UpperDepthLayerRange} to {LowerDepthLayerRange} meters deep',
            showlegend=True,
            #marker = dict(
            line = dict(
                width = 1,
                color = lineColor)
            #)
        )
    )
#--------------------End Functions ------------------------------- 

''' ------------------ Flask app into Dash as server
5. didn't need to be assets folder, static works well
5.1 I changed the name to assets to see if it sees all files in it

6. Single function which contains the entirety of a Plotly Dash app in itself
6.1 Creating a route for Dash # of course, we could always pass / as our prefix

- If you want to append css files
    dash_app.css.append_css({
        "external_url":'dbc.themes.BOOTSTRAP'
        "external_url":'https://codepen.io/chriddyp/pen/bWLwgP.css',
        "external_url":"/static/assets/style_withdash.css"
        })

7. url (raw) path for Json files

8. Reading the Json files from url
'''
def init_dashboard(server): # or create_dashboard   # 5 + # 5.1    
    external_stylesheets = ["/static/assets/style_withdash.css"]
    #external_stylesheets = [dbc.themes.BOOTSTRAP] # bootstrap css as principal


    #------------------ Create a Plotly Dash dashboard ------------    
    dash_app = dash.Dash( # 6
        server=server,        
        routes_pathname_prefix='/dashapp/', # 6.1
        external_stylesheets=external_stylesheets
        )
    
 
    # ------------------ Creating the body - the Data
    # 7
    url_depthPointsDegree = 'https://raw.githubusercontent.com/Juunicacio/Track-Turtle-App/gh-pages/flask_plotlydash/static/data/%7B7%7D.depthPointsDegree.json'
    url_gpsPoints = 'https://raw.githubusercontent.com/Juunicacio/Track-Turtle-App/gh-pages/flask_plotlydash/static/data/%7B8%7D.gpsPointsDegree.json'

    # 8
    responseDegree = requests.get(url_depthPointsDegree)
    responseGps = requests.get(url_gpsPoints)

    jdata_depthPointsDegree = responseDegree.json()
    jdata_gpsPointsDegree = responseGps.json()

    # CREATE A loop through Depth Lon[0] and Lat[1]--------
    jxDegreeDepth = []
    jyDegreeDepth = []
    for i in jdata_depthPointsDegree['features']:
        lonDepth = i['geometry']['coordinates'][0]
        latDepth = i['geometry']['coordinates'][1]
        jxDegreeDepth.append(lonDepth)
        jyDegreeDepth.append(latDepth)

    # CREATE A loop through GPS Lon[0] and Lat[1]
    jxDegreeGps = []
    jyDegreeGps = []
    for i in jdata_gpsPointsDegree['features']:
        lonGps = i['geometry']['coordinates'][0]
        latGps = i['geometry']['coordinates'][1]
        jxDegreeGps.append(lonGps)
        jyDegreeGps.append(latGps)

    # Creating a loop for Depth Acquisition time ----------
    jacquisitionDepth = []
    for i in jdata_depthPointsDegree['features']:
        aquisDepth = i['properties']['Acquisitio']
        jacquisitionDepth.append(aquisDepth)

    # Creating a loop for GPS Acquisition time
    jacquisitionGps = []
    for i in jdata_gpsPointsDegree['features']:
        aquisGps = i['properties']['Acquisitio']
        jacquisitionGps.append(aquisGps)

    # Call function to return all the variables I need from the Depth data
    # Layer values (float), minimum Layer value (float), maximum Layer value (float), Layer values in Percentage
    jlayerDepths1,jminPercLay1,jmaxPercLay1,jlayerDepthsInPercentage1 = loadLayerData('Layer 1 Pe',jdata_depthPointsDegree)
    jlayerDepths2,jminPercLay2,jmaxPercLay2,jlayerDepthsInPercentage2 = loadLayerData('Layer 2 Pe',jdata_depthPointsDegree)
    jlayerDepths3,jminPercLay3,jmaxPercLay3,jlayerDepthsInPercentage3 = loadLayerData('Layer 3 Pe',jdata_depthPointsDegree)
    jlayerDepths4,jminPercLay4,jmaxPercLay4,jlayerDepthsInPercentage4 = loadLayerData('Layer 4 Pe',jdata_depthPointsDegree)
    jlayerDepths5,jminPercLay5,jmaxPercLay5,jlayerDepthsInPercentage5 = loadLayerData('Layer 5 Pe',jdata_depthPointsDegree)
    jlayerDepths6,jminPercLay6,jmaxPercLay6,jlayerDepthsInPercentage6 = loadLayerData('Layer 6 Pe',jdata_depthPointsDegree)
    jlayerDepths7,jminPercLay7,jmaxPercLay7,jlayerDepthsInPercentage7 = loadLayerData('Layer 7 Pe',jdata_depthPointsDegree)
    jlayerDepths8,jminPercLay8,jmaxPercLay8,jlayerDepthsInPercentage8 = loadLayerData('Layer 8 Pe',jdata_depthPointsDegree)
    jlayerDepths9,jminPercLay9,jmaxPercLay9,jlayerDepthsInPercentage9 = loadLayerData('Layer 9 Pe',jdata_depthPointsDegree)
    jlayerDepths10,jminPercLay10,jmaxPercLay10,jlayerDepthsInPercentage10 = loadLayerData('Layer 10 P',jdata_depthPointsDegree)


    jfig1 = generateHistogramGraph(jlayerDepthsInPercentage1, 1)
    jfig2 = generateHistogramGraph(jlayerDepthsInPercentage2, 2)
    jfig3 = generateHistogramGraph(jlayerDepthsInPercentage3, 3)
    jfig4 = generateHistogramGraph(jlayerDepthsInPercentage4, 4)
    jfig5 = generateHistogramGraph(jlayerDepthsInPercentage5, 5)
    jfig6 = generateHistogramGraph(jlayerDepthsInPercentage6, 6)
    jfig7 = generateHistogramGraph(jlayerDepthsInPercentage7, 7)
    jfig8 = generateHistogramGraph(jlayerDepthsInPercentage8, 8)
    jfig9 = generateHistogramGraph(jlayerDepthsInPercentage9, 9)
    jfig10 = generateHistogramGraph(jlayerDepthsInPercentage10, 10)

    jbox1 = generateBoxGraph(1, jlayerDepthsInPercentage1, COLOR_LAYER1)
    jbox2 = generateBoxGraph(2, jlayerDepthsInPercentage2, COLOR_LAYER2)
    jbox3 = generateBoxGraph(3, jlayerDepthsInPercentage3, COLOR_LAYER3)
    jbox4 = generateBoxGraph(4, jlayerDepthsInPercentage4, COLOR_LAYER4)
    jbox5 = generateBoxGraph(5, jlayerDepthsInPercentage5, COLOR_LAYER5)
    jbox6 = generateBoxGraph(6, jlayerDepthsInPercentage6, COLOR_LAYER6)
    jbox7 = generateBoxGraph(7, jlayerDepthsInPercentage7, COLOR_LAYER7)
    jbox8 = generateBoxGraph(8, jlayerDepthsInPercentage8, COLOR_LAYER8)
    jbox9 = generateBoxGraph(9, jlayerDepthsInPercentage9, COLOR_LAYER9)
    jbox10 = generateBoxGraph(10, jlayerDepthsInPercentage10, COLOR_LAYER10)

    jline1 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage1, COLOR_LAYER1)
    jline2 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage2, COLOR_LAYER2)
    jline3 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage3, COLOR_LAYER3)
    jline4 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage4, COLOR_LAYER4)
    jline5 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage5, COLOR_LAYER5)
    jline6 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage6, COLOR_LAYER6)
    jline7 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage7, COLOR_LAYER7)
    jline8 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage8, COLOR_LAYER8)
    jline9 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage9, COLOR_LAYER9)
    jline10 = generateLineGraph(jacquisitionDepth, jlayerDepthsInPercentage10, COLOR_LAYER10)

    jgomaptraceLayer1 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths1, 
    jmaxPercLay1, jminPercLay1, jlayerDepthsInPercentage1, 1)
    jgomaptraceLayer2 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths2, 
    jmaxPercLay2, jminPercLay2, jlayerDepthsInPercentage2, 2)
    jgomaptraceLayer3 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths3, 
    jmaxPercLay3, jminPercLay3, jlayerDepthsInPercentage3, 3)
    jgomaptraceLayer4 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths4, 
    jmaxPercLay4, jminPercLay4, jlayerDepthsInPercentage4, 4)
    jgomaptraceLayer5 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths5, 
    jmaxPercLay5, jminPercLay5, jlayerDepthsInPercentage5, 5)
    jgomaptraceLayer6 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths6, 
    jmaxPercLay6, jminPercLay6, jlayerDepthsInPercentage6, 6)
    jgomaptraceLayer7 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths7, 
    jmaxPercLay7, jminPercLay7, jlayerDepthsInPercentage7, 7)
    jgomaptraceLayer8 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths8, 
    jmaxPercLay8, jminPercLay8, jlayerDepthsInPercentage8, 8)
    jgomaptraceLayer9 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths9, 
    jmaxPercLay9, jminPercLay9, jlayerDepthsInPercentage9, 9)
    jgomaptraceLayer10 = generateGeoMap(jyDegreeGps, jxDegreeGps, jacquisitionGps, jyDegreeDepth, jxDegreeDepth, jlayerDepths10, 
    jmaxPercLay10, jminPercLay10, jlayerDepthsInPercentage10, 10)

    jgoscatterGraph = generateScatterGraph()
    addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage1,1,0,-5, COLOR_LAYER1)
    ######################### END DATA GRAPHS #####################################################
    
    ''' --------------- Create Dash Layout # Page Layout stuff ------------------------------------------------------
    - The final Layout of the page will be NavBar + Body
    - Before the Layout let's create separately each of them   
    ---------- 1st - Creating a NavBar with dropdown Items
    - Create the components that goes in the NavBar
    - make a reusable navitem for the different examples
    '''
    nav_item = dbc.NavItem(dbc.NavLink("example - Dash Udemy Course", href="https://www.udemy.com"))

    # make a reusable dropdown for the different examples
    dropdown = dbc.DropdownMenu(children=[
        dbc.DropdownMenuItem("Plotly / Dash", href='https://dash.plot.ly/'),
        dbc.DropdownMenuItem("Dash Bootstrap", href='https://dash-bootstrap-components.opensource.faculty.ai/')
        ],
        nav=True,
        in_navbar=True,
        label="Important Links"
        )
    # Navbar Layout
    navbar = dbc.Navbar([
        #dbc.Container([
            dbc.Col(html.H1("Track Turtle App", className= 'ml-5')),           

            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav([
                    nav_item, 
                    dropdown
                    ],
                    className="ml-auto",
                    navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,                
            ),

             # A is a link element
            html.A(
                dbc.Row([
                    #dbc.Col(html.H2("Track Turtle App", className= 'ml-2 left_column')),
                    dbc.Col(html.Img(src="/static/images/{2}.loggerhead_turtle.jpg", alt="Caretta caretta", height="50px")),
                    ],
                    align='center',
                    no_gutters=True
                ), 
                href=('/'),
                className= 'ml-4 mr-5'                
            ),
        #]), #id="top_banner"),
        #color="dark",
        #dark=True,
        #className="banner"# mb-5"
    ])
    # ---------- Creating Dash Layout and call the graphs

    dash_app.layout = html.Div([

        #html.Link(rel='stylesheet', href='/static/assets/style_withdash.css'),
        html.Link(rel='stylesheet', href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"),        

        html.Div([navbar
            #html.Div([html.H2("Track Turtle App")
                #], className= 'left_column'),
            #html.Div([html.Img(src="/static/images/{2}.loggerhead_turtle.jpg", alt="Caretta caretta")
                #], className= 'right_column')
            ]), #className='banner'),
        
        # ----------------------- GRAPHS -------------------------------
        html.Div(className= 'content-dash-container ml-5 mr-5 clear', children=[

            #html.H1(className= 'text-center' ,children='Hello Dash'),
            #html.Div(id='top', className= 'row', children=[
            dbc.Row([
                dbc.Col(html.Div(className= 'graph_text', children=[                                      
                        html.Div(className= 'graph_description', children=[                            
                            html.H1(className= 'text-center' ,children='Hello Dash'),
                            html.P('Layer 1 Description'),                                                                                
                        ]),
                        dcc.Dropdown(
                                id='layer-dropdown',
                                options=[
                                    {'label': 'Layer 1 - Occurrence between 0 to -5 meters deep', 'value': '0'},
                                    {'label': 'Layer 2 - Occurrence between -6 to -10 meters deep', 'value': '1'},
                                    {'label': 'Layer 3 - Occurrence between -11 to -20 meters deep', 'value': '2'},
                                    {'label': 'Layer 4 - Occurrence between -21 to -30 meters deep', 'value': '3'},
                                    {'label': 'Layer 5 - Occurrence between -31 to -40 meters deep', 'value': '4'},
                                    {'label': 'Layer 6 - Occurrence between -41 to -50 meters deep', 'value': '5'},
                                    {'label': 'Layer 7 - Occurrence between -51 to -70 meters deep', 'value': '6'},
                                    {'label': 'Layer 8 - Occurrence between -71 to -90 meters deep', 'value': '7'},
                                    {'label': 'Layer 9 - Occurrence between -91 to -110 meters deep', 'value': '8'},
                                    {'label': 'Layer 10 - Occurrence between -111 to -4095 meters deep', 'value': '9'},
                                ],
                                value='0'
                        )
                    ]),
                )
            ]),
            dbc.Row([                
                dbc.Col(html.Div(className= 'graph_graph', children=[
                        # ------------------- calling histogram graph ------------------                
                        dcc.Graph(
                            id='hist_graph',
                            figure=jfig1 
                        ), # ------------------- end histogram)
                    ]), width=4
                ),
                dbc.Col(html.Div(className='graph_graph2', children=[
                        # ------------------- calling box graph ------------------ 
                        dcc.Graph(
                            id='box_graph',
                            figure= jbox1
                        ) # ------------------- end box)
                    ]), width=4
                #html.Div(className= 'clear'),
                ),
                dbc.Col(html.Div(className= 'graph_graph3', children=[
                        # ------------------- calling line graph ------------------                
                        dcc.Graph(
                            id='line_graph',
                            figure=jline1,
                            config={'displayModeBar':False}
                        ), # ------------------- end line)
                    ]), width=4
                ),
            ]),               
            # ----------------------- calling Map graph layer 1 -------------------------------
            dbc.Row([
                dbc.Col(html.Div(id='div_map_graph clear', children=[
                        #html.Div(children=[
                            #html.H2(children='Depth Map'),
                            #html.Div(children= 'Turtle Track Map')],
                            #className= 'row3'),                        
                        dcc.Graph(
                            id='map_graph',
                            figure=jgomaptraceLayer1
                        )  # ------------------- end Map
                    ])
                )
            ]),
             # ---------------------- calling Scatter graph layer 1 ---------------------------
            dbc.Row([
                dbc.Col(html.Div(id='div_scatter_graph clear', children=[

                        html.H2(children='Scatter'),
                        html.Div(children= 'Depth Occurrence in %'),
                        dcc.Checklist(
                            id='layer-checklist',
                            options=[
                                {'label': 'Layer 1', 'value': '0'},
                                {'label': 'Layer 2', 'value': '1'},
                                {'label': 'Layer 3', 'value': '2'},
                                {'label': 'Layer 4', 'value': '3'},
                                {'label': 'Layer 5', 'value': '4'},
                                {'label': 'Layer 6', 'value': '5'},
                                {'label': 'Layer 7', 'value': '6'},
                                {'label': 'Layer 8', 'value': '7'},
                                {'label': 'Layer 9', 'value': '8'},
                                {'label': 'Layer 10', 'value': '9'},
                            ],
                            value=['0'],
                            labelStyle={'display': 'inline-block'}
                        ),
                        dcc.Graph(
                                id='scatter_graph',
                                figure=jgoscatterGraph
                                ) # ------------------- end Scatter
                    ])
                )
            ]),            
        ])
    ], className=' container_dashpage')


    @dash_app.callback(
        Output('hist_graph', 'figure'),
        Output('box_graph', 'figure'),
        Output('line_graph', 'figure'),
        Output('map_graph', 'figure'),        
        Input('layer-dropdown', 'value'))
    def update_histAndMap(selected_value):
        if(selected_value == '0'):
            return jfig1, jbox1, jline1, jgomaptraceLayer1
        elif (selected_value == '1'):
            return jfig2, jbox2, jline2, jgomaptraceLayer2
        elif (selected_value == '2'):
            return jfig3, jbox3, jline3, jgomaptraceLayer3
        elif (selected_value == '3'):
            return jfig4, jbox4, jline4, jgomaptraceLayer4
        elif (selected_value == '4'):
            return jfig5, jbox5, jline5, jgomaptraceLayer5
        elif (selected_value == '5'):
            return jfig6, jbox6, jline6, jgomaptraceLayer6
        elif (selected_value == '6'):
            return jfig7, jbox7, jline7, jgomaptraceLayer7
        elif (selected_value == '7'):
            return jfig8, jbox8, jline8, jgomaptraceLayer8
        elif (selected_value == '8'):
            return jfig9, jbox9, jline9, jgomaptraceLayer9
        elif (selected_value == '9'):
            return jfig10, jbox10, jline10, jgomaptraceLayer10

    @dash_app.callback(
        Output('scatter_graph', 'figure'),        
        Input('layer-checklist', 'value'))
    def update_histAndMap(selected_values):
        jgoscatterGraph = generateScatterGraph()

        if '0' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage1,1,0,-5, COLOR_LAYER1)
        if '1' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage2,2,-6,-10, COLOR_LAYER2)
        if '2' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage3,3,-11,-20, COLOR_LAYER3)
        if '3' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage4,4,-21,-30, COLOR_LAYER4)
        if '4' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage5,5,-31,-40, COLOR_LAYER5)
        if '5' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage6,6,-41,-50, COLOR_LAYER6)
        if '6' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage7,7,-51,-70, COLOR_LAYER7)
        if '7' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage8,8,-71,-90, COLOR_LAYER8)
        if '8' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage9,9,-91,-110, COLOR_LAYER9)
        if '9' in selected_values :
            addScatterGraphTrace(jgoscatterGraph,jacquisitionDepth,jlayerDepthsInPercentage10,10,-111,-4095, COLOR_LAYER10)

        return jgoscatterGraph

    return dash_app.server # app is loaded

