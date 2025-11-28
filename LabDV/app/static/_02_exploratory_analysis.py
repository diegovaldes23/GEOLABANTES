#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "outputs" / "reports"


def run_section(st):
    st.subheader("🔍 02. Análisis Exploratorio de Datos Espaciales (ESDA) - Cerrillos")

    # Cargar datos
    try:
        cerrillos = gpd.read_file(RAW_DIR / "cerrillos_limite.shp").to_crs(epsg=32719)
        buildings = gpd.read_file(
            RAW_DIR / "osm_buildings_cerrillos.geojson"
        ).to_crs(epsg=32719)
    except Exception as e:
        st.error(f"No se pudieron cargar los datos de Cerrillos: {e}")
        return

    # Calcular área
    buildings["area_m2"] = buildings.geometry.area
    st.success(f"Datos cargados: {len(buildings)} edificios con área calculada.")

    # --- Mapa base ---
    st.markdown("### 🗺️ Distribución de edificios")

    fig, ax = plt.subplots(figsize=(8, 8))
    cerrillos.boundary.plot(ax=ax, color="red", linewidth=2)
    buildings.plot(
        ax=ax,
        color="lightgray",
        edgecolor="black",
        linewidth=0.2,
        alpha=0.7,
    )

    ax.set_title("Distribución de edificios en Cerrillos")
    ax.set_axis_off()

    # Leyenda manual
    legend_elements = [
        Line2D([0], [0], color="red", lw=2, label="Límite comunal"),
        Patch(facecolor="lightgray", edgecolor="black", label="Edificios"),
    ]
    ax.legend(handles=legend_elements, loc="lower left")

    st.pyplot(fig)

    # --- Histograma ---
    st.markdown("### 📊 Distribución de áreas de edificios")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(buildings["area_m2"], kde=True, ax=ax, bins=50)
    ax.set_xlabel("Área (m²)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Histograma de área de edificios")
    st.pyplot(fig)

    # --- Mapas ESDA exportados ---
    st.markdown("### 🖼️ Mapas ESDA exportados")

    esda_imgs = [
        ("esda_mapa_base.png", "Mapa base de Cerrillos"),
        ("esda_area_tematica.png", "Mapa temático por área"),
        ("esda_clusters_lisa.png", "Clusters LISA"),
        ("esda_hotspots.png", "Mapa de hotspots"),
        ("esda_semivariograma.png", "Semivariograma (ESDA)"),
    ]

    for fname, caption in esda_imgs:
        path = OUT_DIR / fname
        if path.exists():
            st.image(str(path), caption=caption)
