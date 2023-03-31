import plotly.graph_objects as go
import io
import base64
import pandas as pd
from dash import html, dash_table
import numpy as np
import parameters.default as defaultParam
from src.util.time_stamp import TimeStamp
from collections import Counter
import plotly.express as px
from .css import *
import time
import math
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import xml.etree.ElementTree as xee
import os


# ---------------- global ------------------
def timestamp_converter(timestamp):
    ts = TimeStamp(timestamp)
    time = '[' + str(ts.get_week()) + ' week ' + str(ts.get_day_of_week()) + ' days ' + str(ts.get_hour_min_str()) \
           + ':' + str(ts.get_second()) + ']'
    return time


def df_timestamp_converter(df):
    df.index = range(len(df))
    for i in range(len(df)):
        df.loc[i, 'time_stamp'] = timestamp_converter(df.loc[i, 'time_stamp'])
    return df

# To make the time-series shorter for the efficiency to draw line chart
def preprocess_linear_data(df):
    temp_list = []
    for i in range(0, len(df), 10):
        temp_list.append(i)
    new_df = df.iloc[temp_list]
    new_df.index = range(len(new_df))
    return new_df

# ---------------- config ------------------
def table_generator(target_dataframe):
    column_list = []
    for item in target_dataframe.columns:
        column_list.append(target_dataframe[item])
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(target_dataframe.columns),  # 表头取值是data列属性
                        fill_color='paleturquoise',  # 填充色和文本位置
                        align='left'),
            cells=dict(values=column_list,  # 单元格的取值就是每个列属性的Series取值
                       fill_color='lavender',
                       align='left'
                       )
        )]
    )
    return fig


def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


# ---------------- map ------------------
def build_option_list(tsukuba_map):
    return tsukuba_map['type'].unique().tolist()


def count_business_number(filter_list, filer_df):
    dict_result = {}
    for item in filter_list:
        target_len = len(filer_df.loc[filer_df['type'] == item])
        dict_result[item] = target_len
    return dict_result


def build_map_data_table():
    pass


# ---------------- infection ------------------
def single_fact_calculator(df_disease_transition, current_state, next_state):
    list = []
    for i in range(len(df_disease_transition)):
        if df_disease_transition.loc[i, 'current_state'] == current_state and df_disease_transition.loc[
            i, 'next_state'] == next_state:
            ts_end = df_disease_transition.loc[i, 'time_stamp']
            agent_id = df_disease_transition.loc[i, 'agent_id']
            ts_temp = 0
            for j in range(i + 1):
                if df_disease_transition.loc[i - j, 'agent_id'] == agent_id and df_disease_transition.loc[
                    i - j, 'next_state'] == current_state:
                    ts_temp = df_disease_transition.loc[i - j, 'time_stamp']
                    break
            if ts_temp == 0:
                pass
            else:
                ts_start = ts_temp
                ts_diff = ts_end - ts_start
                list.append(ts_diff)
    p = np.mean(list)
    return p


