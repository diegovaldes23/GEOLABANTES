#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
OUT_DIR = BASE_DIR / "outputs" / "reports"


def run_section(st):
    st.subheader("🤖 04. Resultados de Modelos de Machine Learning - Cerrillos")

    metrics_path = OUT_DIR / "ml_metrics.csv"
    results_geo_path = OUT_DIR / "ml_results.geojson"

    # Cargar métricas y resultados
    try:
        metrics = pd.read_csv(metrics_path)
        buildings = gpd.read_file(results_geo_path)
    except Exception as e:
        st.error(f"No se pudieron cargar los resultados de ML: {e}")
        return

    if buildings.empty:
        st.warning(
            "⚠️ El archivo `ml_results.geojson` está vacío. Revisa el guardado en el notebook 04."
        )
        return

    st.success("Resultados de modelos ML cargados correctamente desde `outputs/reports`.")

    # Tabla de métricas
    st.markdown("### 📊 Métricas de los modelos")
    st.dataframe(metrics, width="stretch")

    # Gráficos de barras de métricas
    st.markdown("### 📈 Comparación de métricas (RMSE y R²)")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.barplot(data=metrics, x="Modelo", y="RMSE", ax=ax[0])
    ax[0].set_title("RMSE por modelo")
    ax[0].tick_params(axis="x", rotation=45)

    sns.barplot(data=metrics, x="Modelo", y="R²", ax=ax[1])
    ax[1].set_title("R² por modelo")
    ax[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    st.pyplot(fig)

    # Mapas de predicciones
    st.markdown("### 🗺️ Mapas de predicciones por modelo")

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    if "pred_rf" in buildings.columns:
        buildings.plot(
            ax=axes[0],
            column="pred_rf",
            cmap="viridis",
            legend=True,
            legend_kwds={"shrink": 0.6},
        )
        axes[0].set_title("Predicción - Random Forest")
        axes[0].set_axis_off()
    else:
        axes[0].set_title("Random Forest")
        axes[0].text(0.5, 0.5, "Columna 'pred_rf' no encontrada", ha="center")
        axes[0].set_axis_off()

    if "pred_xgb" in buildings.columns:
        buildings.plot(
            ax=axes[1],
            column="pred_xgb",
            cmap="viridis",
            legend=True,
            legend_kwds={"shrink": 0.6},
        )
        axes[1].set_title("Predicción - XGBoost")
        axes[1].set_axis_off()
    else:
        axes[1].set_title("XGBoost")
        axes[1].text(0.5, 0.5, "Columna 'pred_xgb' no encontrada", ha="center")
        axes[1].set_axis_off()

    plt.tight_layout()
    st.pyplot(fig)

    # Figuras extra exportadas
    st.markdown("### 🖼️ Figuras exportadas desde el notebook")

    extra_imgs = [
        ("ml_comparacion.png", "Comparación visual de métricas de modelos"),
        ("ml_mapas_predicciones.png", "Mapas de predicciones (resumen)"),
    ]
    for fname, caption in extra_imgs:
        path = OUT_DIR / fname
        if path.exists():
            st.image(str(path), caption=caption)
