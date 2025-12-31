# Laboratorio: Detección de Cambios Urbanos – Pudahuel (2017–2024)

**Curso:** Desarrollo de Aplicaciones Geoinformáticas  
**Institución:** Universidad de Santiago de Chile (USACH)  
**Integrantes:** Diego Valdés, Valentina Campos, Joaquín Saldivia  
**Profesor:** Francisco Parra O.

## 📝 Descripción del Proyecto
Este proyecto aplica técnicas de teledetección multitemporal para identificar la expansión industrial y logística en la comuna de Pudahuel. Utilizando imágenes de la misión **Sentinel-2**, se calculan índices de vegetación (NDVI) y edificación (NDBI) para cuantificar la pérdida de cobertura natural y el aumento de superficies construidas entre 2017 y 2024.

## 📊 Funcionalidades del Dashboard (Cumplimiento Pauta)
La aplicación interactiva desarrollada en **Streamlit** incluye:
- **Mapa Interactivo:** Visualización de capas raster (Deltas) con control de leyendas y capas.
- **Comparador Visual:** Slider "Antes/Después" para observar el cambio de uso de suelo directo.
- **Gráficos Dinámicos:** Histogramas y gráficos de dispersión que se actualizan según el año seleccionado.
- **Análisis Zonal:** Tabla interactiva con métricas calculadas por cuadrantes de 500m.
- **Exportación:** Botón de descarga para obtener los resultados estadísticos en formato `.csv`.

## 🛠️ Requisitos Técnicos
- **Lenguaje:** Python 3.10 o superior.
- **Google Earth Engine:** Cuenta activa y proyecto configurado (ID utilizado: `ee-diegovaldesf`).
- **Librerías principales:** `streamlit`, `rasterio`, `folium`, `numpy`, `pandas`, `geopandas`.

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Entrar a la carpeta del proyecto
```bash
cd geoinformatica-lab2
```
### 2. Levantar los contenedores
```bash
docker compose up -d
```

### 3. Abrir en el navegador para ver los Notebooks: URL: http://localhost:8888
Nota: Los notebooks de procesamiento se encuentran en /notebooks y los resultados generados se guardan automáticamente en /outputs/reports.


### 4. Preparar el Entorno
Se recomienda el uso de un entorno virtual para evitar conflictos de dependencias:
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Linux/Mac)
source venv/bin/activate
```
### 5. Instalar Dependencias
```bash
pip install -r requirements.txt
```
Nota: El archivo requirements.txt incluye streamlit, folium, streamlit-folium, rasterio, geopandas, entre otros.
### 5. Ejecutar la Aplicación

Para lanzar el dashboard en tu navegador local, ejecuta:

```bash
streamlit run app/streamlit_app.py
```

### 6. Estructura de Archivos Clave

- app/: Contiene el código fuente de la aplicación Streamlit.
- data/processed/: Almacena los productos raster (.tif) y deltas calculados.
- outputs/: Resultados del análisis zonal y tablas estadísticas en CSV.
- notebooks/: Jupyter Notebooks utilizados para el procesamiento inicial y validación.

### 7. Fuente de Datos

Los datos fueron procesados originalmente en Google Earth Engine utilizando el producto COPERNICUS/S2_SR_HARMONIZED (Sentinel-2 MSI, Nivel-2A), aplicando filtros de nubosidad (<10%) y compuestos de mediana para los meses de enero y febrero de cada año analizado.
