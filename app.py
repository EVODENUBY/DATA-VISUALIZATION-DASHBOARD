import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import utils  

app = dash.Dash(__name__, assets_folder='assets')

# Load data into a DataFrame
df = pd.read_csv('data/imdb_movies.csv',sep=';', on_bad_lines='skip' )
df = utils.clean_data(df)  #for data cleaning

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# App layout
app.layout = html.Div([
    html.Div([
        html.H3("EVODENUBY", className="header-title"),
        html.H1("IMDb Movies Dashboard", className="header-title"),
        html.P(
            "Explore movie ratings, budgets, and popularity across years",
            className="header-description",
        ),
    ], className="header"),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='year-slider',
                options=[{'label': str(year), 'value': year} 
                        for year in sorted(df['year'].dropna().unique())],
                value=2010,
                clearable=False,
                className="dropdown"
            ),
        ], className="card"),
        
        html.Div([
            dcc.Dropdown(
                id='genre-filter',
                options=[{'label': genre, 'value': genre} 
                        for genre in df['genre'].str.split(', ').explode().unique()],
                multi=True,
                placeholder="Select genre(s)",
                className="dropdown"
            ),
        ], className="card"),
    ], className="wrapper"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='rating-vs-budget'),
        ], className="card"),
        
        html.Div([
            dcc.Graph(id='movies-by-year'),
        ], className="card"),
    ], className="wrapper"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='top-directors'),
        ], className="card"),
        
        html.Div([
            html.H3("Correlation Heatmap"),
            html.Img(id='heatmap-image'),
        ], className="card"),
    ], className="wrapper"),
], className="container")
#footer
app.layout.children.append(
    html.Div([
        html.P("Created by Evode MUYISINGIZEMWESE", className="footer-text"),
        html.A("GitHub", href="https://www.github.com/EVODENUBY", target="_blank", className="footer-link"),
        html.A("Linkedin", href="#", target="_blank", className="footer-link"),
        html.A("YouTube", href="https://www.youtube.com/@EVODENUBY", target="_blank", className="footer-link"),
    ], className="footer")
)
# Callbacks for interactivity
@app.callback(
    Output('rating-vs-budget', 'figure'),
    [Input('year-slider', 'value'),
     Input('genre-filter', 'value')]
)
def update_scatter_plot(selected_year, selected_genres):
    filtered_df = df[df['year'] == selected_year]
    
    if selected_genres:
        mask = filtered_df['genre'].apply(
            lambda x: any(genre in x for genre in selected_genres)) 
        filtered_df = filtered_df[mask]
    
    fig = px.scatter(
        filtered_df,
        x='budget',
        y='avg_vote',
        color='genre',
        hover_data=['title', 'director'],
        title=f'Rating vs Budget ({selected_year})',
        labels={'avg_vote': 'Average Rating', 'budget': 'Budget (USD)'}
    )
    fig.update_layout(transition_duration=500)
    return fig

@app.callback(
    Output('movies-by-year', 'figure'),
    [Input('genre-filter', 'value')]
)
def update_movies_by_year(selected_genres):
    if selected_genres:
        mask = df['genre'].apply(
            lambda x: any(genre in x for genre in selected_genres))
        filtered_df = df[mask]
    else:
        filtered_df = df.copy()
        
    yearly_counts = filtered_df.groupby('year').size().reset_index(name='count')
    
    fig = px.line(
        yearly_counts,
        x='year',
        y='count',
        title='Movies Released by Year',
        labels={'count': 'Number of Movies', 'year': 'Year'}
    )
    return fig

@app.callback(
    Output('top-directors', 'figure'),
    [Input('year-slider', 'value')]
)
def update_top_directors(selected_year):
    filtered_df = df[df['year'] == selected_year]
    top_directors = filtered_df.groupby('director')['avg_vote']\
        .mean().nlargest(10).reset_index()
    
    fig = px.bar(
        top_directors,
        x='director',
        y='avg_vote',
        title=f'Top Directors by Average Rating ({selected_year})',
        labels={'avg_vote': 'Average Rating', 'director': 'Director'}
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig

@app.callback(
    Output('heatmap-image', 'src'),
    [Input('year-slider', 'value')]
)
def update_heatmap(selected_year):
    filtered_df = df[df['year'] == selected_year]
    numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])
    corr_matrix = numeric_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    encoded_image = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded_image}'

if __name__ == '__main__':
    app.run(debug=True)