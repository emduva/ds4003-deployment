# import dependencies
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

# read in data from csv
df = pd.read_csv('gdp_pcap.csv')

# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
# server setup
server = app.server

# transpose gdp data - necessary for use in the line chart
df_tp = df.transpose()
# make column names equal to country names
df_tp.columns = df_tp.iloc[0]
# remove redundant row
df_tp = df_tp.drop('country')
# reset index
df_tp = df_tp.reset_index()
# rename index column to year
df_tp = df_tp.rename(columns={'index' : 'year'})

# create list of countries in dataset
all_countries = df['country'].unique().tolist()

# pivot gdp data long
df_pivot = df_tp.melt(id_vars='year', value_vars=all_countries, var_name='country', value_name='gdp')
# reformat gdp values as numbers; if this is not done line chart y axis does not display properly
df_pivot['gdp'] = df_pivot['gdp'].replace({'k': '*1e3'}, regex=True).map(pd.eval).astype(int)
# do the same for years
df_pivot['year'] = df_pivot['year'].astype(int)

# get all unique years in dataset
unique_years = df_pivot['year'].unique()
# create list of every 25 years
mark_years = unique_years[unique_years % 25 == 0]

# create html div for the graph
graph_div = html.Div([
    dcc.Graph(
        id='graph'
    ),
])

# create html div for country selection dropdown
dropdown_div = html.Div(dcc.Dropdown(
            id="country-dropdown",
            # can select multiple countries
            multi=True,
            value=['USA', 'France', 'China', 'Egypt', 'Vietnam', 'Brazil'],
            options=[
            {"label": x, "value": x} 
            # populate from dataset
            for x in sorted(df['country'].unique())
            ],
            # spans half of page width (6/12 columns)
        ), className="six columns")

# create html div for year selection slider
slider_div = html.Div(
    # slider has tow nodes to allow selection of a range
    dcc.RangeSlider(
        id = 'year-slider',
        # minimum date in the dataset
        min = df_pivot['year'].min(), 
        # maximum date in the dataset
        max = df_pivot['year'].max(), 
        # slider can be moved by 5 year increments
        step = 5,
        # place mark every 25 years
        marks={str(year): str(year) for year in mark_years},
        # default slider positions at min and max values
        value = [df_pivot['year'].min(), df_pivot['year'].max()],
        # nodes cannot cross
        allowCross=False,
         # spans half of page width (6/12 columns)
    ), className="six columns")

# variables for text in app
title = "GDP Per Capita of 195 Countries Over Time"
description_text = '''This is a visualization of data for estimates of the GDP per capita of 195 countries from years 1800 to 2100.
Values in the far past are based on analysis of historical data, while future values are extrapolated based on currently available data.
 Values from recent years are primarily from the World Bank; data is complied from the Gapminder GDP per capita dataset.'''

# define app layout
app.layout = html.Div([
    # heading
    html.H1(title, style={'width': '100%', 'display': 'flex', 'align-items':'center', 'justify-content':'center'}),
    # description paragraph
    html.P(description_text),
    # country select dropdown and year select slider
    html.Div([dropdown_div,
    slider_div]),
    # padding area
    html.Div(style={'marginBottom': 100, 'marginTop': 100}),
    # graph
    graph_div,
], className="row")
# callbacks
@app.callback(
    Output('graph', 'figure'),
    Input('year-slider', 'value'),
    Input('country-dropdown', 'value'))
def update_figure(year_range, countries):
    # filter dataset according to selected year range
    filtered_df = df_pivot[df_pivot['year'] >= year_range[0]]
    filtered_df = filtered_df[filtered_df['year'] <= year_range[1]]

    # filter dataset according to selected countries
    countries_filter = all_countries.copy()
    print(countries_filter)

    for country in countries:
        countries_filter.remove(country)

    for country in countries_filter:
        filtered_df = filtered_df[filtered_df['country'] != country]

    # create new graph
    fig = px.line(filtered_df, 
                      # set x axis to year
                      x='year', 
                      # set y axis to gdp
                      y='gdp',
                      # put gdp data for each country on a different line with a unique color
                      color='country',
                    # set graph title
                    title='GDP per Capita of Countries from 1800-2100',
                    # set labels in chart to be more formal
                    labels={'country': 'Country', 'year' : 'Year', 'gdp' : 'GDP per Capita (USD)'})

    # update graph
    fig.update_layout()

    return fig

# run app
if __name__ == '__main__':
    app.run_server(debug=True)