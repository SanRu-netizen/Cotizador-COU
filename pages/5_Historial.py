import os
import streamlit as st
from database import init_db, get_session, Cotizacion

st.set_page_config(page_title="Historial", page_icon="🗂️", layout="wide")
init_db()
st.title("🗂️ Historial de Cotizaciones")

session = get_session()
cotizaciones = session.query(Cotizacion).order_by(Cotizacion.fecha.desc()).all()

if not cotizaciones:
    st.info("Todavía no se ha generado ninguna cotización.")

estados = ["Borrador", "Enviada", "Aprobada", "Rechazada"]

for c in cotizaciones:
    with st.expander(f"#{c.id}  ·  {c.cliente.nombre if c.cliente else 's/d'}  ·  "
                      f"{c.fecha}  ·  ${c.valor_total:,.0f}".replace(",", ".") + f"  ·  {c.estado}"):
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Tipo:** {c.tipo_cotizacion}")
        col2.write(f"**Plazo:** {c.plazo_dias_habiles} días hábiles")
        col3.write(f"**Garantía:** {c.garantia_meses} meses")
        st.write(f"**Ítems:** {len(c.items)}")
        for item in c.items:
            st.write(f"- {item.nombre_trabajo} ({item.cantidad} {item.unidad or ''})")

        nuevo_estado = st.selectbox("Estado", estados, index=estados.index(c.estado) if c.estado in estados else 0,
                                     key=f"estado_{c.id}")
        if nuevo_estado != c.estado:
            c.estado = nuevo_estado
            session.commit()
            st.success("Estado actualizado.")

        colb1, colb2 = st.columns([1, 1])
        if c.pdf_path and os.path.exists(c.pdf_path):
            with open(c.pdf_path, "rb") as f:
                colb1.download_button("⬇️ Descargar PDF", data=f.read(),
                                       file_name=os.path.basename(c.pdf_path),
                                       mime="application/pdf", key=f"dl_{c.id}")
        else:
            colb1.warning("PDF no disponible.")
        if colb2.button("🗑️ Eliminar cotización", key=f"delc_{c.id}"):
            session.delete(c)
            session.commit()
            st.rerun()

session.close()
