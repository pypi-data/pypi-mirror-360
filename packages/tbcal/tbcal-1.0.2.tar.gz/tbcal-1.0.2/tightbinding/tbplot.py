import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import ipywidgets as widgets
from ipywidgets import interact, HBox, VBox
from IPython.display import clear_output
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State


def plot_bands(x, y):
    fig = go.Figure(data = go.Scatter(x=x, y=y, mode='markers',marker_line_width=1))
    fig.show()




def plot_interactive_bands(
        x1, y1, cdata, x2, y2, 
        marker_size1=1, marker_size2=1,
        hermitian: bool = True,
    ):
    '''
    x1(1D), y1(1D)为subplot1(能带图)的的x轴，y轴数据
    z2(2D)为对应subplot1数据点的subplot2(场分布)数据源，axis=1与x1,y1等长
    x2(1D), y2(1D)为对应z2数据的坐标点，与x1,y1等长
    '''
    customdata = cdata.T  # axis=1 is index in tightbounding.tbcalculation
    f = make_subplots(
        rows=1, cols=2,
        column_widths=[0.6, 0.4],
        row_heights=[1],
        specs=[[{"type": "scatter"}, {"type": "scatter"}]],
        subplot_titles=("Energy band", "Field distribution"),
        figure=go.FigureWidget()
    )

    # 显示复数能量，而画图数据只有实部
    text_values = [f"{y1_i:.2f}" for y1_i in y1]
    band = go.Scatter(
        x=x1, y=y1.real, mode='markers', customdata = customdata.real,
        hovertemplate='%{x}, E=%{text}', text = text_values, 
        showlegend=False,
    )
    band.marker = {
        'line_width': 1, 'line_color':'rgba(0,0,0,0.5)',
    }
    field = go.Scatter(
        x=x2, y=y2, mode='markers', customdata = np.ones(x2.shape[0]),
        hovertemplate='%{marker.color:.2f}', showlegend=False,
    ) 
    field.marker = {
        'size': [90*marker_size2/np.power(y2.shape[0],1/2)] * y1.shape[0],
        'line_color':'rgba(0,0,0,0.3)', 'cauto':True,
        'color': customdata[0].real*0, 'cmin':0,
    }
   

    f.add_trace(band ,row=1, col=1)
    f.add_trace(field,row=1, col=2)
    f.update_layout(
        margin=dict(r=20, t=50, b=50, l=20),
        xaxis2=dict(scaleanchor='y2')    # subplot2 x,y等比例
    )
   

    # 单击能带画场分布
    if hermitian:
        c_init = ['lightblue'] * y1.shape[0]
    else:
        f.data[0].marker.cmid = 0
        c_init = y1.imag
    s_init = [8*marker_size1]* y1.shape[0]
    f.data[0].marker.color = c_init
    f.data[0].marker.size = s_init   


    def update_point(trace, points, selector):
        for i in points.point_inds:
            update_point_ind(i)


    def update_point_ind(i):  
        c = c_init.copy()
        s = s_init.copy()
        if hermitian:
            c[i] = 'rgba(0,0,0,0.7)'
        s[i] = 20
        z = f.data[0].customdata[i]        
        with f.batch_update():
            f.data[0].marker.color = c
            f.data[0].marker.size = s
            f.data[1].marker.color = z
            f.data[1].customdata[0] = i
            if normE_Ez_dropdown.value == 'Ez':
                max_min = np.abs(z).max()
                f.data[1].marker.cmax = max_min
                f.data[1].marker.cmin = -max_min
            elif normE_Ez_dropdown.value == 'normE':
                f.data[1].marker.cmax = np.max(z)
                f.data[1].marker.cmin = 0

        


    f.data[0].on_click(update_point)


    # 更新颜色映射
    colorscale_dropdown = widgets.Dropdown(
        options=[ 'hot', 'Rainbow', 'PuOr', 'Blues', 'Reds','Purples','RdBu'],
        value='RdBu',  
        description='Colorscale:'
    )

    
    def update_colorscale(colorscale):
        with f.batch_update():  # 批量更新以提高性能
            f.data[1].marker.colorscale = colorscale
    
    interact(update_colorscale, colorscale=colorscale_dropdown)


    # 更新场分布形式
    normE_Ez_dropdown = widgets.Dropdown(
        options=["normE", "Ez"],
        value="normE", 
        description="Data:"
    )


    def update_subplot_data(selected_data):
        if selected_data == 'Ez':
            f.data[0].customdata = customdata.real
            update_colorscale('RdBu')
        elif selected_data == 'normE':
            f.data[0].customdata = np.abs(customdata)
            update_colorscale('Purples')
        update_point_ind(int(f.data[1].customdata[0]))


    interact(update_subplot_data, selected_data=normE_Ez_dropdown)    


    # 排布下拉列表
    controls = HBox([normE_Ez_dropdown, colorscale_dropdown])
    clear_output(wait=True)  # 防止多次输出
    return VBox([controls, f])




