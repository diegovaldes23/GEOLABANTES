#!/usr/bin/env python
# coding: utf-8
"""
Aplicación web para visualización del análisis geoespacial de Cerrillos.
Autores: Diego Valdés y Valentina Campos
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

# Importar las secciones (deben estar en esta misma carpeta)
from _01_data_acquisition import run_section as sec_data_acq
from _02_exploratory_analysis import run_section as sec_esda
from _03_geostatistics import run_section as sec_geo
from _04_machine_learning import run_section as sec_ml
from _05_results_synthesis import run_section as sec_summary

# ============================================================
# Configuración general
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv()

COMUNA = os.getenv("COMUNA_NAME") or "Cerrillos"

st.set_page_config(
    page_title=f"Análisis Territorial - {COMUNA}",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS opcional
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #0066CC;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Título principal
st.title("🗺️ Sistema de Análisis Territorial")
st.markdown(f"### Comuna: **{COMUNA}**")

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown("### 📊 Navegación")

    page = st.selectbox(
        "Seleccione una sección:",
        [
            "🏠 Inicio",
            "📥 01. Adquisición de Datos",
            "🔍 02. Análisis Exploratorio",
            "📈 03. Geoestadística",
            "🤖 04. Machine Learning",
            "📊 05. Síntesis de Resultados",
        ],
    )

    st.markdown("---")
    st.info(
        """
        **Laboratorio Integrador – Geoinformática 2025**

        Proyecto comunal: Cerrillos  
        Desarrollado por:  
        - Diego Valdés  
        - Valentina Campos
        """
    )

# ============================================================
# Contenido según la página seleccionada
# ============================================================

if page == "🏠 Inicio":
    st.subheader("Resumen general del proyecto")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📍 Ubicación de la comuna")

        # Mapa simple centrado en Cerrillos (aprox)
        m = folium.Map(location=[-33.49, -70.71], zoom_start=13, tiles="OpenStreetMap")
        folium.Marker(
            [-33.49, -70.71],
            popup="Cerrillos",
            tooltip="Cerrillos",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)

        st_folium(m, height=400, width=None)

    with col2:
        st.markdown("#### 🎯 Objetivos del análisis")
        st.markdown(
            """
            - Integrar distintas fuentes de datos espaciales para la comuna de Cerrillos.  
            - Analizar la distribución de edificaciones y variables territoriales clave.  
            - Aplicar técnicas de geoestadística e inteligencia artificial.  
            - Generar una síntesis visual y cuantitativa para apoyar la toma de decisiones territoriales.
            """
        )

elif page == "📥 01. Adquisición de Datos":
    sec_data_acq(st)

elif page == "🔍 02. Análisis Exploratorio":
    sec_esda(st)

elif page == "📈 03. Geoestadística":
    sec_geo(st)

elif page == "🤖 04. Machine Learning":
    sec_ml(st)

elif page == "📊 05. Síntesis de Resultados":
    sec_summary(st)

# ============================================================
# Footer
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Laboratorio Integrador – Geoinformática 2025</p>
        <p>Proyecto desarrollado por <b>Diego Valdés</b> y <b>Valentina Campos</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
