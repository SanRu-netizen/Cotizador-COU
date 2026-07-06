import streamlit as st
from database import init_db, get_session, Trabajo, Material, TrabajoMaterial

st.set_page_config(page_title="Catálogo de Trabajos", page_icon="🛠️", layout="wide")
init_db()
st.title("🛠️ Catálogo de Trabajos")
st.caption("Este es el catálogo inteligente: cada trabajo trae su descripción técnica, "
           "materiales sugeridos y observaciones, listos para usarse en una cotización.")

session = get_session()

tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo trabajo"])

with tab1:
    trabajos = session.query(Trabajo).order_by(Trabajo.categoria, Trabajo.nombre).all()
    categorias = sorted(set(t.categoria or "Sin categoría" for t in trabajos))
    filtro = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)

    for t in trabajos:
        if filtro != "Todas" and (t.categoria or "Sin categoría") != filtro:
            continue
        with st.expander(f"{t.nombre}  ·  {t.categoria or ''}"):
            nueva_desc = st.text_area("Descripción técnica", value=t.descripcion or "", key=f"d_{t.id}", height=90)
            nueva_obs = st.text_area("Observaciones", value=t.observaciones or "", key=f"o_{t.id}", height=70)
            nueva_unidad = st.text_input("Unidad", value=t.unidad or "", key=f"u_{t.id}")
            materiales_actuales = [tm.material.nombre for tm in t.materiales_rel]
            st.write("**Materiales sugeridos:** " + (", ".join(materiales_actuales) if materiales_actuales else "_ninguno_"))

            todos_materiales = session.query(Material).order_by(Material.nombre).all()
            nuevos_mats = st.multiselect(
                "Editar materiales sugeridos",
                options=[m.nombre for m in todos_materiales],
                default=materiales_actuales,
                key=f"m_{t.id}",
            )

            colb1, colb2 = st.columns([1, 1])
            if colb1.button("💾 Guardar cambios", key=f"save_{t.id}"):
                t.descripcion = nueva_desc
                t.observaciones = nueva_obs
                t.unidad = nueva_unidad
                # actualizar relación de materiales
                session.query(TrabajoMaterial).filter_by(id_trabajo=t.id).delete()
                mapa = {m.nombre: m.id for m in todos_materiales}
                for nombre_mat in nuevos_mats:
                    session.add(TrabajoMaterial(id_trabajo=t.id, id_material=mapa[nombre_mat]))
                session.commit()
                st.success("Trabajo actualizado.")
                st.rerun()
            if colb2.button("🗑️ Eliminar trabajo", key=f"delt_{t.id}"):
                session.delete(t)
                session.commit()
                st.rerun()

with tab2:
    with st.form("nuevo_trabajo_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del trabajo *")
        categoria = st.text_input("Categoría")
        unidad = st.text_input("Unidad", value="M2")
        descripcion = st.text_area("Descripción técnica", height=100)
        observaciones = st.text_area("Observaciones", height=70)
        todos_materiales = session.query(Material).order_by(Material.nombre).all()
        materiales_sel = st.multiselect("Materiales sugeridos", options=[m.nombre for m in todos_materiales])
        enviado = st.form_submit_button("Guardar trabajo", type="primary")
        if enviado:
            if not nombre:
                st.error("El nombre es obligatorio.")
            elif session.query(Trabajo).filter_by(nombre=nombre).first():
                st.error("Ya existe un trabajo con ese nombre.")
            else:
                t = Trabajo(nombre=nombre, categoria=categoria, unidad=unidad,
                            descripcion=descripcion, observaciones=observaciones)
                session.add(t)
                session.flush()
                mapa = {m.nombre: m.id for m in todos_materiales}
                for nombre_mat in materiales_sel:
                    session.add(TrabajoMaterial(id_trabajo=t.id, id_material=mapa[nombre_mat]))
                session.commit()
                st.success(f"Trabajo '{nombre}' agregado al catálogo.")
                st.rerun()

session.close()
