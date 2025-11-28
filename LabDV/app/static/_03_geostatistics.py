#!/usr/bin/env python
# coding: utf-8

import json
import os
from pathlib import Path

import geopandas as gpd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "outputs" / "reports"


def run_section(st):
    st.subheader("📈 03. Geoestadística - Cerrillos")

    # Límite comunal (referencia)
    try:
        gpd.read_file(RAW_DIR / "cerrillos_limite.shp").to_crs(epsg=32719)
        st.success("Límite comunal cargado correctamente.")
    except Exception as e:
        st.error(f"Error cargando límite comunal: {e}")
        return

    # Mapa Kriging
    st.markdown("### 🗺️ Mapa interpolado (Kriging)")
    krig_path = OUT_DIR / "geo_kriging_map.png"
    if krig_path.exists():
        st.image(str(krig_path), caption="Mapa interpolado - Kriging")
    else:
        st.warning("⚠️ No se encontró `geo_kriging_map.png` en outputs/reports")

    # Semivariograma
    st.markdown("### 📉 Semivariograma experimental")
    semiv_path = OUT_DIR / "geo_semivariograma.png"
    if semiv_path.exists():
        st.image(str(semiv_path), caption="Semivariograma experimental")
    else:
        st.warning("⚠️ No se encontró `geo_semivariograma.png` en outputs/reports")

    # Validación cruzada
    st.markdown("### ✔️ Validación cruzada del modelo")

    val_path = OUT_DIR / "geo_validation.json"
    if val_path.exists():
        with open(val_path) as f:
            val = json.load(f)
        st.success(
            f"Validación cruzada (20%) — RMSE: **{val['rmse']:.2f} m²** "
            f"con **{val['n_validados']} puntos validados**."
        )
    else:
        st.info("ℹ️ No se encontró `geo_validation.json` en outputs/reports")
