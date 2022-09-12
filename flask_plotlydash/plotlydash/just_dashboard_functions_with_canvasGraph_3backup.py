from dash.dependencies import Input, Output, State
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px # for the 2nd graph
from datetime import datetime

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
        yaxis_range=[0,100], yaxis_title= 'Occurrence in %')
    jbox =go.Figure(
            {"data":jboxdata,
            "layout":jboxlayout})

    return jbox


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
        
    jgoscattermapLayer.update_xaxes(dict(                                
                                rangeslider_visible=True,                                
                                autorange=True,
                                #range= ['x'[0], 'x'[-1]],
                                type='date',
                                #fixedrange=True,                                
                                rangeselector= dict(
                                    buttons = list([
                                        dict(count=26, step="hour", stepmode="todate", label="1D"),
                                        dict(count=7, step="day", stepmode="todate", label="1W"),
                                        dict(count=14, step="day", stepmode="todate", label="2W"),
                                        dict(count=1, step="month", stepmode="todate", label="1M"),
                                        dict(count=2, step="month", stepmode="todate", label="2M"),
                                        dict(count=3, step="month", stepmode="todate", label="3M"),
                                        dict(step="all")
                                    ]),
                                ), 
                                tickformat='%H:%M:%S <br>%d.%m.%Y', # use <br> if want to separate in 2 lines
                                #tick0= str('x'[0]),
                                #dtick=7200000.0, # Converting one day time to milliseconds (86400000.0) (7200000.0 to 2hr),
                            ))
                                
    jgoscattermapLayer.update_yaxes(dict(
                                    range=[0,100],
                                    fixedrange=True))


    jgoscattermapLayer.update_layout(#title='Depth Occurrence',
                        legend = {'orientation': 'h', 'x': 0.1 ,'y':1.4},
                        showlegend=True, # change if you want to see the legend *
                        xaxis={'title': 'Datetime'},
                        yaxis={'title': 'Occurrence in %', 'range': [0,100]}
    )

    return jgoscattermapLayer

def addScatterGraphTrace(jgoscattermap,jacquisitionDepth,jlayerDepthsInPercentage,LayerNumber,UpperDepthLayerRange,LowerDepthLayerRange, lineColor):
    dates = []

    for dt in jacquisitionDepth:
        dates.append(datetime.strptime(dt, "%Y.%m.%d %H:%M:%S"))

    jgoscattermap.add_trace( # 4.1
        go.Scatter(
            x = dates,
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

def drawCanvasGraphFigure():
    graphCanvas = go.Figure()

    img_width = 1
    img_height = 1.5

    graphCanvas.add_layout_image(
        dict(
            x=0,
            sizex=img_width,
            y=img_height,
            sizey=img_height,
            xref="paper",
            yref="paper",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source='../../../static/img/{}.mod_deep_sea_2d_1.jpg',
            #source="{% static 'img/{}.mod_deep_sea_2d_1.jpg' %}",
        )     
    )

    #graphCanvas.update_traces(textposition='outside')

    # Set axes properties
    graphCanvas.update_xaxes(range=[0,1], showgrid=False, visible=False)
    graphCanvas.update_yaxes(range=[0,4], visible=False)   

    graphCanvas.update_layout(width=560, height=450, showlegend=False, template="plotly_white") 

    return graphCanvas

def addCanvasGraphTrace(graphCanvas, color, index, text, meters="", layers=None): 
    rect_height = 0
    start_rect_layers = []
    for i in range(1,13):
        rect_height += 0.1
        start_rect_layers.append(round(rect_height, 2))
    #[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    
    # Rectangle Positioned Relative to the Plot = xref="paper", yref="paper"
    # Rectangle Positioned Relative to the Axis Data = xref="x", yref="y"
    # Add shapes    
    graphCanvas.add_shape(
        type='rect',
        xref="paper", yref="paper",
        # rect positions Relative to the Plot
        x0=0.25, y0=start_rect_layers[index]-0.05, x1=0.78, y1=start_rect_layers[index]+0.05,
        line=dict(color=color),
        fillcolor=color,
    )
    text_height = 0
    start_text_positions = []
    for i in range(1,13):
        text_height += 0.11
        start_text_positions.append(round(text_height, 2))
    #[0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
    graphCanvas.add_annotation(
        xref="paper", yref="paper",
        x=0.88,
        y=start_rect_layers[index],
        text=layers,
        font=dict(
            #family="sans serif",
            size=14,
            color="Black",
        ),
        showarrow=True,
        arrowcolor=color,
        arrowsize=0.3, #minimum
        #arrowwidth=0.1, # thin
        startarrowsize=0.3,
        yshift=1,
        ay=0,
        ax=0,
        #xshift=,
    )
    graphCanvas.add_annotation(
        xref="paper", yref="paper",
        x=0.12,
        y=start_rect_layers[index],
        text=text+meters,
        font=dict(
            #family="sans serif",
            #size=12,
            color="Black",
        ),
        showarrow=True,
        arrowcolor=color,
        arrowsize=0.3, #minimum
        #arrowwidth=0.1, # thin
        startarrowsize=0.3,
        yshift=1,
        ay=0,
        ax=0,
        #xshift=,
    )

    # border rect shape
    graphCanvas.add_shape(
        type='rect',
        xref="paper", yref="paper",
        # rect positions Relative to the Plot
        x0=0.25, y0=start_rect_layers[0]-0.05, x1=0.78, y1=start_rect_layers[-1]+0.15,
        line=dict(color="Black")
    )

#--------------------End Functions ------------------------------- 

