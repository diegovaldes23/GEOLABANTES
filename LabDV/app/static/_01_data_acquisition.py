#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st

# Rutas absolutas
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"


def run_section(st):
    COMUNA = "Cerrillos"

    st.subheader("📥 01. Adquisición y exploración básica de datos")
    st.write(f"Comuna seleccionada: **{COMUNA}**")

    # Mostrar archivos en data/raw
    try:
        archivos = os.listdir(RAW_DIR)
        st.markdown("### 📂 Archivos disponibles en `data/raw`")
        st.write(archivos)
    except Exception as e:
        st.error(f"No se pudo listar `{RAW_DIR}`: {e}")
        return

    plt.style.use("seaborn-v0_8-darkgrid")

    # Cargar datos
    try:
        limite = gpd.read_file(RAW_DIR / "cerrillos_limite.shp").to_crs(epsg=32719)
        buildings = gpd.read_file(
            RAW_DIR / "osm_buildings_cerrillos.geojson"
        ).to_crs(epsg=32719)
    except Exception as e:
        st.error(f"No se pudieron cargar los datos base: {e}")
        return

    st.success(f"Datos cargados correctamente: {len(buildings)} edificios.")

    # Visualización
    st.subheader("🖼️ Límite comunal + edificaciones OSM")

    fig, ax = plt.subplots(figsize=(10, 10))
    limite.boundary.plot(ax=ax, color="red", linewidth=2, label="Límite Comunal")
    buildings.plot(
        ax=ax,
        color="lightgray",
        edgecolor="black",
        linewidth=0.2,
        alpha=0.7,
    )
    ax.set_title(f"{COMUNA} - Límite + Edificios (OSM)")
    ax.set_axis_off()

    st.pyplot(fig)
