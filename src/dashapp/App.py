from dash import Dash
import dash
from pages.public.data import *
import matplotlib.pyplot as plt

plt.legend

app = Dash(__name__, use_pages=True, external_stylesheets=[BS])

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("General", href="/config"),
                dbc.DropdownMenuItem("Map", href="/map"),
            ],
            nav=True,
            in_navbar=True,
            label="Configuration",
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Infection", href="/comparison_infection"),
                # dbc.DropdownMenuItem("Evacuation", href="/comparison_evacuation"),
                # dbc.DropdownMenuItem("Location", href="/comparison_geo"),
                dbc.DropdownMenuItem("Log", href="/comparison_log"),
            ],
            nav=True,
            in_navbar=True,
            label="Simulation Analysis",
        ),
        dbc.NavItem(dbc.NavLink("Upload", href="/upload")),
    ],
    brand="Simulator Dashboard",
    brand_href="/",
    color="dark",
    dark=True,
)

navIncluded = html.Div(
    [
        dbc.Row(
            dbc.Col(html.Div([navbar])),
        )
    ]
)

app.layout = html.Div([
    navIncluded, dash.page_container,
]
)

if __name__ == '__main__':
    app.run_server(debug=True)
