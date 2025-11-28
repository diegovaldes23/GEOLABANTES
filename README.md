# GEOLABANTES

# Proyecto LABDV – Análisis Territorial de Cerrillos

Este proyecto integra análisis espacial, geoestadística y modelos de machine learning para la comuna de Cerrillos.  
Incluye un pipeline completo ejecutado en Jupyter (via Docker) y una aplicación web interactiva desarrollada en Streamlit.

## 🔧 Requisitos
- Docker / Docker Compose  
- Python 3.10+  
- pip / virtualenv  

---

## ▶️ Ejecutar Jupyter (Docker)

```bash
cd LABDV
docker compose up


Luego abrir en el navegador:

http://localhost:8888


Los notebooks están en /notebooks y sus resultados se guardan en /outputs/reports.

Para detener los contenedores:

docker compose down

▶️ Ejecutar la aplicación Streamlit
cd LABDV
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app/static/main.py


App disponible en:

http://localhost:8501