def calculate_facts(df_new_infection, df_disease_transition):
    p1 = np.mean(df_new_infection['time_stamp'])

    list_p2 = []
    for i in range(len(df_disease_transition)):
        if df_disease_transition.loc[i, 'current_state'] == 'exposed' and df_disease_transition.loc[
            i, 'next_state'] == 'asymptomatic':
            ts_end = df_disease_transition.loc[i, 'time_stamp']
            agent_id = df_disease_transition.loc[i, 'agent_id']
            ts_start = df_new_infection.loc[df_new_infection['agent_id'] == agent_id].iloc[0, 0]
            ts_diff = ts_end - ts_start
            list_p2.append(ts_diff)
    p2 = np.mean(list_p2)

    p3 = single_fact_calculator(df_disease_transition, 'asymptomatic', 'symptomatic')
    p4 = single_fact_calculator(df_disease_transition, 'asymptomatic', 'recovered')
    p5 = single_fact_calculator(df_disease_transition, 'symptomatic', 'recovered')
    p6 = single_fact_calculator(df_disease_transition, 'symptomatic', 'severe')
    p7 = single_fact_calculator(df_disease_transition, 'severe', 'recovered')

    p8_1 = list(set(df_disease_transition['agent_id']))
    p8_2 = list(set(df_new_infection['agent_id']))
    p8_3 = p8_1 + p8_2
    p8_len = len(list(set(p8_3)))
    total_agents = defaultParam.parameters.get("N_AGENTS")
    p8 = (total_agents - p8_len) / total_agents * 100

    p9 = 0
    l9 = []
    for i in range(len(df_disease_transition)):
        if df_disease_transition.loc[i, 'current_state'] == 'recovered':
            p9 = p9 + 1
            agent_id = df_disease_transition.loc[i, 'agent_id']
            l9.append(agent_id)

    list_location = []
    for i in range(len(df_disease_transition)):
        if df_disease_transition.loc[i, 'current_state'] == 'exposed' and df_disease_transition.loc[
            i, 'next_state'] == 'asymptomatic':
            list_location.append(df_disease_transition.loc[i, 'agent_location'])
    result_counter1 = Counter(list_location)

    list_location = []
    for i in range(len(df_disease_transition)):
        if df_disease_transition.loc[i, 'current_state'] == 'asymptomatic' and df_disease_transition.loc[
            i, 'next_state'] == 'symptomatic':
            list_location.append(df_disease_transition.loc[i, 'agent_location'])
    result_counter2 = Counter(list_location)

    return p1, p2, p3, p4, p5, p6, p7, p8, total_agents, p9, l9, result_counter1, result_counter2


def build_infection_agent_list(new_infection):
    return new_infection['agent_id'].unique().tolist()


def agent_id_filter(data_df, agent_id):
    return data_df.loc[data_df['agent_id'] == agent_id]


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def join_search_profession(profession, file_name, df_new_infection, df_activity_history, df_disease_transition):
    if file_name == 'New Infection':
        if profession == 'University Student':
            result_df = df_new_infection[df_new_infection['agent_profession'] == 'university_student']
        elif profession == 'All':
            result_df = df_new_infection
        else:
            result_df = df_new_infection[df_new_infection['agent_profession'] == 'student']
    elif file_name == 'Activity History':
        if profession == 'University Student':
            result_df = df_activity_history[df_activity_history['profession'] == 'university_student']
        elif profession == 'All':
            result_df = df_activity_history
        else:
            result_df = df_activity_history[df_activity_history['profession'] == 'student']
    else:
        if profession == 'University Student':
            result_df = df_disease_transition[df_disease_transition['agent_profession'] == 'university_student']
        elif profession == 'All':
            result_df = df_disease_transition
        else:
            result_df = df_disease_transition[df_disease_transition['agent_profession'] == 'student']
    return result_df


def text_color():
    pass


def get_data_by_interval(start, end, df):
    df = df.loc[(df['time_stamp'] >= start) & (df['time_stamp'] <= end)]
    return df


# ---------------- evacuation ------------------
def find_single_agent_path():
    pass


# ---------------- location ------------------
def location_divider(df_agent_position_summary):
    list_locations = []
    unique_location_list = df_agent_position_summary['location'].unique()

    for location in unique_location_list:
        this_location_list = df_agent_position_summary.loc[df_agent_position_summary['location'] == location]
        list_locations.append(this_location_list)

    df_comp = location_df_processor(list_locations)
    return df_comp


def location_df_processor(position_list):
    init_df = position_list[0]
    init_df.drop(['location'], axis=1)
    init_df.rename(columns={'count': 'home'})
    for df in position_list:
        pass
    return position_list


def proportion_calculation(df):
    result_dict = {}
    timestamp_length = int(df.loc[len(df) - 1, 'time_stamp']) / 5
    unique_location_list = df['location'].unique()
    for location in unique_location_list:
        single_location_df = df.loc[df['location'] == location]
        mean_count = np.sum(single_location_df['count']) / timestamp_length
        result_dict[location] = round(mean_count, 2)

    return result_dict


