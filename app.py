import streamlit as st
import numpy as np
import pandas as pd
import pickle
from difflib import get_close_matches

# Cargar la matriz de similitud y los datos
with open('combined_similirity.pkl', 'rb') as file:
    combined_similarity = pickle.load(file)
games_data_merged = pd.read_csv('games_data_merged.csv')

# Función para generar recomendaciones
def recommend(game_name, similarity_matrix, games_data, top_n=5):
    if game_name in games_data['title'].values:
        idx = games_data[games_data['title'] == game_name].index[0]
        sim_scores = list(enumerate(similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sim_scores[1:top_n + 1]]
        recommended_titles = games_data.iloc[top_indices]['title'].tolist()
        return recommended_titles
    else:
        # Buscar juegos similares utilizando difflib
        similar_titles = get_close_matches(game_name, games_data['title'], n=5, cutoff=0.5)
        return similar_titles

# Interfaz de Streamlit
st.set_page_config(page_title="Game Recommender", page_icon=":game_die:", layout="wide")

# Establecer colores personalizados
primary_color = "#2e9ff5"  # Azul claro
background_color = "#171a21"  # Fondo oscuro
card_color = "#2a2e38"  # Gris oscuro
text_color = "#e8e8e8"  # Color de texto blanco/clarito

# Título y descripción
st.title("Game Recommender System")
st.markdown("""
    Descubre nuevos juegos recomendados basados en lo que ya te gusta. ¡Encuentra tu próximo juego favorito ahora!
""", unsafe_allow_html=True)

# Estilización de la imagen
st.image("steam.png", width=150)

# Configurar el fondo de la página
st.markdown(f"""
    <style>
        body {{
            background-color: {background_color};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

# Entrada del usuario: Dropdown para búsqueda dinámica
search_term = st.text_input("Escribe el nombre de un juego:", key="game_search")

if search_term:
    # Filtrar juegos que contengan el término ingresado
    filtered_games = games_data_merged[games_data_merged['title'].str.contains(search_term, case=False, na=False)]
    
    if not filtered_games.empty:
        # Crear un dropdown con las opciones filtradas
        selected_game = st.selectbox("Selecciona un juego", filtered_games['title'].tolist())
        
        if selected_game:
            recommendations = recommend(selected_game, combined_similarity, games_data_merged, top_n=5)
            if recommendations:
                st.subheader(f"Recomendaciones para '{selected_game}':")
                for i, rec in enumerate(recommendations, 1):
                    # Encontrar el app_id de cada juego recomendado
                    app_id = games_data_merged[games_data_merged['title'] == rec]['app_id'].values[0]
                    game_url = f"https://store.steampowered.com/app/{app_id}/{rec.replace(' ', '_')}/"
                    
                    # Mostrar recomendación como tarjeta
                    st.markdown(f"""
                    <div style="background-color:{card_color}; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid {primary_color};">
                        <h5 style="color: {primary_color};">{i}: <a href="{game_url}" target="_blank" style="text-decoration: none; color: {primary_color};">{rec}</a></h5>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No se encontraron recomendaciones para el juego seleccionado.")
    else:
        st.error("No se encontraron juegos que coincidan con el término ingresado.")
