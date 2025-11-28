#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
OUT_DIR = BASE_DIR / "outputs" / "reports"


def run_section(st):
    st.subheader("📊 05. Síntesis final de resultados - Cerrillos")

    metrics_path = OUT_DIR / "final_metrics.csv"
    maps_path = OUT_DIR / "final_maps.png"
    metrics_plot_path = OUT_DIR / "final_metrics_plot.png"

    # Métricas finales
    try:
        metrics = pd.read_csv(metrics_path)
        st.markdown("### 📈 Métricas finales comparadas")
        st.dataframe(metrics, width="stretch")
    except Exception as e:
        st.warning(f"No se pudo cargar `final_metrics.csv`: {e}")

    # Mapas comparativos
    if maps_path.exists():
        st.markdown("### 🗺️ Mapas comparativos (real vs modelos)")
        st.image(str(maps_path), caption="Mapas comparativos (real vs modelos)")
    else:
        st.info("ℹ️ No se encontró `final_maps.png` en outputs/reports")

    # Gráfico de comparación de métricas
    if metrics_plot_path.exists():
        st.markdown("### 📉 Gráfico de comparación de métricas")
        st.image(str(metrics_plot_path), caption="Comparación visual de métricas finales")
    else:
        st.info("ℹ️ No se encontró `final_metrics_plot.png` en outputs/reports")

    # Texto de cierre
    st.markdown(
        """
        ### 📝 Conclusiones generales

        - Los modelos de machine learning logran capturar patrones espaciales relevantes en Cerrillos.  
        - La geoestadística permite analizar la variación espacial de variables clave.  
        - La combinación de ESDA, geoestadística y ML entrega una base cuantitativa robusta para apoyar decisiones territoriales.
        """
    )