def exits_in_df(df, lat, lon):
    for i in range(len(df)):
        if df.loc[i, 'centroid_lat']==lat and df.loc[i, 'centroid_lon']==lon:
            df.loc[i, 'infection_num'] += 1
            return True
    return False


def infection_heatmap(df_new_infection, domTree):
    df_new_infection = df_new_infection.drop(['time', 'disease_name', 'agent_profession', 'source_profession', 'type',
                                              'source_location', 'source_id', 'current_mask', 'next_mask'], axis=1)
    df = pd.DataFrame(columns=['centroid_lat', 'centroid_lon', 'infection_num', 'business'], dtype=float)
    list_node = []
    for node in domTree.getroot().iter('node'):
        list_node.append(node.attrib)

    for i in range(len(df_new_infection)):
        temp_id = df_new_infection.loc[i, 'agent_node_id'].split('_')[0]
        for j in range(len(list_node)):
            if list_node[j]['id'] == temp_id:
                lat = list_node[j]['lat']
                lon = list_node[j]['lon']
                if exits_in_df(df, lat, lon):
                    break
                else:
                    # insert
                    df.loc[len(df.index)] = [lat, lon, 1, df_new_infection.loc[i, 'agent_location']]
                    break

    for i in range(len(df)):
        df.loc[i, 'centroid_lat'] = float(df.loc[i, 'centroid_lat'])
        df.loc[i, 'centroid_lon'] = float(df.loc[i, 'centroid_lon'])

    dic = {}
    for i in range(len(df)):
        if df.loc[i, 'business'] in dic.keys():
            dic[df.loc[i, 'business']] = dic[df.loc[i, 'business']] + df.loc[i, 'infection_num']
        else:
            dic[df.loc[i, 'business']] = df.loc[i, 'infection_num']

    px.set_mapbox_access_token(
        'pk.eyJ1Ijoic2ppYW5nMjMiLCJhIjoiY2xlb3Jid2c0MDU0NTNybnZlc3Rrb2J0ayJ9.Kc5kX7FNpk4MJODTFNS-BA')
    fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon", color="infection_num", size="infection_num",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=50, zoom=10)
    fig.update_layout(
        height=600,
        showlegend=True,
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0),
    )
    return fig


# ---------------- upload ------------------
def parse_contents(contents, filename, date, f):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            if 'activity_history.' in filename:
                f.activity_history = df
            elif 'agent_position_summary.' in filename:
                f.agent_position_summary = df
            elif 'disease_transition.' in filename:
                f.disease_transition = df
            elif 'evacuation.' in filename:
                f.evacuation = df
            elif 'infection_summary' in filename:
                f.infection_summary = df
            elif 'infection_transition.' in filename:
                f.infection_transition = df
            elif 'new_infection.' in filename:
                f.new_infection = df
            elif 'evac_refused_entry.' in filename:
                f.evac_refused_entry = df
            elif 'mask_summary.' in filename:
                f.mask_summary = df
            elif 'symptom' in filename:
                f.symptom = df
            else:
                return html.Div(['CSV file is not found .'])
        elif 'txt' in filename:
            # Assume that the user uploaded an excel file
            log_data_lines = str(decoded).split('\\n')
            html_list = []
            for i in range(len(log_data_lines)):
                html_list.append(html.H5(log_data_lines[i]))
            f.log = html_list
    except Exception as e:
        return html.Div([
            'There was an error processing this file, please refer to terminal.'
        ])
    return html.Div([
        html.H5('[File Processing ' + time.ctime() + ']: ' + filename + ' is uploaded successfully!',
                style=style_title)
    ])


# ---------------- comparison location ------------------
def table_return_html(counts_dict):
    proportion_list = []
    counts_sum = np.sum(list(counts_dict.values()))
    for value in list(counts_dict.values()):
        proportion_list.append(str(format((value / counts_sum * 100), '.3f')) + '%')
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
        height=300,
        showlegend=True,
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0),
    )
    return fig


