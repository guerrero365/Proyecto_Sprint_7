import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página (debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Dashboard de Vehículos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Cargar los datos
@st.cache_data
def load_data():
    """
    Carga los datos desde data/vehicles_us.csv. 
    Si la carpeta data no existe, usa vehicles_us.csv como respaldo.
    """
    try:
        df = pd.read_csv('data/vehicles_us.csv')
    except FileNotFoundError:
        df = pd.read_csv('vehicles_us.csv')
    
    # Limpieza básica rápida para mejorar la visualización
    df['model_year'] = pd.to_numeric(df['model_year'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['odometer'] = pd.to_numeric(df['odometer'], errors='coerce')
    df.dropna(subset=['price', 'model_year', 'model'], inplace=True)
    return df

df = load_data()

# 2. Título y subtítulo llamativos con emojis
st.title("🚗 Panel de Control de Mercado de Vehículos 🏎️")
st.markdown("### 📊 *Explora, analiza y descubre tendencias en la venta de autos usados* 🔍")
st.divider()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("⚙️ Filtros de Búsqueda")

# Filtro por tipo de vehículo
tipos_vehiculos = df['type'].dropna().unique().tolist()
tipo_seleccionado = st.sidebar.multiselect(
    "Selecciona el Tipo de Vehículo:",
    options=tipos_vehiculos,
    default=tipos_vehiculos[:3] if len(tipos_vehiculos) >= 3 else tipos_vehiculos
)

# Filtro por rango de precio
precio_min = int(df['price'].min())
precio_max = int(df['price'].max())
precio_max_visual = int(df['price'].quantile(0.99)) 

rango_precio = st.sidebar.slider(
    "Selecciona el Rango de Precio ($):",
    min_value=precio_min,
    max_value=precio_max_visual,
    value=(precio_min, precio_max_visual),
    step=500
)

# Filtro por estado del vehículo (condition)
condiciones = df['condition'].dropna().unique().tolist()
condicion_seleccionada = st.sidebar.multiselect(
    "Condición del Vehículo:",
    options=condiciones,
    default=condiciones
)

# --- APLICAR FILTROS ---
df_filtrado = df[
    (df['type'].isin(tipo_seleccionado)) &
    (df['price'] >= rango_precio[0]) &
    (df['price'] <= rango_precio[1]) &
    (df['condition'].isin(condicion_seleccionada))
]

# 3. Checkbox para mostrar/ocultar vista previa del DataFrame
st.markdown("#### 📋 Vista de Datos")
mostrar_datos = st.checkbox("Mostrar vista previa de los datos filtrados", value=False)

if mostrar_datos:
    # Mostramos las primeras 10 filas del dataframe filtrado
    st.dataframe(df_filtrado.head(10), use_container_width=True)
    st.caption(f"Mostrando 10 de {len(df_filtrado)} vehículos que coinciden con los filtros.")

st.divider()

# 4. Gráficos interactivos con Plotly Express
if df_filtrado.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados. Por favor, ajusta tu búsqueda.")
else:
    # Crear un diseño de columnas para los gráficos iniciales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Modelos Más Populares")
        top_modelos = df_filtrado['model'].value_counts().reset_index().head(10)
        top_modelos.columns = ['Modelo', 'Cantidad']
        
        fig_bar = px.bar(
            top_modelos, 
            x='Cantidad', 
            y='Modelo', 
            orientation='h',
            color='Cantidad',
            color_continuous_scale=px.colors.sequential.Blues,
            text_auto=True
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("#### ⛽ Distribución por Tipo de Transmisión")
        transmision_count = df_filtrado['transmission'].value_counts().reset_index()
        transmision_count.columns = ['Transmisión', 'Cantidad']
        
        fig_pie = px.pie(transmision_count, names='Transmisión', values='Cantidad', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # --- REQUISITOS DEL PROYECTO ---
    
    # 1. Uso de st.header()
    st.header("Análisis de Precios y Kilometraje")
    
    # Colocamos los botones uno al lado del otro
    bot1, bot2 = st.columns(2)
    
    with bot1:
        # 2. Botón para construir histograma
        hist_button = st.button('Construir histograma')
        
    with bot2:
        # 3. Botón para construir gráfico de dispersión
        scatter_button = st.button('Construir gráfico de dispersión')

    # Lógica al hacer clic en el botón del histograma
    if hist_button:
        st.write('Creación de un histograma para el conjunto de datos de anuncios de venta de coches (Distribución de Precios)')
        fig_hist = px.histogram(
            df_filtrado, 
            x='price', 
            nbins=50,
            color='condition',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Lógica al hacer clic en el botón del gráfico de dispersión
    if scatter_button:
        st.write('Creación de un gráfico de dispersión para comparar el Precio vs el Kilometraje (Odometer)')
        fig_scatter = px.scatter(
            df_filtrado,
            x="odometer",
            y="price",
            color="condition",
            opacity=0.5, # Hace los puntos un poco transparentes
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