def plot_interactive_bands_dash(
        x1, y1, cdata, x2, y2, z2=None,
        marker_size1=1, marker_size2=1,
        hermitian: bool = True,
        port=8051
    ):
    '''
    浏览器打开 http://127.0.0.1:8051 查看交互图
    port=8051 可以修改端口
    '''

    customdata = cdata.T  # axis=1 is index in tightbounding.tbcalculation

    text_values = [f"{y1_i:.2f}" for y1_i in y1]
    band = go.Figure(
        data = go.Scatter(
            x=x1, y=y1.real, mode='markers', 
            hovertemplate='%{x}, E=%{text}', text = text_values, showlegend=False,
            marker = {
                'line_width': 1, 'line_color':'rgba(0,0,0,0.5)',
                'color': 'lightblue', 'size': 10*marker_size1,
            },
        ),
        layout = {'title': 'Energy band', 'title_font_size': 30,
                  'height': 600, 'width': 800, 
                  'yaxis': {'title':'Energy', 'title_font_size': 25},
        }
    )

    # 判断场分布是 2D or 3D
    if np.all(z2 == None):
        field = go.Figure(
            data = go.Scatter(
                x=x2, y=y2, mode='markers', customdata = np.ones(x2.shape[0]),
                hovertemplate='%{marker.color:.2f}', showlegend=False,
                marker = {
                    'size': [200*marker_size2/np.power(y2.shape[0],1/2)] * y1.shape[0],
                    'line_color':'rgba(0,0,0,0.3)', 'cauto':True,
                    'color': customdata[0].real*0, 'cmin':0, 
                },
            ),
            layout = {'title': 'Field distribution', 'title_font_size': 30,
                    'xaxis': {'scaleanchor':'y','title':'x', 'title_font_size': 25},
                    'yaxis': {'title':'y', 'title_font_size': 25},
                    'height': 600, 'width': 600,
            }
        )
    else:
        field = go.Figure(
            data = go.Scatter3d(
                x=x2, y=y2, z=z2, mode='markers', customdata = np.ones(x2.shape[0]),
                hovertemplate='%{marker.color:.2f}', showlegend=False,
                marker = {
                    'size': [120*marker_size2/np.power(y2.shape[0],1/3)] * y1.shape[0],
                    'line_color':'rgba(0,0,0,0.3)', 'cauto':True,
                    'color': customdata[0].real*0, 'cmin':0, 
                },
            ),
            layout = {'title': 'Field distribution', 'title_font_size': 30,
                  'scene':{'xaxis':{'range':(y2.min()-0.5, y2.max()+0.5),'title':'x', 'title_font_size': 25},
                           'yaxis':{'range':(y2.min()-0.5, y2.max()+0.5),'title':'y', 'title_font_size': 25},
                           'zaxis':{'range':(y2.min()-0.5, y2.max()+0.5),'title':'z', 'title_font_size': 25}},         
                  'height': 600, 'width': 600,
            }
        )
        
    
   
    app = dash.Dash(__name__)
    app.layout = html.Div(children=[

        html.H1("Interactive Band Structure Diagram for TB Model"),
        html.Div([
            dcc.Graph(id='subplot1', figure=band),
            dcc.Graph(id='subplot2', figure=field),
        ], style={'display': 'flex'}),
        html.Div([
            html.Label('Colorscale:'),
            dcc.Dropdown(
                options=[{'label': i, 'value': i} for i in ['hot', 'Rainbow', 'PuOr', 'Blues', 'Reds','Purples','RdBu']],
                value='RdBu',  
                id='colorscale-dropdown',
                style={'margin-left': '10px','margin-right': '30px', 'min-width': '200px'}
            ),
            html.Label('Data:'),
            dcc.Dropdown(
                options=[{'label': i, 'value': i} for i in ["normE", "Ez"]],
                value="Ez", 
                id='normE-Ez-dropdown',
                style={'margin-left': '10px','margin-right': '30px', 'min-width': '200px'}
            ), 
            html.Button(
                'pin', id='pin_button', n_clicks=0,
                style={'margin-left': '200px', 'min-width': '120px','fontSize': '100%',
                       'backgroundColor': 'rgb(30, 112, 33)', 'color':'rgb(255,255,255)',
                       'cursor': 'pointer','borderRadius': '5px',
            },),
            html.Button(
                'clear all', id='clear_button', n_clicks=0,
                style={'margin-left': '50px', 'min-width': '150px','fontSize': '100%',
                       'backgroundColor': 'rgb(148, 36, 26)', 'color':'rgb(255,255,255)',
                       'cursor': 'pointer','borderRadius': '5px',
            },),
        ], style={'display': 'flex', 'fontSize': '150%'} ),
        html.Div(children=[],id='pinned_graphs',
                 style={'scale':'60%','display': 'grid', 
                        'gridTemplateColumns': 'repeat(4, 1fr)','height': '80vh','width': '20vh'}),   
    ], style={'margin-left': '100px', 'margin-top': '50px'})


    # 定义回调函数，点击band更新field
    # 定义回调函数，更新颜色映射和场分布形式
    @app.callback(
        Output('subplot2', 'figure'),
        Output('subplot1', 'figure'),
        Input('subplot1', 'clickData'),  # 监听点击事件
        Input('colorscale-dropdown', 'value'),
        Input('normE-Ez-dropdown', 'value'),
    )

    def update_graph(clickData, colorscale, selected_data):     #, current_band 
        field.data[0].marker.colorscale = colorscale
        if clickData:
            point_index = clickData['points'][0]['pointIndex']
            # 更新subplot2的title
            new_title = f"Field x={x1[point_index]:.2f}, y={y1[point_index]:.2f}"
            field.update_layout(title=new_title)
            # 获取点击点的customdata
            custom_val = customdata[point_index]
            # 更新subplot2
            if selected_data == 'Ez':
                field.data[0].marker.color = custom_val.real
                field.data[0].marker.update({'cmin':None, 'cmax':None, 'cmid':0})
            elif selected_data == 'normE':
                field.data[0].marker.color = np.abs(custom_val)
                field.data[0].marker.update({'cmin':0, 'cmax':None, 'cmid':None})
            # 根据选中的点更新subplot1的颜色
            color_array = ['lightblue'] * len(x1)
            size_array = [10*marker_size1] * len(x1)
            color_array[point_index] = 'rgba(0,0,0,0.7)' 
            size_array[point_index] = 20
            band.data[0].marker.color = color_array
            band.data[0].marker.size = size_array
        # 恢复布局状态
        #band.update_layout(current_band.get('layout'))   # 减慢相应速度
        field.update_layout(title_font_size=30)
        return field, band
    

    # 定义回调函数，pin将当前场分布在下方保持显示，clear all清空下方图片
    @app.callback(
        Output('pinned_graphs', 'children'),
        Output('clear_button', 'n_clicks'),
        Input('pin_button', 'n_clicks'),
        Input('clear_button', 'n_clicks'),
        State('pinned_graphs', 'children'),
        State('subplot2', 'figure'),
    )
    def update_pinned_graph(pin_button, clear_button,  pinned_graphs, field):
        if pin_button:
            pinned_graphs.append(dcc.Graph(id=str(pin_button), figure=field))
        if clear_button:
            pinned_graphs = []
            clear_button = 0
        return pinned_graphs, clear_button


    app.run_server(debug=True, port=port, jupyter_mode="external")
    print('http://127.0.0.1:{:d}'.format(port))

    return app




