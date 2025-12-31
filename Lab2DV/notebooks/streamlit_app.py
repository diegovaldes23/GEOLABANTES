from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds

import streamlit as st
import folium
from folium.raster_layers import ImageOverlay
from folium.plugins import DualMap
from streamlit_folium import st_folium

import os
# --- ESTO DEBE IR ANTES DE IMPORTAR GEOPANDAS O RASTERIO ---
os.environ['PROJ_LIB'] = '/opt/conda/lib/python3.10/site-packages/pyproj/proj_dir/share/proj'
os.environ['PROJ_DATA'] = '/opt/conda/lib/python3.10/site-packages/pyproj/proj_dir/share/proj'

import streamlit as st
import geopandas as gpd
# ... resto de tus imports

# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="Cambio Urbano Pudahuel (2017–2024)",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path("/home/jovyan")
DATA = ROOT / "data"
# Verificamos si existe la carpeta 'processed', si no, usamos 'data' directamente
DATA_PROCESSED = DATA / "processed" if (DATA / "processed").exists() else DATA
OUTPUTS = ROOT / "outputs"

YEARS = [2017, 2019, 2021, 2024]

NDVI = {y: DATA_PROCESSED / f"ndvi_pudahuel_{y}.tif" for y in YEARS}
NDBI = {y: DATA_PROCESSED / f"ndbi_pudahuel_{y}.tif" for y in YEARS}
DELTA_NDVI = DATA_PROCESSED / "delta_ndvi_2017_2024.tif"
DELTA_NDBI = DATA_PROCESSED / "delta_ndbi_2017_2024.tif"

ZONES_GPKG = DATA_PROCESSED / "cambios_por_zona.gpkg"
ZONES_CSV = OUTPUTS / "cambios_por_zona_pudahuel.csv"


# -----------------------------
# Helpers
# -----------------------------
def file_ok(p: Path) -> bool:
    return p.exists() and p.is_file()


@st.cache_data(show_spinner=False)
def load_zones():
    if not file_ok(ZONES_GPKG):
        return None
    gdf = gpd.read_file(ZONES_GPKG)

    # Asegurar WGS84 para mapa
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    centroid = gdf.unary_union.centroid
    return gdf, (centroid.y, centroid.x)


@st.cache_data(show_spinner=False)
def raster_to_png_and_bounds(raster_path: Path, vmin=None, vmax=None):
    with rasterio.open(raster_path) as src:
        arr = src.read(1).astype("float32")
        nodata = src.nodata

        # Mask nodata
        if nodata is not None:
            arr = np.where(arr == nodata, np.nan, arr)

        # Bounds a EPSG:4326
        if src.crs is None:
            west, south, east, north = src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top
        else:
            west, south, east, north = transform_bounds(
                src.crs, "EPSG:4326", *src.bounds, densify_pts=21
            )

        finite = np.isfinite(arr)
        if not np.any(finite):
            raise ValueError(f"Raster vacío o sin datos válidos: {raster_path.name}")

        if vmin is None:
            vmin = np.nanpercentile(arr, 2)
        if vmax is None:
            vmax = np.nanpercentile(arr, 98)

        arr = np.clip(arr, vmin, vmax)
        norm = (arr - vmin) / (vmax - vmin + 1e-9)
        norm = np.where(np.isfinite(norm), norm, np.nan)

        # Colormap simple (rojo -> amarillo -> verde)
        def colormap(x):
            r = np.clip(2 - 2 * x, 0, 1)
            g = np.clip(2 * x, 0, 1)
            b = np.clip(0.30 + 0 * x, 0, 1)
            return r, g, b

        r, g, b = colormap(norm)
        a = np.where(np.isfinite(norm), 0.85, 0.0)

        rgba = np.dstack(
            [
                (r * 255).astype(np.uint8),
                (g * 255).astype(np.uint8),
                (b * 255).astype(np.uint8),
                (a * 255).astype(np.uint8),
            ]
        )

    bounds = [[south, west], [north, east]]
    return rgba, bounds


def make_map_base(center):
    return folium.Map(location=center, zoom_start=12, control_scale=True, tiles="OpenStreetMap")


