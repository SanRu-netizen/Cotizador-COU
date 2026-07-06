import streamlit as st
from database import init_db, get_session, Cotizacion, Cliente, Trabajo, Material
from seed_data import seed

st.set_page_config(
    page_title="Cotizador Obra Civil",
    page_icon="🏗️",
    layout="wide",
)

init_db()
seed()  # no hace nada si ya hay datos

st.title("🏗️ Cotizador de Obra Civil")
st.caption("Genera cotizaciones profesionales de mano de obra y materiales en minutos.")

session = get_session()
n_cotizaciones = session.query(Cotizacion).count()
n_clientes = session.query(Cliente).count()
n_trabajos = session.query(Trabajo).count()
n_materiales = session.query(Material).count()
valor_total_historico = sum(c.valor_total or 0 for c in session.query(Cotizacion).all())
session.close()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cotizaciones generadas", n_cotizaciones)
col2.metric("Clientes registrados", n_clientes)
col3.metric("Trabajos en catálogo", n_trabajos)
col4.metric("Materiales en catálogo", n_materiales)

st.divider()

st.subheader("¿Qué quieres hacer?")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 📝 Nueva Cotización")
    st.write("Crea una cotización seleccionando trabajos del catálogo inteligente. "
             "La descripción, los materiales y las observaciones se completan solas.")
    st.page_link("pages/1_Nueva_Cotizacion.py", label="Ir a Nueva Cotización", icon="➡️")
with c2:
    st.markdown("### 👥 Clientes")
    st.write("Consulta o registra los datos de tus clientes y sus proyectos.")
    st.page_link("pages/2_Clientes.py", label="Ir a Clientes", icon="➡️")
with c3:
    st.markdown("### 📚 Catálogos")
    st.write("Administra el catálogo de trabajos y de materiales que alimenta las cotizaciones.")
    st.page_link("pages/3_Catalogo_Trabajos.py", label="Catálogo de Trabajos", icon="➡️")
    st.page_link("pages/4_Catalogo_Materiales.py", label="Catálogo de Materiales", icon="➡️")

st.divider()
c4, c5 = st.columns(2)
with c4:
    st.markdown("### 🗂️ Historial")
    st.write(f"Valor total cotizado histórico: **${valor_total_historico:,.0f}**".replace(",", "."))
    st.page_link("pages/5_Historial.py", label="Ver historial de cotizaciones", icon="➡️")
with c5:
    st.markdown("### ⚙️ Configuración")
    st.write("Datos de la empresa, logo y textos institucionales que aparecen en el PDF.")
    st.page_link("pages/6_Configuracion.py", label="Ir a Configuración", icon="➡️")

st.divider()
st.info(
    "💡 **Recomendación de flujo:** primero completa el Catálogo de Trabajos y Materiales, "
    "luego registra tus Clientes, y finalmente genera cotizaciones seleccionando actividades "
    "desde el catálogo inteligente."
)
