import pandas as pd
import dash
from dash import dcc as dcc
from dash import html as html
import plotly.express as px
import plotly.graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State
import datetime

#mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Load the data
df = pd.read_csv(
    "https://raw.githubusercontent.com/max-wittenberg-dbx/dash_app/main/dl_with_preds.csv")

# Rename the population column to sales
df = df.rename(columns={'population': 'sales'})
df = df.rename(columns={'predicted_population': 'predicted_sales'})

# Create the app
app = dash.Dash(__name__)
app.title = "Global Sales by Country"
server = app.server


# Define colors and fonts
colors = {
    'background': '#FFFFFF',
    'text': '#d8d8d8',
    'accent': '#0D0D0D'
}

fonts = {
    'family': 'DM Sans',
    'size': 16,
    'color': colors['text']
}


# Define app layout
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(src='https://datasentics.com/storage/partners/databricks-white-horizontal.png',
                                     style={'height':'75px', 'margin':'1px', 'display': 'inline-block', 'vertical-align': 'left'})
                            ),
                        html.H2("Global Sales by Country App"),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="country-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in df['country']
                                            ],
                                            placeholder="Select a country",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className='div-for-charts',
                                    children=[
                                        dcc.Graph(id="top-10-bar"),
                                    ]
                                )
                            ],
                        )
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        #dcc.Graph(id="top-10-bar"),
                    ],
                ),
            ],
        )
    ]
)
# Define the callback for the map
@app.callback(
    dash.dependencies.Output('map-graph', 'figure'),
    dash.dependencies.Input('country-dropdown', 'value')
)



def update_map(selected_country):
    # Filter the data by the selected country
    if selected_country is None:
        filtered_df = df
        zoom = 1.8
    else:
        filtered_df = df[df['country'] == selected_country]
        zoom = 4.0

    # Create the map figure
    map_fig = px.scatter_mapbox(
        filtered_df, 
        lat='lat', 
        lon='lng', 
        hover_name='city',
        hover_data=['country', 'predicted_sales'],
        color='predicted_sales', 
        size='predicted_sales', 
        color_continuous_scale='Solar',
        zoom=zoom, 
        height=800)
    map_fig.update_layout(mapbox_style="carto-darkmatter")
    map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    map_fig.update_layout(coloraxis_showscale=False)

    return map_fig






# Define the callback for the top 10 bar chart
@app.callback(
    dash.dependencies.Output('top-10-bar', 'figure'),
    dash.dependencies.Input('country-dropdown', 'value')
)
def update_top_10_bar(selected_country):
    # Filter the data by the selected country
    if selected_country is None:
        filtered_df = df
    else:
        filtered_df = df[df['country'] == selected_country]

    # Group the data by city and sum the sales
    grouped_df = filtered_df.groupby('city', as_index=False)['sales'].sum()

    # Sort the data by sales and take the top 10
    sorted_df = grouped_df.sort_values('sales', ascending=False).iloc[:10]

    # Create the bar chart figure
    bar_fig = go.Figure(
        data = [
            go.Bar(
                x=sorted_df['sales'], 
                y=sorted_df['city'],
                orientation='h',
                text=(sorted_df['sales']),
                texttemplate='%{text:.3s}',
                textposition='auto',
                marker=dict(
                    color='rgb(189,43,38)',
                    line=dict(
                        color="rgba(0,0,0,0)"
                    )
                )
            )
        ]
    )
    bar_fig.update_layout(
        title="Top 10 Cities by Sales",
        #yaxis_title="City",
        #xaxis_title="Sales",
        font=fonts,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            #showgrid=False, 
            #tickangle=-45
            visible=False
            ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            ticksuffix=' ',
            autorange="reversed"
            ),
        bargap=.33,
        height=600,
        width=550
    )

    return bar_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)