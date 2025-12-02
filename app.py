import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from streamlit_carousel import carousel
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from pathlib import Path
import math

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL Y CONSTANTES
# ==============================================================================

# URL del Logo Oficial
LOGO_URL = "https://images.ligup2.com/eyJidWNrZXQiOiJsaWd1cC12MiIsImtleSI6InB1ZW50ZWFsdG8vdXNlcnMvNDg3N19sb2dvX2NvcnBvX2RlcG9ydGVzX2FfY29sb3JfZm9uZG9fYmxhbmNvX2NvcHkucG5nIiwiZWRpdHMiOnsicmVzaXplIjp7IndpZHRoIjoyMDAwLCJoZWlnaHQiOjIwMDAsImZpdCI6Imluc2lkZSJ9LCJyb3RhdGUiOm51bGx9fQ=="

st.set_page_config(
    page_title="Deportes Puente Alto | Portal Oficial",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes de Configuración
API_KEY_PA = "hLzRbd12XMz2dFpIgwwCyRXgpCp7dc7U5hsyZp4l"
API_URL_PA = "http://mpuentealto.cloudapi.junar.com/api/v2/visualizations/TALLE-DEPOR-2019"

# Paleta de Colores Corporativa
COLOR_PRIMARY = "#002B5C"  # Azul oscuro institucional
COLOR_ACCENT = "#E65100"   # Naranja vibrante
COLOR_BG = "#F8F9FA"       # Gris muy claro para fondo

# ==============================================================================
# 2. ESTILOS CSS AVANZADOS (UI/UX)
# ==============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Reset */
    .stApp {{
        background-color: {COLOR_BG};
        font-family: 'Roboto', sans-serif;
    }}
    
    /* Encabezado Principal */
    .header-container {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #004080 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }}
    .header-title {{ font-size: 2.5rem; font-weight: 700; margin: 0; }}
    .header-subtitle {{ font-size: 1.1rem; opacity: 0.9; font-weight: 300; }}

    /* Tarjetas de Talleres */
    .taller-card {{
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        margin-bottom: 1rem;
    }}
    .taller-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
    }}
    .card-img {{
        height: 160px;
        width: 100%;
        background-size: cover;
        background-position: center;
    }}
    .card-content {{ padding: 1.2rem; flex-grow: 1; display: flex; flex-direction: column; }}
    .card-title {{ 
        color: {COLOR_PRIMARY}; 
        font-weight: 700; 
        font-size: 1.1rem; 
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        line-height: 1.3;
        border-bottom: 2px solid {COLOR_ACCENT};
        padding-bottom: 5px;
        display: inline-block;
    }}
    .card-info {{ 
        font-size: 0.9rem; 
        color: #555; 
        margin-bottom: 0.4rem; 
        display: flex; 
        align-items: center; 
        gap: 5px; 
    }}
    .card-info strong {{ color: {COLOR_PRIMARY}; min-width: 60px; }}
    
    .card-footer {{ margin-top: auto; padding-top: 10px; border-top: 1px solid #eee; }}
    .tag-badge {{
        background-color: #E3F2FD;
        color: {COLOR_PRIMARY};
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
    }}
    
    /* Métricas - Ajustadas para fila superior */
    div[data-testid="stMetric"] {{
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border-top: 4px solid {COLOR_ACCENT};
        text-align: center;
    }}

    /* Contenedor Gráficos */
    .chart-container {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-top: 20px;
    }}
    .chart-header {{
        color: {COLOR_PRIMARY};
        font-weight: 700;
        margin-bottom: 15px;
        font-size: 1.1rem;
        border-left: 4px solid {COLOR_ACCENT};
        padding-left: 10px;
    }}

    /* Sidebar personalizado */
    section[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }}
    
    /* Tabs */
    .stTabs [aria-selected="true"] {{
        color: {COLOR_ACCENT} !important;
        border-bottom-color: {COLOR_ACCENT} !important;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. GESTIÓN DE DATOS Y LÓGICA
# ==============================================================================

def get_taller_image(nombre_taller):
    """Retorna una URL de imagen temática."""
    nombre = str(nombre_taller).lower()
    mapa_imagenes = {
        'futbol': "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=600",
        'fútbol': "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=600",
        'baile': "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600",
        'zumba': "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600",
        'yoga': "https://images.unsplash.com/photo-1599447421405-0e32096d30fd?q=80&w=600",
        'pilates': "https://images.unsplash.com/photo-1599447421405-0e32096d30fd?q=80&w=600",
        'tenis': "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=600",
        'karate': "https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=600",
        'taekwondo': "https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=600",
        'basket': "https://images.unsplash.com/photo-1546519638-68e109498ee2?q=80&w=600",
        'natacion': "https://images.unsplash.com/photo-1530549387789-4c1017266635?q=80&w=600",
        'agua': "https://images.unsplash.com/photo-1530549387789-4c1017266635?q=80&w=600",
        'gimnasia': "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?q=80&w=600",
        'patin': "https://images.unsplash.com/photo-1533561972580-b2b93240212f?q=80&w=600"
    }
    
    for key, url in mapa_imagenes.items():
        if key in nombre:
            return url
    return "https://img.freepik.com/free-vector/gradient-dynamic-blue-lines-background_23-2148995756.jpg"

@st.cache_data(ttl=3600, show_spinner=False)
def cargar_datos_hibridos():
    df = pd.DataFrame()
    origen = "Desconocido"
    
    try:
        response = requests.get(API_URL_PA, params={"auth_key": API_KEY_PA, "output": "json"}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            origen = "API Municipal (Online)"
    except Exception:
        pass

    if df.empty:
        try:
            csv_path = Path(__file__).parent / "Talleres_deporte.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                origen = "Respaldo Local (Offline)"
        except Exception:
            pass
            
    if not df.empty:
        rename_map = {
            'Villa/ población/sede': 'Recinto', 'RECINTO': 'Recinto',
            'Calidad del taller': 'Costo',
            'Latitud': 'lat', 'LATITUD': 'lat',
            'Longitud': 'lon', 'LONGITUD': 'lon',
            'Inscripción': 'Inscripcion', 'Días': 'Dias', 'DIAS': 'Dias',
            'TALLER': 'Taller', 'HORARIO': 'Horario'
        }
        df.rename(columns=lambda x: rename_map.get(x, x), inplace=True)
        
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        if 'Taller' in df.columns: df['Taller'] = df['Taller'].astype(str).str.strip().str.upper()
        if 'Recinto' in df.columns: df['Recinto'] = df['Recinto'].astype(str).str.strip()
        
        def clasificar_cohorte(row):
            texto = (str(row.get('Edad', '')) + " " + str(row.get('Taller', ''))).lower()
            if any(x in texto for x in ['60', 'mayor', 'tercera', 'adulto mayor']): return "Adulto Mayor"
            elif any(x in texto for x in ['12', '15', '17', 'joven', 'estudiante', 'juvenil']): return "Jóvenes"
            elif any(x in texto for x in ['niñ', '4 a', '5 a', 'infant', 'kids', 'semill']): return "Infantil"
            return "Adultos/Todo Público"

        if 'Cohorte' not in df.columns:
            df['Cohorte'] = df.apply(clasificar_cohorte, axis=1)

    return df, origen

@st.cache_data(ttl=1800)
def obtener_clima():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.6167&longitude=-70.5833&current_weather=true"
        r = requests.get(url, timeout=2)
        return r.json().get('current_weather') if r.status_code == 200 else None
    except:
        return None

# ==============================================================================
# 4. CARGA DE DATOS
# ==============================================================================
df_talleres, source_status = cargar_datos_hibridos()

# ==============================================================================
# 5. SIDEBAR (FILTROS Y NAVEGACIÓN)
# ==============================================================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("### Filtros de Búsqueda")
    
    if "API" in source_status:
        st.caption(f"Estado: Conectado")
    else:
        st.warning(f"Estado: {source_status}")

    st.divider()

    f_cohorte = st.selectbox("Público Objetivo", ["Todos"] + sorted(list(df_talleres['Cohorte'].unique()))) if not df_talleres.empty else "Todos"
    
    recintos_list = sorted(df_talleres['Recinto'].unique()) if not df_talleres.empty else []
    f_recinto = st.selectbox("Recinto Deportivo", ["Todos"] + recintos_list)

    f_dias = st.multiselect("Días Disponibles", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

    st.divider()
    with st.expander("Información"):
        st.markdown("""
        **Corporación Municipal de Deportes**
        
        Plataforma de visualización de talleres deportivos.
        
        Av. Concha y Toro 462
        deportes@puentealto.cl
        """)

# Lógica de Filtrado
df_filtrado = df_talleres.copy()
if not df_filtrado.empty:
    if f_cohorte != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Cohorte'] == f_cohorte]
    if f_recinto != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Recinto'] == f_recinto]
    if f_dias:
        pattern = '|'.join(f_dias)
        df_filtrado = df_filtrado[df_filtrado['Dias'].str.contains(pattern, case=False, na=False)]

# ==============================================================================
# 6. INTERFAZ PRINCIPAL
# ==============================================================================

st.markdown("""
<div class="header-container">
    <h1 class="header-title">CORPORACIÓN DE DEPORTES</h1>
    <div class="header-subtitle">Puente Alto - Capital del Deporte</div>
</div>
""", unsafe_allow_html=True)

# Pestañas sin emojis
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inicio", "Talleres", "Mapa", "Programación", "Noticias"])

# --- TAB 1: DASHBOARD (REDISEÑADO) ---
with tab1:
    # 1. KPIs en Fila Superior (Horizontal)
    st.markdown("### Resumen General")
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    
    with c_kpi1:
        st.metric("Talleres Disponibles", len(df_filtrado) if not df_filtrado.empty else 0)
    with c_kpi2:
        st.metric("Sedes Activas", df_filtrado['Recinto'].nunique() if not df_filtrado.empty else 0)
    with c_kpi3:
        st.metric("Disciplinas", df_filtrado['Taller'].nunique() if not df_filtrado.empty else 0)
    with c_kpi4:
        clima = obtener_clima()
        val_clima = f"{clima['temperature']}°C" if clima else "--"
        st.metric("Temperatura Actual", val_clima)

    st.write("") # Espaciador
    st.write("") 

    # 2. Carousel EXPANDIDO (Ancho Completo)
    # Usamos container_height=500 para mayor resolución vertical
    carousel(items=[
        {"title": "Escuelas de Fútbol", "text": "Formando campeones", "img": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1200"},
        {"title": "Vida Sana", "text": "Programas gratuitos", "img": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?q=80&w=1200"},
        {"title": "Comunidad", "text": "Participación activa", "img": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1200"},
        {"title": "Instalaciones", "text": "Infraestructura de calidad", "img": "https://images.unsplash.com/photo-1577223625816-7546f13df25d?q=80&w=1200"}
    ], container_height=500)

    # 3. Gráficos Abajo
    st.write("")
    st.markdown("### Estadísticas")
    
    if not df_filtrado.empty:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2, gap="large")
            
            with c1:
                st.markdown('<div class="chart-header">Distribución por Público</div>', unsafe_allow_html=True)
                chart_data = df_filtrado['Cohorte'].value_counts().sort_values(ascending=True)
                st.bar_chart(chart_data, color=COLOR_PRIMARY, horizontal=True, height=300)
                
            with c2:
                st.markdown('<div class="chart-header">Disciplinas Más Populares</div>', unsafe_allow_html=True)
                top_talleres = df_filtrado['Taller'].value_counts().head(5).sort_values(ascending=True)
                st.bar_chart(top_talleres, color=COLOR_ACCENT, horizontal=True, height=300)
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: CATÁLOGO DE TALLERES ---
with tab2:
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("Buscar taller por nombre", placeholder="Ej: Yoga, Fútbol, Zumba...")
    
    df_display = df_filtrado.copy()
    if search_term:
        df_display = df_display[df_display['Taller'].str.contains(search_term, case=False, na=False)]

    items_per_page = 9
    if not df_display.empty:
        total_pages = math.ceil(len(df_display) / items_per_page)
        
        if total_pages > 1:
            c_prev, c_page, c_next = st.columns([1, 2, 1])
            with c_page:
                current_page = st.number_input("Página", min_value=1, max_value=total_pages, value=1)
        else:
            current_page = 1
            
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        batch = df_display.iloc[start_idx:end_idx]

        rows = st.columns(3)
        for idx, row in enumerate(batch.iterrows()):
            data = row[1]
            with rows[idx % 3]:
                st.markdown(f"""
                <div class="taller-card">
                    <div class="card-img" style="background-image: url('{get_taller_image(data['Taller'])}');"></div>
                    <div class="card-content">
                        <div class="card-title">{data['Taller']}</div>
                        <div class="card-info"><strong>Sede:</strong> {data.get('Recinto', 'S/I')[:25]}...</div>
                        <div class="card-info"><strong>Días:</strong> {data.get('Dias', 'Por definir')}</div>
                        <div class="card-info"><strong>Hora:</strong> {data.get('Horario', 'Consultar')}</div>
                        <div class="card-footer">
                            <span class="tag-badge">{data.get('Cohorte', 'General')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        st.caption(f"Mostrando {len(batch)} de {len(df_display)} registros.")
    else:
        st.info("No se encontraron resultados.")

# --- TAB 3: MAPA GEOESPACIAL ---
with tab3:
    st.markdown("### Ubicación de Sedes")
    
    df_map = df_filtrado.dropna(subset=['lat', 'lon'])
    
    if not df_map.empty:
        center_lat = df_map['lat'].mean()
        center_lon = df_map['lon'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB positron")
        marker_cluster = MarkerCluster().add_to(m)
        
        for _, row in df_map.iterrows():
            info_html = f"""
            <div style="font-family: Roboto, sans-serif; font-size: 14px; width: 220px;">
                <h4 style="margin: 0; color: #002B5C; border-bottom: 2px solid #E65100; padding-bottom: 5px;">
                    {row['Taller']}
                </h4>
                <p style="margin: 5px 0 0 0; font-weight: bold; font-size: 12px; color: #666;">
                    {row['Recinto']}
                </p>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #eee;">
                <ul style="padding-left: 15px; margin: 0; font-size: 12px; color: #333; list-style-type: none;">
                    <li style="margin-bottom: 3px;"><strong>Días:</strong> {row.get('Dias', 'Por confirmar')}</li>
                    <li style="margin-bottom: 3px;"><strong>Horario:</strong> {row.get('Horario', 'Por confirmar')}</li>
                    <li><strong>Público:</strong> {row.get('Cohorte', 'General')}</li>
                </ul>
            </div>
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(info_html, max_width=260),
                tooltip=f"{row['Taller']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)
            
        st_folium(m, height=500, use_container_width=True)
    else:
        st.warning("No hay información geográfica disponible.")

# --- TAB 4: PROGRAMACIÓN ---
with tab4:
    st.markdown("### Programación Detallada")
    
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado[['Taller', 'Recinto', 'Dias', 'Horario', 'Cohorte', 'Costo']],
            use_container_width=True,
            column_config={
                "Taller": st.column_config.TextColumn("Disciplina", width="medium"),
                "Recinto": st.column_config.TextColumn("Lugar", width="medium"),
                "Costo": st.column_config.TextColumn("Estado"),
            },
            hide_index=True
        )
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Reporte (CSV)",
            data=csv,
            file_name='programacion_deportes_puente_alto.csv',
            mime='text/csv',
        )
    else:
        st.info("No hay datos disponibles con los filtros actuales.")

# --- TAB 5: NOTICIAS ---
with tab5:
    st.markdown("### Actualidad Deportiva")
    
    @st.cache_data(ttl=3600)
    def cargar_noticias():
        try:
            url_news = "https://news.google.com/rss/search?q=Deporte+Puente+Alto&hl=es-419&gl=CL&ceid=CL:es-419"
            resp = requests.get(url_news, timeout=4)
            root = ET.fromstring(resp.content)
            return root.findall('./channel/item')[:6]
        except:
            return []

    items = cargar_noticias()
    
    if items:
        grid_news = st.columns(2)
        for i, item in enumerate(items):
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text[:16]
            
            with grid_news[i % 2]:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid {COLOR_ACCENT}; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-weight: bold; color: {COLOR_PRIMARY}; margin-bottom: 5px;">{title}</div>
                    <div style="font-size: 0.8rem; color: gray; margin-bottom: 10px;">Fecha: {pub_date}</div>
                    <a href="{link}" target="_blank" style="text-decoration: none; color: {COLOR_ACCENT}; font-weight: 600; font-size: 0.9rem;">Leer nota completa →</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No se pudieron cargar las noticias en este momento.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.8rem;'>"
    "© 2025 Corporación Municipal de Deportes de Puente Alto - Desarrollado con Streamlit"
    "</div>", 
    unsafe_allow_html=True
)