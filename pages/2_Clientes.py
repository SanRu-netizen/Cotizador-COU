import streamlit as st
from database import init_db, get_session, Cliente

st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")
init_db()
st.title("👥 Clientes")

session = get_session()

tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo cliente"])

with tab1:
    clientes = session.query(Cliente).order_by(Cliente.nombre).all()
    if not clientes:
        st.info("No hay clientes registrados todavía.")
    for c in clientes:
        with st.expander(f"{c.nombre}  ·  {c.documento or 's/d'}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Teléfono:** {c.telefono or '-'}")
                st.write(f"**Correo:** {c.correo or '-'}")
                st.write(f"**Ciudad:** {c.ciudad or '-'}")
            with col2:
                st.write(f"**Dirección:** {c.direccion or '-'}")
                st.write(f"**Conjunto:** {c.conjunto or '-'}")
                st.write(f"**Torre / Apto:** {c.torre or '-'} / {c.apartamento or '-'}")
            if c.observaciones:
                st.write(f"**Observaciones:** {c.observaciones}")
            st.write(f"**Cotizaciones asociadas:** {len(c.cotizaciones)}")
            colb1, colb2 = st.columns([1, 5])
            if colb1.button("🗑️ Eliminar", key=f"del_cli_{c.id}"):
                if c.cotizaciones:
                    st.error("No se puede eliminar: tiene cotizaciones asociadas.")
                else:
                    session.delete(c)
                    session.commit()
                    st.rerun()

with tab2:
    with st.form("nuevo_cliente_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo *")
            documento = st.text_input("Documento")
            telefono = st.text_input("Teléfono")
            correo = st.text_input("Correo")
        with col2:
            direccion = st.text_input("Dirección")
            ciudad = st.text_input("Ciudad", value="Bogotá D.C.")
            colc1, colc2 = st.columns(2)
            conjunto = colc1.text_input("Conjunto")
            torre = colc2.text_input("Torre")
            apartamento = st.text_input("Apartamento")
        observaciones = st.text_area("Observaciones")
        enviado = st.form_submit_button("Guardar cliente", type="primary")
        if enviado:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                session.add(Cliente(
                    nombre=nombre, documento=documento, telefono=telefono, correo=correo,
                    direccion=direccion, ciudad=ciudad, conjunto=conjunto, torre=torre,
                    apartamento=apartamento, observaciones=observaciones,
                ))
                session.commit()
                st.success(f"Cliente '{nombre}' guardado correctamente.")
                st.rerun()

session.close()
