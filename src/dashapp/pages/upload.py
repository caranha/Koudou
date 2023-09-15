import time
import dash
from dash import dcc, html, callback, State, Input, Output
from .public.css import *
from dash.dependencies import Input, Output, State
from .public.utils import *
import dash_bootstrap_components as dbc
from .public.File_Factory import *

dash.register_page(__name__)

layout = html.Div([
    html.Br(),
    html.Div(style=style_offcanvas, children=[
        dbc.Button("Instructions", id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas(
            html.P(
                "In this module, you can upload up to three model result sets, the results will be shown in the"
                " comparison module. Based on the analytical components developed in the simulation analysis module,"
                "we will review and compare them based on the data upload."
            ),
            id="offcanvas",
            title="How Upload Works",
            is_open=False,
        ),
    ]),

    html.P("Uploaded Files: infection_transition.csv, evac_refused_entry.csv, log.txt, ", style=style_offcanvas),
    html.Br(),
    html.Div("Upload Model One", style=style_title),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style=style_upload_bottom,
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    html.Hr(style=style_data_align_3),
    html.Div("Upload Model Two", style=style_title),
    dcc.Upload(
        id='upload-data-model-two',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style=style_upload_bottom,
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload-model-two'),
    html.Hr(style=style_data_align_3),
    html.Div("Upload Model Three", style=style_title),
    dcc.Upload(
        id='upload-data-model-three',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style=style_upload_bottom,
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload-model-three'),
])


@callback(Output('output-data-upload', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified'))
def update_output_model_one(list_of_contents, list_of_names, list_of_dates):
    f = ModelOne()
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d, f) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@callback(Output('output-data-upload-model-two', 'children'),
          Input('upload-data-model-two', 'contents'),
          State('upload-data-model-two', 'filename'),
          State('upload-data-model-two', 'last_modified'))
def update_output_model_two(list_of_contents, list_of_names, list_of_dates):
    f = ModelTwo()
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d, f) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(Output('output-data-upload-model-three', 'children'),
          Input('upload-data-model-three', 'contents'),
          State('upload-data-model-three', 'filename'),
          State('upload-data-model-three', 'last_modified'))
def update_output_model_three(list_of_contents, list_of_names, list_of_dates):
    f = ModelThree()
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d, f) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
