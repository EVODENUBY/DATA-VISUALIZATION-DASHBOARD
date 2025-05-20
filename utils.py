import pandas as pd

def clean_data(df):
    
    # ERROR BAD LINES  = FALSE, TO AVOID PROBLEMATIC ROWS.
    df = pd.read_csv('data/imdb_movies.csv', encoding='utf-8', 
                    on_bad_lines='skip',
                    sep=';', 
                    quotechar='"', 
                    escapechar='\\')
    
    df.columns = df.columns.str.lower().str.strip()

    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df[df['year'].notna()]
    df['avg_vote'] = df['avg_vote'].fillna(df['avg_vote'].median())
    df['genre'] = df['genre'].fillna('Unknown')
    
    return df