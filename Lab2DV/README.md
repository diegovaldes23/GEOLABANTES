# Laboratorio Cambio Urbano – Pudahuel (2017–2024)

## Requisitos
- Python 3.10+ (recomendado 3.11/3.12)
- Entorno virtual (venv/conda)
- Dependencias: ver `requirements.txt` (o instalar manualmente)

## Estructura esperada (archivos clave)
- `data/processed/`
  - `ndvi_pudahuel_2017.tif`, `ndvi_pudahuel_2019.tif`, `ndvi_pudahuel_2021.tif`, `ndvi_pudahuel_2024.tif`
  - `ndbi_pudahuel_2017.tif`, `ndbi_pudahuel_2019.tif`, `ndbi_pudahuel_2021.tif`, `ndbi_pudahuel_2024.tif`
  - `delta_ndvi_2017_2024.tif`, `delta_ndbi_2017_2024.tif`
  - `cambios_por_zona.gpkg` (grilla con métricas por zona)
- `outputs/`
  - `cambios_por_zona_pudahuel.csv`
- `app/streamlit_app.py`

## Instalación
Activar el entorno virtual y luego instalar:

```bash
pip install -r requirements.txt
pip install streamlit folium streamlit-folium branca
