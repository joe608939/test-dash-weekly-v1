#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Output, Input



def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def creator_stop_word_list():
    with open('stopwords_author_5Dec2019.txt' , encoding="utf8") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]     
    return content

data = pd.read_csv('sample_file_for_weekly_without_nan_v1.csv')
color_list = []
color_change_step = 20
color_start = 70
r = color_start
while r < 210:
    g = color_start
    while g < 210:
        b = color_start
        while b < 210:
            color_list.append('rgb(%s,%s,%s)'%(r,g,b))
            b += color_change_step
        g += color_change_step
    r += color_change_step
number_of_color = len(color_list)



color_dict = {}
stop_word_list = creator_stop_word_list()
unique_author_list = list(set(data['Author name after removing stop word'].tolist()))
unique_author_list = [str(x) for x in unique_author_list if not any(str(y) in str(x) for y in stop_word_list)]
for i in range(0,len(unique_author_list)):
    color_dict[unique_author_list[i]] = color_list[i % number_of_color]



data.insert(data.shape[1],'Year','')
for i in range(0,data.shape[0]):
    year = data.iloc[i]['Search_date']
    required_index = year.rfind('/')
    data.at[i,'Year'] = year[required_index + 1:]
year_list = data['Year'].tolist()
yearList = list(set(year_list))
yearList.sort()

freq_dict = {}
for year in yearList:
    temp_df = data[data['Year']==year]
    author_name_with_no_stop_word = list(set(temp_df['Author name after removing stop word'].tolist()))
    author_list_for_that_year = intersection(author_name_with_no_stop_word, unique_author_list)
    freq_dict[year] = len(author_list_for_that_year)



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div([
    html.Div([
            html.H2('Adjust the year by the slider below.')
            ],style={'text-align':'center'}),
    html.Div([
            dcc.Slider(
            id='demo-slider',
            min=int(yearList[0]),
            max=int(yearList[len(yearList) - 1]),
            step=1,
            marks={
                    int(yearList[0]): str(yearList[0]),
                    int(yearList[int(0.25 * len(yearList))]): str(yearList[int(0.25 * len(yearList))]),
                    int(yearList[int(0.5 * len(yearList))]): str(yearList[int(0.5 * len(yearList))]),
                    int(yearList[int(0.75 * len(yearList))]): str(yearList[int(0.75 * len(yearList))]),
                    int(yearList[len(yearList)-1]): str(yearList[len(yearList) - 1]),
                    },
            value=int(yearList[0]),
            )], style={'margin':'auto','align-items':'center','padding':'50px',}
        ),    
        html.Div(id='text-output-container',style={'margin-top': '50px', 'text-align':'center', 'font-size':'200%' }) ,  
    
        html.Div('Dynamic Controls'),
        html.Hr(),
        html.Div([dcc.RangeSlider(
                id="my-range-slider",
                min=1,
                max=1952,
                step = 1,
                marks = {

                },
                value=[1,20]
            )],style={'margin':'auto','align-items':'center','padding':'50px',}),
        html.Hr(),
        html.Div(id='text-output-container_2',style={'margin-top': '50px', 'text-align':'center', 'font-size':'200%' }) , 
        html.Div([
                dcc.Graph(
                    id='dd-output-container',
                    style={
                        "width":1200, 
                        "height":800,
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        }
                    )
                ]),           
            ],
        )

@app.callback(dash.dependencies.Output('my-range-slider', 'marks'),
              [dash.dependencies.Input('demo-slider', 'value')])
def update_slider_example_value(input): 
    dict = {}
    dict[1] = 1
    dict[int(freq_dict[str(input)])] = int(freq_dict[str(input)])
    dict[int(0.25 * int(freq_dict[str(input)]))] = int(0.25 * int(freq_dict[str(input)]))
    dict[int(0.5 * int(freq_dict[str(input)]))] = int(0.5 * int(freq_dict[str(input)]))
    dict[int(0.75 * int(freq_dict[str(input)]))] = int(0.75 * int(freq_dict[str(input)]))
    return dict

@app.callback(
    dash.dependencies.Output('my-range-slider','max'),
    [dash.dependencies.Input('demo-slider', 'value')])

def update_slider_max(input):
    max_value = freq_dict[str(input)]
    return max_value

@app.callback(
    [dash.dependencies.Output('text-output-container', 'children'),
     dash.dependencies.Output('text-output-container_2', 'children'),
     dash.dependencies.Output('dd-output-container', 'figure')
     ],
    [dash.dependencies.Input('my-range-slider', component_property='max'),
    dash.dependencies.Input('my-range-slider', component_property='min'),
     dash.dependencies.Input('my-range-slider', 'value'),
    dash.dependencies.Input('demo-slider', 'value')
    ])

def update_output_graph(max_value, min_value,slider_list, year):
    input_str = str(year)
    return_str = 'Year : ' + input_str
    range_start = str(slider_list[0])
    range_end = str(slider_list[1])
    return_str_2 = 'From ' + range_start + ' to ' + range_end
    temp_df = data[data['Year'] == input_str]
    name_list_from_temp_df = list(temp_df['Author name after removing stop word'])
    sorted_temp_dict = {}
    temp_dict = {}
    for i in range(0,len(unique_author_list)):
        count = 0
        for element in name_list_from_temp_df:
            if str(element) == unique_author_list[i] and str(element) != 'nan':
                count = count + 1
            temp_dict[unique_author_list[i]] = count
    sorted_temp_dict = [(k, temp_dict[k]) for k in sorted(temp_dict, key=temp_dict.get, reverse=True)]
    temp_data = []
    x,y,plot_color = [],[],[]
    for i in range(int(slider_list[0]) - 1,int(slider_list[1])):
        x.append(sorted_temp_dict[i][0])
        y.append(sorted_temp_dict[i][1])
        plot_color.append(color_dict[sorted_temp_dict[i][0]])
    x.reverse()
    y.reverse()
    plot_color.reverse()
    trace_close = go.Bar(
                x=y, y=x,
                text=x,
                textposition='auto',
                orientation='h',
                marker = dict(color=plot_color)
            )
    temp_data.append(trace_close)
    
    layout = {"title":"Frequency of name in field Creator in year " + input_str,
              "xaxis":{"title": 'Frequency'},
              "yaxis": {"title": 'Name',
                     "dtick": 1},  


    }
    return return_str,return_str_2,{  
        "data":temp_data,
        "layout" : layout
    }
    
if __name__ == '__main__':
    app.run_server(debug = False)



