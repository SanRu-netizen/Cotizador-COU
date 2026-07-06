import streamlit as st
from database import init_db, get_session, Material

st.set_page_config(page_title="Catálogo de Materiales", page_icon="🧱", layout="wide")
init_db()
st.title("🧱 Catálogo de Materiales")

session = get_session()

tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo material"])

with tab1:
    materiales = session.query(Material).order_by(Material.nombre).all()
    busqueda = st.text_input("Buscar material")
    filas = []
    for m in materiales:
        if busqueda and busqueda.lower() not in m.nombre.lower():
            continue
        filas.append({"ID": m.id, "Material": m.nombre, "Marca": m.marca or "", "Unidad": m.unidad or ""})
    st.dataframe(filas, use_container_width=True, hide_index=True)

    st.subheader("Editar / eliminar")
    if materiales:
        nombres = [m.nombre for m in materiales]
        elegido = st.selectbox("Selecciona un material", nombres)
        m = next(x for x in materiales if x.nombre == elegido)
        col1, col2, col3 = st.columns(3)
        nuevo_nombre = col1.text_input("Nombre", value=m.nombre, key=f"nm_{m.id}")
        nueva_marca = col2.text_input("Marca", value=m.marca or "", key=f"mm_{m.id}")
        nueva_unidad = col3.text_input("Unidad", value=m.unidad or "", key=f"mu_{m.id}")
        colb1, colb2 = st.columns([1, 1])
        if colb1.button("💾 Guardar cambios"):
            m.nombre = nuevo_nombre
            m.marca = nueva_marca
            m.unidad = nueva_unidad
            session.commit()
            st.success("Material actualizado.")
            st.rerun()
        if colb2.button("🗑️ Eliminar material"):
            if m.trabajos_rel:
                st.error("No se puede eliminar: está asociado a uno o más trabajos del catálogo.")
            else:
                session.delete(m)
                session.commit()
                st.rerun()

with tab2:
    with st.form("nuevo_material_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del material *")
        marca = st.text_input("Marca (opcional)")
        unidad = st.text_input("Unidad", value="Unidad")
        enviado = st.form_submit_button("Guardar material", type="primary")
        if enviado:
            if not nombre:
                st.error("El nombre es obligatorio.")
            elif session.query(Material).filter_by(nombre=nombre).first():
                st.error("Ya existe un material con ese nombre.")
            else:
                session.add(Material(nombre=nombre, marca=marca, unidad=unidad))
                session.commit()
                st.success(f"Material '{nombre}' agregado al catálogo.")
                st.rerun()

session.close()
