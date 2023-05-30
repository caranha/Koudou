import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .public.css import *
import os

markdown_text = open(os.getcwd() + './data/home/markdown_files/introduction.txt', encoding='utf-8').read()

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(children=[
                    html.Img(src=dash.get_asset_url('covid simulator.png'), style=style_front_img),
                ]),
                html.H3(style=style_title, id='datetime-text'),
                dcc.Interval(
                    id='datetime',
                    interval=20 * 1000,
                    n_intervals=0
                ),
                dcc.Markdown(style=style_mkd, children=markdown_text),
            ]
        )
    ]
)
dash.register_page(__name__, path='/')

