import os
import streamlit as st
from database import init_db, get_session, Configuracion

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")
init_db()
st.title("⚙️ Configuración")
st.caption("Estos datos aparecen automáticamente en el encabezado y la firma de cada PDF generado.")

session = get_session()
config = session.query(Configuracion).first()
if config is None:
    config = Configuracion()
    session.add(config)
    session.commit()

with st.form("config_form"):
    col1, col2 = st.columns(2)
    with col1:
        nombre_empresa = st.text_input("Nombre de la empresa", value=config.nombre_empresa)
        responsable = st.text_input("Responsable / Firma", value=config.responsable)
        ciudad = st.text_input("Ciudad", value=config.ciudad)
    with col2:
        celular = st.text_input("Celular", value=config.celular)
        correo = st.text_input("Correo", value=config.correo)

    objetivos = st.text_area("Objetivos (uno por línea, se insertan automáticamente)",
                              value=config.objetivos, height=120)
    texto_institucional = st.text_area(
        "Texto institucional de cierre (usa {empresa} para insertar el nombre de la empresa)",
        value=config.texto_institucional, height=180,
    )

    logo_file = st.file_uploader("Logo de la empresa (PNG o JPG)", type=["png", "jpg", "jpeg"])

    enviado = st.form_submit_button("💾 Guardar configuración", type="primary")
    if enviado:
        config.nombre_empresa = nombre_empresa
        config.responsable = responsable
        config.ciudad = ciudad
        config.celular = celular
        config.correo = correo
        config.objetivos = objetivos
        config.texto_institucional = texto_institucional

        if logo_file is not None:
            os.makedirs("assets", exist_ok=True)
            ext = os.path.splitext(logo_file.name)[1]
            ruta_logo = f"assets/logo_empresa{ext}"
            with open(ruta_logo, "wb") as f:
                f.write(logo_file.getbuffer())
            config.logo_path = ruta_logo

        session.commit()
        st.success("Configuración guardada correctamente.")

if config.logo_path and os.path.exists(config.logo_path):
    st.subheader("Logo actual")
    st.image(config.logo_path, width=200)

session.close()