def add_overlay(m, rgba, bounds, name):
    ImageOverlay(
        image=rgba,
        bounds=bounds,
        name=name,
        opacity=0.9,
        interactive=True,
        cross_origin=False,
        zindex=2,
    ).add_to(m)


def add_zones_layer(m, zones_gdf):
    gdf = zones_gdf.copy()

    # Rellenar NaNs con 0 para que el estilo no falle
    gdf["perc_gain_built"] = gdf["perc_gain_built"].fillna(0)
    gdf["perc_loss_veg"] = gdf["perc_loss_veg"].fillna(0)
    
    if "perc_gain_built" not in gdf.columns:
        return

    vals = gdf["perc_gain_built"].fillna(0).values
    q = np.quantile(vals, [0.5, 0.75, 0.9, 0.97])

    def style_fn(feat):
        v = feat["properties"].get("perc_gain_built", 0) or 0
        if v <= q[0]:
            color = "#fff5f0"
        elif v <= q[1]:
            color = "#fcbba1"
        elif v <= q[2]:
            color = "#fc9272"
        elif v <= q[3]:
            color = "#fb6a4a"
        else:
            color = "#cb181d"
        return {"fillColor": color, "color": "#999999", "weight": 0.3, "fillOpacity": 0.6}

    folium.GeoJson(
        gdf,
        name="Zonas (intensidad cambio construido)",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["zone_id", "perc_loss_veg", "perc_gain_built"],
            aliases=["Zona", "% Pérdida veg", "% Aumento construido"],
        ),
    ).add_to(m)


@st.cache_data(show_spinner=False)
def compute_year_stats(index_dict):
    rows = []
    for y, p in index_dict.items():
        if not file_ok(p):
            continue
        with rasterio.open(p) as src:
            a = src.read(1).astype("float32")
            nodata = src.nodata
            if nodata is not None:
                a = np.where(a == nodata, np.nan, a)

            rows.append(
                {
                    "Año": y,
                    "Media": float(np.nanmean(a)),
                    "Std": float(np.nanstd(a)),
                    "Min": float(np.nanmin(a)),
                    "Max": float(np.nanmax(a)),
                }
            )
    df = pd.DataFrame(rows)
    return df.sort_values("Año") if not df.empty else df


def kpi_summary_from_zones(zones_gdf: gpd.GeoDataFrame):
    if zones_gdf is None:
        return None
    out = {}
    if "perc_loss_veg" in zones_gdf.columns:
        out["loss_veg_mean"] = float(zones_gdf["perc_loss_veg"].fillna(0).mean())
        out["loss_veg_p90"] = float(zones_gdf["perc_loss_veg"].fillna(0).quantile(0.90))
    if "perc_gain_built" in zones_gdf.columns:
        out["gain_built_mean"] = float(zones_gdf["perc_gain_built"].fillna(0).mean())
        out["gain_built_p90"] = float(zones_gdf["perc_gain_built"].fillna(0).quantile(0.90))
    return out if out else None


# -----------------------------
# Header
# -----------------------------
st.title("Detección de Cambios Urbanos – Pudahuel (2017–2024)")
st.caption("Exploración de NDVI/NDBI, deltas 2017–2024, análisis zonal y comparador antes/después.")


# -----------------------------
# Sidebar (compacta)
# -----------------------------
with st.sidebar:
    st.header("Controles")

    page = st.radio("Sección", ["Explorar", "Comparar", "Datos"], index=0)

    st.markdown("**Capa principal**")
    layer_type = st.selectbox(
        "Selecciona capa",
        ["NDVI", "NDBI", "ΔNDVI (2024-2017)", "ΔNDBI (2024-2017)"],
        index=0,
    )
    year_view = st.selectbox("Año para NDVI/NDBI", YEARS, index=len(YEARS) - 1)
    show_zones = st.checkbox("Mostrar zonas (coroplético)", value=True)

    st.markdown("---")
    st.markdown("**Comparador**")
    comp_index = st.selectbox("Índice", ["NDVI", "NDBI"], index=0)
    year_left = st.selectbox("Año (antes)", YEARS, index=0)
    year_right = st.selectbox("Año (después)", YEARS, index=len(YEARS) - 1)