def pie_return_html(counts_dict):
    counts_pd = pd.DataFrame({
        'location': counts_dict.keys(),
        'counts': counts_dict.values()
    })
    fig = px.pie(counts_pd, names="location", values="counts",
                 # 不同颜色：RdBu、Peach
                 color_discrete_sequence=px.colors.sequential.Peach  # 只需要改变最后的RdBu即可
                 )
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'cyan']
    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='value',
        textfont_size=10,
        marker=dict(colors=colors,
                    line=dict(color='#000000', width=2)))
    fig.update_layout(
        height=300,
        # width=80,
        showlegend=True,
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0),  # pad参数是刻度与标签的距离
    )
    return fig


def bar_return_html(counts_dict):
    x = list(counts_dict.keys())
    y = list(counts_dict.values())

    # Use the hovertext kw argument for hover text
    fig = go.Figure(data=[go.Bar(x=x, y=y,
                                 hovertext=list(counts_dict.keys()))])
    # Customize aspect
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5, opacity=0.6)
    fig.update_layout(
        height=300,
        # width=80,
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0),  # pad参数是刻度与标签的距离
    )
    return fig



# ---------------- comparison infection ------------------
def facts_return_html(model):
    df_new_infection = model.new_infection
    df_disease_transition = model.disease_transition
    p1, p2, p3, p4, p5, p6, p7, p8, total_agents, p9, l9, l10, l11 = calculate_facts(df_new_infection, df_disease_transition)
    return html.Div(style=style_data_align_4, children=[
        dbc.Badge("Parameter 1", className="ms-1"),
        html.H5("Avg time when first get exposed:"),
        html.H5(timestamp_converter(math.floor(p1))),
        dbc.Badge("Parameter 2", className="ms-1"),
        html.H5(" Avg time from exposed to asymptomatic: "),
        html.H5(timestamp_converter(math.floor(p2))),
        dbc.Badge("Parameter 3", className="ms-1"),
        html.H5("Avg time from asymptomatic to symptomatic:"),
        html.H5(timestamp_converter(math.floor(p3))),
        dbc.Badge("Parameter 4", className="ms-1"),
        html.H5("Avg time from asymptomatic to recovered:"),
        html.H5(timestamp_converter(math.floor(p4))),
        dbc.Badge("Parameter 5", className="ms-1"),
        html.H5("Avg time from symptomatic to recovered:"),
        html.H5(timestamp_converter(math.floor(p5))),
        dbc.Badge("Parameter 6", className="ms-1"),
        html.H5("Avg time from symptomatic to severe: "),
        html.H5(timestamp_converter(math.floor(p6))),
        dbc.Badge("Parameter 7", className="ms-1"),
        html.H5("Avg time from severe to recovered: "),
        html.H5(timestamp_converter(math.floor(p7))),
        dbc.Badge("Parameter 8", className="ms-1"),
        html.H5("Percentage of agents (" + str(total_agents) +
                " agents in total) never get infected in this life cycle: " + str(p8) + "%"),
        dbc.Badge("Parameter 9", className="ms-1"),
        html.H5("List and number of agent that get infected multiples times:"),
        html.H5(str(p9) + ' agent(s) got infected multiples times, and they are ' + str(l9)),
        dbc.Badge("Parameter 10", className="ms-1"),
        html.H5("Most frequent locations that make agents transfer from exposed to asymptomatic: "),
        html.H5("The locations are lists by their frequency from high to low: "),
        html.H5(str(l10)),
        dbc.Badge("Parameter 11", className="ms-1"),
        html.H5("Most frequent locations that make agents transfer from asymptomatic to symptomatic: "),
        html.H5("The locations are lists by their frequency from high to low: "),
        html.H5(str(l11)),
    ])

