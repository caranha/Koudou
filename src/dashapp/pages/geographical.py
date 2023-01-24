import dash
import numpy as np
from dash import html, dcc, Input, Output, callback
from .public.css import *
from .public.utils import *
import dash_bootstrap_components as dbc
import pandas as pd
import os
import plotly.express as px

dash.register_page(__name__)

df_agent_position_summary = pd.read_csv(os.getcwd() + './data/simulation_result/agent_position_summary.csv',low_memory=False)
unique_location_list = df_agent_position_summary['location'].unique()
list_locations = location_divider(df_agent_position_summary)
counts_dict = proportion_calculation(df_agent_position_summary)
counts_pd = pd.DataFrame({
    'location': counts_dict.keys(),
    'counts': counts_dict.values()
})
proportion_list = []
counts_sum = np.sum(list(counts_dict.values()))
for value in list(counts_dict.values()):
    proportion_list.append(str(round(value / counts_sum, 5)*100)+'%')

layout = html.Div(style=style_title,
    children=[
        html.Span('Agent Location Analysis', className="badge bg-dark", style=style_badge, id='random-input'),
        # html.Div(style=style_data_align_0, children=[
        #     html.H5("All locations are listed: ", id='random-input'),
        #     html.H5(unique_location_list + ' ')
        # ]),
        html.Span(style=style_fontSize, children=[
            dbc.Badge(
                "Agent Position Summary",
                color="white",
                text_color="danger",
                className="border me-1",
            )
        ]),
        dcc.Graph(style=style_data_align_4, id='count_proportion_pie_chart'),
        dcc.Graph(style=style_data_align_3, id='count_proportion_table'),

    ]
)

@callback(
    Output('count_proportion_table', 'figure'),
    Input('random-input', 'value')
)
def table_return(value):
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Location', 'Average Count', 'Proportion'],
                    line_color='darkslategray',
                    fill_color='lightskyblue',
                    align='center'),
        cells=dict(values=[list(counts_dict.keys()),
                           list(counts_dict.values()),
                           proportion_list],
                   line_color='darkslategray',
                   fill_color='lightcyan',
                   align='center'))
    ])
    fig.update_layout(
        height=400,
        showlegend=True,
        margin=go.layout.Margin(l=0, r=0, b=0, t=15, pad=0),
    )
    return fig


@callback(
    Output('count_proportion_pie_chart', 'figure'),
    Input('random-input', 'value')
)
def pie_chart_return(value):
    fig = px.pie(counts_pd,
                 names="location",
                 values="counts",
                 # Different color: RdBu、Peach
                 color_discrete_sequence=px.colors.sequential.Peach
                 )
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'cyan']
    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='value',
        textfont_size=20,
        marker=dict(colors=colors,
                    line=dict(color='#000000', width=2)))
    fig.update_layout(
        height=300,
        # width=80,
        showlegend=True,
        margin=go.layout.Margin(l=0, r=0, b=0, t=15, pad=0),
    )
    return fig
