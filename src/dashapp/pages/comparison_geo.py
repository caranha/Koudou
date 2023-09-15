import dash
import pandas
from dash import html, dcc, callback, Input, Output
from .public.utils import *
from .public.File_Factory import *
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function

dash.register_page(__name__, path='/comparison_geo')

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            # html.P("Comparison based on agent position summary", className="card-text"),
            # dbc.Button("Link to there", color="success", href='/geographical'),
            # html.Hr(),
            html.Div(
                style=style_data_align_4,
                children=[
                    dbc.Badge(
                        "Figures",
                        color="white",
                        text_color="warning",
                        className="border me-1",
                        style=style_fontSize20
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                className='container-fluid',
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model One"),
                                html.Div(id='count-proportion-pie-model-one'),
                                html.Br(),
                                html.Div(id='count-proportion-bar-model-one')
                            ]),
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model Two"),
                                html.Div(id='count-proportion-pie-model-two'),
                                html.Br(),
                                html.Div(id='count-proportion-bar-model-two')
                            ]),
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model Three"),
                                html.Div(id='count-proportion-pie-model-three'),
                                html.Br(),
                                html.Div(id='count-proportion-bar-model-three')
                            ])
                        ]
                    ),
                ]
            ),
            html.Hr(),
            html.Div(
                style=style_data_align_4,
                children=[
                    dbc.Badge(
                        "Tables",
                        color="white",
                        text_color="warning",
                        className="border me-1",
                        style=style_fontSize20
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                className='container-fluid',
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model One", id="random-input-model-one"),
                                html.Div(id='count-proportion-table-model-one'),
                            ]),
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model Two", id="random-input-model-two"),
                                html.Div(id='count-proportion-table-model-two'),
                            ]),
                            html.Div(className='col-sm-4', children=[
                                html.H5("Model Three", id="random-input-model-three"),
                                html.Div(id='count-proportion-table-model-three'),
                            ])
                        ]
                    ),
                ]
            ),
        ]
    ),
    className="mt-3",
)


IHM_tab1_content = dbc.Card(
    dbc.CardBody([
        html.H5("Drag the slider to change the time range:"),
        html.Br(),
        dcc.RangeSlider(0, 10, value=[0, 2], allowCross=False,
                        marks={i: str(i)+'day' for i in range(10)},
                        id='range-slider-ihm',
                        tooltip={"placement": "bottom", "always_visible": True}),
        html.Div(id='range-slider-text-output'),
        html.Div(id='infection-heat-map-one')
    ]),
    className="mt-3",
)

IHM_tab2_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='infection-heat-map-two')
    ]),
    className="mt-3",
)

IHM_tab3_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='infection-heat-map-three')
    ]),
    className="mt-3",
)

TM_tab1_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='transmit-map-one')
    ]),
    className="mt-3",
)

TM_tab2_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='transmit-map-two')
    ]),
    className="mt-3",
)

TM_tab3_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='transmit-map-three')
    ]),
    className="mt-3",
)

LB_tab1_content = dbc.Card(
    dbc.CardBody([
        html.H5("Test the map", id='lb-random-input-one'),
        html.Div(id='lb-map-one')
    ]),
    className="mt-3",
)


tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                style=style_data_align_4,
                children=[
                    dbc.Badge(
                        "Heat Map",
                        color="white",
                        text_color="warning",
                        className="border me-1",
                        style=style_fontSize20
                    ),
                ]
            ),
            html.Br(),
            html.P("Heat map for infection taken place", className="card-text"),
            dbc.Tabs(
                [
                    dbc.Tab(IHM_tab1_content, label="Model One"),
                    dbc.Tab(IHM_tab2_content, label="Model Two", id='im-random-input-two'),
                    dbc.Tab(IHM_tab3_content, label="Model Three", id='im-random-input-three'),
                ], style={'marginTop': '5px'}
            )
        ]
    ),
    className="mt-3",
)


tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                style=style_data_align_4,
                children=[
                    dbc.Badge(
                        "Route Tracking",
                        color="white",
                        text_color="warning",
                        className="border me-1",
                        style=style_fontSize20
                    ),
                ]
            ),
            html.Br(),
            html.P("Map to show how disease is transmitting", className="card-text"),
            dbc.Tabs(
                [
                    dbc.Tab(TM_tab1_content, label="Model One", id='tm-random-input-one'),
                    dbc.Tab(TM_tab2_content, label="Model Two", id='tm-random-input-two'),
                    dbc.Tab(TM_tab3_content, label="Model Three", id='tm-random-input-three'),
                ], style={'marginTop': '5px'}
            )
        ]
    ),
    className="mt-3",
)


tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                style=style_data_align_4,
                children=[
                    dbc.Badge(
                        "Leaflet Map Test",
                        color="white",
                        text_color="warning",
                        className="border me-1",
                        style=style_fontSize20
                    ),
                ]
            ),
            html.Br(),
            html.P("This is for dash leaflet map test", className="card-text"),
            dbc.Tabs(
                [
                    dbc.Tab(LB_tab1_content, label="Model One", id='tm-random-input-one'),
                    # dbc.Tab(LB_tab2_content, label="Model Two", id='tm-random-input-two'),
                    # dbc.Tab(LB_tab3_content, label="Model Three", id='tm-random-input-three'),
                ], style={'marginTop': '5px'}
            )
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Infection Location Statistics"),
        dbc.Tab(tab2_content, label="Infection Map"),
        dbc.Tab(tab3_content, label="Infection Transmission Route"),
        dbc.Tab(tab4_content, label="Leaflet Map Test"),
        dbc.Tab(
            "This tab's content is never seen", label="To be developed", disabled=True
        ),
    ], style={'marginTop': '5px'}
)

layout = html.Div(style=style_data_align_0, children=[
    html.Div(
        children=[
            html.H3("Model Comparison for Location Part", style=style_select_case),
            tabs
        ]
    ),
])


@callback(
    Output('lb-map-one', 'children'),
    Input('lb-random-input-one', 'value'))
def lb_map_one(value):
    # f = ModelOne()
    # df_new_infecion = f.new_infection

    return html.Div(children=[
        dl.Map(
            [
                dl.TileLayer(),
                dl.GeoJSON(data=dlx.dicts_to_geojson([dict(lat=36.103901, lon=140.103707)] * 100), cluster=True),
            ],
            center=(36.103901, 140.103707),
            zoom=15,
            style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}
        )
    ])


@callback(Output('transmit-map-one', 'children'),
          Input('tm-random-input-one', 'value'))
def track_infection_one(value):
    f = ModelOne()
    df_new_infecion = f.new_infection
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')
    trace_fig1, trace_fig2 = compute_fig2(df_new_infecion, domTree)

    return html.Div(children=[
        dcc.Graph(figure=trace_fig1),
        dcc.Graph(figure=trace_fig2)
    ])


@callback(Output('transmit-map-two', 'children'),
          Input('tm-random-input-two', 'value'))
def track_infection_two(value):
    f = ModelTwo()
    df_new_infecion = f.new_infection
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')
    trace_fig1, trace_fig2 = compute_fig2(df_new_infecion, domTree)

    return html.Div(children=[
        dcc.Graph(figure=trace_fig1),
        dcc.Graph(figure=trace_fig2)
    ])


@callback(Output('transmit-map-three', 'children'),
          Input('tm-random-input-three', 'value'))
def track_infection_three(value):
    f = ModelThree()
    df_new_infecion = f.new_infection
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')
    trace_fig1, trace_fig2 = compute_fig2(df_new_infecion, domTree)

    return html.Div(children=[
        dcc.Graph(figure=trace_fig1),
        dcc.Graph(figure=trace_fig2)
    ])


@callback(
    Output('range-slider-text-output', 'children'),
    [Input('range-slider-ihm', 'value')])
def infection_heat_map_one_text(value):
    return 'You have selected days from {} to {}.'.format(value[0], value[1])