# -----------------------------
# Data loading
# -----------------------------
zones_data = load_zones()
if zones_data is None:
    zones_gdf, center = None, (-33.40, -70.70)
else:
    zones_gdf, center = zones_data


# -----------------------------
# Tabs content
# -----------------------------
if page == "Explorar":
    # Layout: mapa grande + panel insights
    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.subheader("Mapa")
        m = make_map_base(center)

        try:
            if layer_type == "NDVI":
                p = NDVI.get(year_view)
                if not file_ok(p):
                    st.error(f"No se encontró NDVI {year_view}: {p}")
                else:
                    rgba, bounds = raster_to_png_and_bounds(p)
                    add_overlay(m, rgba, bounds, f"NDVI {year_view}")

            elif layer_type == "NDBI":
                p = NDBI.get(year_view)
                if not file_ok(p):
                    st.error(f"No se encontró NDBI {year_view}: {p}")
                else:
                    rgba, bounds = raster_to_png_and_bounds(p)
                    add_overlay(m, rgba, bounds, f"NDBI {year_view}")

            elif layer_type == "ΔNDVI (2024-2017)":
                if not file_ok(DELTA_NDVI):
                    st.error(f"No se encontró: {DELTA_NDVI}")
                else:
                    rgba, bounds = raster_to_png_and_bounds(DELTA_NDVI)
                    add_overlay(m, rgba, bounds, "ΔNDVI 2024-2017")

            else:
                if not file_ok(DELTA_NDBI):
                    st.error(f"No se encontró: {DELTA_NDBI}")
                else:
                    rgba, bounds = raster_to_png_and_bounds(DELTA_NDBI)
                    add_overlay(m, rgba, bounds, "ΔNDBI 2024-2017")

        except Exception as e:
            st.error(f"Error generando overlay: {e}")

        if show_zones and zones_gdf is not None:
            add_zones_layer(m, zones_gdf)

        folium.LayerControl(collapsed=True).add_to(m)
        st_folium(m, width=None, height=620, use_container_width=True)

    with right:
        st.subheader("Insights")

        # KPIs de zona (si existen)
        kpis = kpi_summary_from_zones(zones_gdf)
        if zones_gdf is None:
            st.info("No se encontró la capa zonal (GPKG).")
        elif not kpis:
            st.info("La capa zonal no tiene métricas esperadas (perc_loss_veg / perc_gain_built).")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Pérdida veg (prom.)", f"{kpis['loss_veg_mean']:.2f}%")
                st.metric("Pérdida veg (P90)", f"{kpis['loss_veg_p90']:.2f}%")
            with c2:
                st.metric("Aum. construido (prom.)", f"{kpis['gain_built_mean']:.2f}%")
                st.metric("Aum. construido (P90)", f"{kpis['gain_built_p90']:.2f}%")

        st.markdown("---")

        # Evolución sin tablas por defecto
        df_ndvi = compute_year_stats(NDVI)
        df_ndbi = compute_year_stats(NDBI)

        st.markdown("**Evolución temporal (media)**")
        sel = st.radio("Serie", ["NDVI", "NDBI"], horizontal=True, index=0)

        if sel == "NDVI" and not df_ndvi.empty:
            st.line_chart(df_ndvi.set_index("Año")[["Media"]], use_container_width=True)
            with st.expander("Ver estadísticas NDVI (tabla)", expanded=False):
                st.dataframe(df_ndvi, use_container_width=True, hide_index=True)
        elif sel == "NDBI" and not df_ndbi.empty:
            st.line_chart(df_ndbi.set_index("Año")[["Media"]], use_container_width=True)
            with st.expander("Ver estadísticas NDBI (tabla)", expanded=False):
                st.dataframe(df_ndbi, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos suficientes para graficar esta serie.")

        st.markdown("---")

        # Zona específica en modo “panel” (no en tablas)
        if zones_gdf is not None and "zone_id" in zones_gdf.columns:
            st.markdown("**Zona específica**")
            zone_ids = zones_gdf["zone_id"].astype(int).sort_values().tolist()
            z = st.selectbox("zone_id", zone_ids, index=0)

            row = zones_gdf[zones_gdf["zone_id"].astype(int) == int(z)].iloc[0]
            a, b = st.columns(2)
            with a:
                if "perc_loss_veg" in row:
                    st.metric("Pérdida vegetación", f"{row['perc_loss_veg']:.2f}%")
            with b:
                if "perc_gain_built" in row:
                    st.metric("Aumento construido", f"{row['perc_gain_built']:.2f}%")

            # Comparación rápida como barras (compacto)
            if ("perc_loss_veg" in row) and ("perc_gain_built" in row):
                st.bar_chart(
                    pd.DataFrame(
                        {
                            "Métrica": ["% pérdida veg", "% aumento construido"],
                            "Valor": [row["perc_loss_veg"], row["perc_gain_built"]],
                        }
                    ).set_index("Métrica"),
                    use_container_width=True,
                )
        else:
            st.info("Zonas no disponibles para selección (revisa el GPKG).")


elif page == "Comparar":
    st.subheader("Comparador visual antes/después (DualMap)")
    st.caption("Comparación lado a lado para el índice seleccionado. Útil para evidenciar cambios en el tiempo.")

    dm = DualMap(location=center, zoom_start=12, tiles="OpenStreetMap")

    try:
        if comp_index == "NDVI":
            pL = NDVI.get(year_left)
            pR = NDVI.get(year_right)
            nameL, nameR = f"NDVI {year_left}", f"NDVI {year_right}"
        else:
            pL = NDBI.get(year_left)
            pR = NDBI.get(year_right)
            nameL, nameR = f"NDBI {year_left}", f"NDBI {year_right}"

        if file_ok(pL) and file_ok(pR):
            rgbaL, boundsL = raster_to_png_and_bounds(pL)
            rgbaR, boundsR = raster_to_png_and_bounds(pR)

            add_overlay(dm.m1, rgbaL, boundsL, nameL)
            add_overlay(dm.m2, rgbaR, boundsR, nameR)

            if show_zones and zones_gdf is not None:
                add_zones_layer(dm.m1, zones_gdf)
                add_zones_layer(dm.m2, zones_gdf)

            folium.LayerControl(collapsed=True).add_to(dm.m1)
            folium.LayerControl(collapsed=True).add_to(dm.m2)
        else:
            st.warning("No se encontraron rasters para los años seleccionados. Revisa data/processed/.")

    except Exception as e:
        st.error(f"Error generando comparador: {e}")

    st_folium(dm, width=None, height=650, use_container_width=True)


else:  # page == "Datos"
    st.subheader("Descargas y trazabilidad")
    st.caption("Descarga de resultados. Las tablas se muestran solo bajo demanda.")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**Archivos de salida**")
        if file_ok(ZONES_CSV):
            st.download_button(
                "Descargar CSV (cambios por zona)",
                data=ZONES_CSV.read_bytes(),
                file_name="cambios_por_zona_pudahuel.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No se encontró el CSV en outputs/. Genera el CSV en el Notebook 03.")

        if file_ok(ZONES_GPKG):
            st.download_button(
                "Descargar GPKG (zonas + métricas)",
                data=ZONES_GPKG.read_bytes(),
                file_name="cambios_por_zona.gpkg",
                mime="application/geopackage+sqlite3",
                use_container_width=True,
            )
        else:
            st.info("No se encontró el GPKG en data/processed/. Genera el GPKG en el Notebook 03.")

    with c2:
        st.markdown("**Vista de datos (opcional)**")
        if zones_gdf is None:
            st.info("No hay GPKG cargado.")
        else:
            with st.expander("Ver tabla de zonas (GPKG)", expanded=False):
                st.dataframe(
                    zones_gdf.drop(columns=["geometry"], errors="ignore"),
                    use_container_width=True,
                    hide_index=True,
                )


st.markdown("---")
st.caption("Curso: Desarrollo de Aplicaciones Geoinformáticas | Estudiantes: Diego Valdés y Valentina Campos | Prof.: Francisco Parra")