def IA_return_random_new_infection_figure(model, n_clicks):
    df_new_infection = model.new_infection
    infection_agent_id_list = build_infection_agent_list(df_new_infection)
    # initiate and show the first id
    random_id = infection_agent_id_list[0]
    if n_clicks:
        id_list = infection_agent_id_list
        which = n_clicks % len(id_list)
        random_id = id_list[which]
        # random_id = infection_agent_id_list[random.randint(0, len(infection_agent_id_list)-1)]

    agent_pd = agent_id_filter(df_new_infection, random_id)

    agent_pd = df_timestamp_converter(agent_pd)
    column_name_values = ['Agent ID', 'Time Stamp', 'Type', 'Disease', 'Profession',
                          'Location', 'Source Profession', 'Source Location']
    column_name_list = ['agent_id', 'time_stamp', 'type', 'disease_name', 'agent_profession',
                        'agent_location', 'source_profession', 'source_location']

    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}]]
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=column_name_values,
                font=dict(size=12),
                align="left"
            ),
            cells=dict(
                values=[agent_pd[k].tolist() for k in column_name_list],
                align="left")
        ),
        row=1, col=1
    )
    fig.update_layout(
        height=120,
        # width=80,
        showlegend=False,
        margin=go.layout.Margin(l=0, r=0, b=0, t=5, pad=0),  # pad参数是刻度与标签的距离
    )

    return fig


def IA_return_random_activity_history_list(model, random_id):
    df_disease_transition = model.disease_transition
    df_activity_history = model.activity_history
    df_new_infection = model.new_infection
    infection_agent_id_list = build_infection_agent_list(df_new_infection)
    component_list = [
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H5("Sample List [Time Stamp]: [Disease Name] Infection State", className="mb-1"),
                        html.Small("Infection Transition: [Current State] -> [Next State]", className="text-success"),
                    ],
                    className="d-flex w-100 justify-content-between",
                ),
                html.P("Agent Location at [Location]", className="mb-1"),
                html.Div(
                    [
                        html.Small("At [Time Stamp], the agent [Agent ID] [Activity] at [Location].",
                                   className="text-muted"),
                        html.Br(),
                        html.Small("Finish activities at this infection state period.", className="text-muted"),
                    ]
                )
            ]
        ),
    ]

    if random_id == "":
        disease_transition_pd = agent_id_filter(df_disease_transition, infection_agent_id_list[0])
        activity_history_pd = agent_id_filter(df_activity_history, infection_agent_id_list[0])
    else:
        disease_transition_pd = agent_id_filter(df_disease_transition, random_id)
        activity_history_pd = agent_id_filter(df_activity_history, random_id)

    time_stamp_list = disease_transition_pd['time_stamp'].tolist()
    current_state_list = disease_transition_pd['current_state'].tolist()
    next_state_list = disease_transition_pd['next_state'].tolist()
    disease_list = disease_transition_pd['disease_name'].tolist()
    location_list = disease_transition_pd['agent_location'].tolist()

    for i in range(len(time_stamp_list) - 1):
        table = get_data_by_interval(time_stamp_list[i], time_stamp_list[i + 1], activity_history_pd)
        agent_activity_html_list = []
        for j in range(len(table)):
            behavioral_sentence = "At " + timestamp_converter(table.iloc[j, 0]) + ", the agent " + \
                                  str(table.iloc[j, 1]) + " " + str(table.iloc[j, 7]) + ', the location is ' \
                                  + table.iloc[j, 3] + '.'
            agent_activity_html_list.append(
                html.Small(behavioral_sentence, className="text-muted"),
            )
            agent_activity_html_list.append(
                html.Br(),
            )

        agent_activity_html_list.append(
            html.Small("Finish activities at this infection state period.", className="text-muted")
        )

        component_list.append(
            dbc.ListGroupItem(
                [
                    html.Div(
                        [
                            html.H5(
                                timestamp_converter(time_stamp_list[i]) + ": " + disease_list[i] + " Infection State",
                                className="mb-1"),
                            html.Small("Infection Transition: " + current_state_list[i] + " -> " + next_state_list[i],
                                       className="text-success"),
                        ],
                        className="d-flex w-100 justify-content-between",
                    ),
                    html.P("Agent Location when infection state changes is " + location_list[i], className="mb-1"),
                    html.Div(children=agent_activity_html_list)
                ]
            ),
        )

    # Add tracking information for the last state.
    table = activity_history_pd.loc[(activity_history_pd['time_stamp'] >= time_stamp_list[len(time_stamp_list) - 1])]
    agent_activity_html_list = []
    for j in range(len(table)):
        behavioral_sentence = "At " + timestamp_converter(table.iloc[j, 0]) + ", the agent " + \
                              str(table.iloc[j, 1]) + " " + str(table.iloc[j, 7]) + ', the location is ' \
                              + table.iloc[j, 3] + '.'

        agent_activity_html_list.append(
            html.Small(behavioral_sentence, className="text-muted"),
        )
        agent_activity_html_list.append(
            html.Br(),
        )

    agent_activity_html_list.append(
        html.Small("Finish activities at this infection state period.", className="text-muted")
    )

    component_list.append(
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H5(timestamp_converter(time_stamp_list[len(time_stamp_list) - 1]) + ": " +
                                disease_list[len(time_stamp_list) - 1] + " Infection State", className="mb-1"),
                        html.Small("Infection Transition: " + current_state_list[len(time_stamp_list) - 1] + " -> "
                                   + next_state_list[len(time_stamp_list) - 1], className="text-success"),
                    ],
                    className="d-flex w-100 justify-content-between",
                ),
                html.P("Agent Location when infection state changes is " + location_list[len(time_stamp_list) - 1],
                       className="mb-1"),
                html.Div(children=agent_activity_html_list)
            ]
        ),
    )
    return dbc.ListGroup(component_list)


