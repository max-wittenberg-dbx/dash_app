import pandas as pd
import dash
from dash import dcc as dcc
from dash import html as html
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import datetime

# Load the data
df = pd.read_csv(
    "https://raw.githubusercontent.com/max-wittenberg-dbx/dash_app/main/dl_with_preds.csv")

# Rename the population column to sales
df = df.rename(columns={'population': 'sales'})
df = df.rename(columns={'predicted_population': 'predicted_sales'})

# Create the app
app = dash.Dash(__name__)
app.title = "Global Sales by Country"

# Define colors and fonts
colors = {
    'background': '#FFFFFF',
    'text': '#0D0D0D',
    'accent': '#0D0D0D'
}

fonts = {
    'family': 'Arial',
    'size': 16,
    'color': colors['text']
}

# Define the layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Img(src='https://cdn.cookielaw.org/logos/29b588c5-ce77-40e2-8f89-41c4fa03c155/bc546ffe-d1b7-43af-9c0b-9fcf4b9f6e58/1e538bec-8640-4ae9-a0ca-44240b0c1a20/databricks-logo.png', style={'height':'25px', 'margin':'8px', 'display': 'inline-block', 'vertical-align': 'left'}),

    html.H1(
        children="Global Sales by Country",
        style={
            'textAlign': 'center',
            'color': colors['accent'],
            'fontFamily': fonts['family']
        }
    ),
    html.H2(
        children=f"Data as of {datetime.datetime.today().strftime('%B %d, %Y')}",
        style={
            'textAlign': 'center',
            'color': colors['accent'],
            'fontFamily': fonts['family']
        }
    ),

    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in df['country'].unique()],
        value=df['country'].iloc[0],
        clearable=True,
        style={
            'margin': '10px',
            'fontFamily': fonts['family'],
            'color': colors['text']
        }
    ),

    dcc.Graph(id='map'),

    html.Div([
        dcc.Graph(id='top-10-bar')
    ])
])


# Define the callback for the map
@app.callback(
    dash.dependencies.Output('map', 'figure'),
    dash.dependencies.Input('country-dropdown', 'value')
)
def update_map(selected_country):
    # Filter the data by the selected country
    if selected_country is None:
        filtered_df = df
    else:
        filtered_df = df[df['country'] == selected_country]

    # Create the map figure
    map_fig = px.scatter_mapbox(
        filtered_df, 
        lat='lat', 
        lon='lng', 
        hover_name='city',
        hover_data=['country', 'predicted_sales'],
        color='predicted_sales', 
        size='predicted_sales', 
        zoom=1.5, height=800)
    map_fig.update_layout(mapbox_style="carto-darkmatter")
    map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

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
    bar_fig = go.Figure(data=[go.Bar(x=sorted_df['city'], y=sorted_df['sales'])])
    bar_fig.update_layout(title="Top 10 Cities by Sales",
                          xaxis_title="City",
                          yaxis_title="Sales",
                          font=fonts,
                          plot_bgcolor=colors['background'],
                          paper_bgcolor=colors['background'],
                          xaxis=dict(showgrid=False, tickangle=-45),
                          yaxis=dict(showgrid=False))

    return bar_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)