@callback(
    Output('infection-heat-map-one', 'children'),
    [Input('range-slider-ihm', 'value')]
)
def infection_heat_map_one(value):
    f = ModelOne()
    df_new_infection = f.new_infection
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')

    # domTree = xee.parse(os.path.join('..\data\map_osm', 'tsukuba_area.xml'))
    heat_fig, dic_table = infection_heatmap(df_new_infection, domTree, value[0], value[1])

    if df_new_infection is pandas.NA:
        return html.H5("Not loaded yet, please upload new_infection.csv to model one.")
    else:
        return html.Div(children=[
            dcc.Graph(figure=dic_table),
            dcc.Graph(figure=heat_fig)
        ])



@callback(
    Output('infection-heat-map-two', 'children'),
    Input('im-random-input-two', 'value')
)
def infection_heat_map_two(value):
    f = ModelTwo()
    df_new_infection = f.new_infection
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')
    # domTree = xee.parse(os.path.join('..\data\map_osm', 'tsukuba_area.xml'))
    heat_fig = infection_heatmap(df_new_infection, domTree)

    if df_new_infection is pandas.NA:
        return html.H5("Not loaded yet, please upload new_infection.csv to model two.")
    else:
        return dcc.Graph(figure=heat_fig)


@callback(
    Output('infection-heat-map-three', 'children'),
    Input('im-random-input-three', 'value')
)
def infection_heat_map_three(value):
    f = ModelThree()
    df_new_infection = f.new_infection
    # domTree = xee.parse(os.path.join('..\data\map_osm', 'tsukuba_area.xml'))
    domTree = xee.parse(r'I:\Epidemicon Research\Post-ALIFE\Koudou\src\dashapp\data\map_osm\tsukuba_area.osm')
    heat_fig = infection_heatmap(df_new_infection, domTree)

    if df_new_infection is pandas.NA:
        return html.H5("Not loaded yet, please upload new_infection.csv to model three.")
    else:
        return dcc.Graph(figure=heat_fig)


@callback(
    Output('count-proportion-bar-model-one', 'children'),
    Input('random-input-model-one', 'value')
)
def bar_return_model_one(value):
    f = ModelOne()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = bar_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)

@callback(
    Output('count-proportion-bar-model-two', 'children'),
    Input('random-input-model-two', 'value')
)
def bar_return_model_two(value):
    f = ModelTwo()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = bar_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)

@callback(
    Output('count-proportion-bar-model-three', 'children'),
    Input('random-input-model-three', 'value')
)
def bar_return_model_three(value):
    f = ModelThree()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = bar_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)

@callback(
    Output('count-proportion-pie-model-one', 'children'),
    Input('random-input-model-one', 'value')
)
def pie_return_model_one(value):
    f = ModelOne()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = pie_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)


@callback(
    Output('count-proportion-pie-model-two', 'children'),
    Input('random-input-model-two', 'value')
)
def pie_return_model_two(value):
    f = ModelTwo()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = pie_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)


@callback(
    Output('count-proportion-pie-model-three', 'children'),
    Input('random-input-model-three', 'value')
)
def pie_return_model_three(value):
    f = ModelThree()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)
    fig = pie_return_html(counts_dict)

    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)


@callback(
    Output('count-proportion-table-model-one', 'children'),
    Input('random-input-model-one', 'value')
)
def table_return_model_one(value):
    f = ModelOne()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)

    fig = table_return_html(counts_dict)
    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model one.")
    else:
        return dcc.Graph(figure=fig)


@callback(
    Output('count-proportion-table-model-two', 'children'),
    Input('random-input-model-two', 'value')
)
def table_return_model_one(value):
    f = ModelTwo()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)

    fig = table_return_html(counts_dict)
    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model two.")
    else:
        return dcc.Graph(figure=fig)


@callback(
    Output('count-proportion-table-model-three', 'children'),
    Input('random-input-model-three', 'value')
)
def table_return_model_three(value):
    f = ModelThree()
    df_agent_position_summary = f.agent_position_summary
    counts_dict = proportion_calculation(df_agent_position_summary)

    fig = table_return_html(counts_dict)
    if df_agent_position_summary is pandas.NA:
        return html.H5("Not loaded yet, please upload agent_position_summary.csv to model three.")
    else:
        return dcc.Graph(figure=fig)