def IA_return_random_activity_history_table(model, random_id):
    df_new_infection = model.new_infection
    df_activity_history = model.activity_history
    infection_agent_id_list = build_infection_agent_list(df_new_infection)
    if random_id == "":
        agent_pd = agent_id_filter(df_activity_history, infection_agent_id_list[0])
    else:
        agent_pd = agent_id_filter(df_activity_history, random_id)

    agent_pd = df_timestamp_converter(agent_pd)
    column_name_values = [
        'Time Stamp', 'Profession', 'Location', 'Household ID', 'Activity Name'
    ]
    column_name_list = [
        'time_stamp', 'profession', 'location', 'household_id', 'activy_name'
    ]

    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}]]
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=column_name_values,
                font=dict(size=12),
                align="left"
            ),
            cells=dict(
                values=[agent_pd[k].tolist() for k in column_name_list],
                align="left")
        ),
        row=1, col=1
    )
    fig.update_layout(
        height=300,
        # width=80,
        showlegend=False,
        margin=go.layout.Margin(l=0, r=0, b=0, t=5, pad=0),  # pad参数是刻度与标签的距离
    )
    return fig


def IA_return_random_disease_transition_table(model, random_id):
    df_new_infection = model.new_infection
    df_disease_transition = model.disease_transition
    infection_agent_id_list = build_infection_agent_list(df_new_infection)
    if random_id == "":
        agent_pd = agent_id_filter(df_disease_transition, infection_agent_id_list[0])
    else:
        agent_pd = agent_id_filter(df_disease_transition, random_id)

    agent_pd = df_timestamp_converter(agent_pd)
    column_name_values = ['Time Stamp', 'Disease', 'Profession', 'Location',
                          'Current State', 'Next State']
    column_name_list = ['time_stamp', 'disease_name', 'agent_profession', 'agent_location',
                        'current_state', 'next_state']

    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}]]
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=column_name_values,
                font=dict(size=12),
                align="left"
            ),
            cells=dict(
                values=[agent_pd[k].tolist() for k in column_name_list],
                align="left")
        ),
        row=1, col=1
    )
    fig.update_layout(
        height=140,
        # width=80,
        showlegend=False,
        margin=go.layout.Margin(l=0, r=0, b=0, t=5, pad=0),  # pad参数是刻度与标签的距离
    )
    return fig

def IA_random_agent_infection(model, n_clicks):
    df_new_infection = model.new_infection
    infection_agent_id_list = build_infection_agent_list(df_new_infection)
    if n_clicks:
        id_list = infection_agent_id_list
        which = n_clicks % len(id_list)
        return id_list[which]
    else:
        return ""
