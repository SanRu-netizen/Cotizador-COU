import os
from datetime import date

import streamlit as st

from database import (
    init_db, get_session, Cliente, Trabajo, Nota, Cotizacion, ItemCotizacion, Configuracion
)
from utils import construir_texto_forma_pago, formato_moneda, generar_logo_placeholder
from pdf_generator import generar_pdf_cotizacion

st.set_page_config(page_title="Nueva Cotización", page_icon="📝", layout="wide")
init_db()

st.title("📝 Nueva Cotización")

if "carrito" not in st.session_state:
    st.session_state.carrito = []  # lista de dicts de items

session = get_session()

# ==========================================================================
# 1. Datos del cliente
# ==========================================================================
st.header("1. Datos del Cliente")

clientes = session.query(Cliente).order_by(Cliente.nombre).all()
opciones_cliente = ["➕ Nuevo cliente"] + [f"{c.nombre} ({c.documento or 's/d'})" for c in clientes]
seleccion_cliente = st.selectbox("Cliente", opciones_cliente)

if seleccion_cliente == "➕ Nuevo cliente":
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
    observaciones_cliente = st.text_area("Observaciones del cliente", height=70)
    cliente_id_existente = None
else:
    idx = opciones_cliente.index(seleccion_cliente) - 1
    cli = clientes[idx]
    cliente_id_existente = cli.id
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nombre completo", value=cli.nombre, disabled=True)
        st.text_input("Documento", value=cli.documento or "", disabled=True)
        st.text_input("Teléfono", value=cli.telefono or "", disabled=True)
    with col2:
        st.text_input("Dirección", value=cli.direccion or "", disabled=True)
        st.text_input("Torre", value=cli.torre or "", disabled=True)
        st.text_input("Apartamento", value=cli.apartamento or "", disabled=True)

st.divider()

# ==========================================================================
# 2. Datos del proyecto
# ==========================================================================
st.header("2. Datos del Proyecto")
col1, col2, col3 = st.columns(3)
with col1:
    tipo_cotizacion = st.radio("Tipo de cotización", ["Mano de obra", "Mano de obra + materiales"])
with col2:
    plazo_dias = st.number_input("Tiempo de ejecución (días hábiles)", min_value=1, value=40, step=1)
with col3:
    garantia_meses = st.number_input("Garantía (meses)", min_value=0, value=6, step=1)

col4, col5 = st.columns(2)
with col4:
    anticipo_pct = st.slider("Anticipo (%)", 0, 100, 30, step=5)
with col5:
    tipo_pago = st.selectbox("Tipo de pagos", ["Semanales", "Quincenales", "Mensuales"])

st.divider()

# ==========================================================================
# 3. Seleccionar trabajos (catálogo inteligente)
# ==========================================================================
st.header("3. Seleccionar Trabajos")
st.caption("Al seleccionar un trabajo del catálogo, la descripción y los materiales se cargan automáticamente. Puedes editarlos antes de agregarlo.")

trabajos = session.query(Trabajo).order_by(Trabajo.categoria, Trabajo.nombre).all()
mapa_trabajos = {f"{t.nombre}  ·  {t.categoria or ''}": t for t in trabajos}

colA, colB = st.columns([3, 1])
with colA:
    seleccion_trabajo = st.selectbox("Trabajo del catálogo", list(mapa_trabajos.keys()) if mapa_trabajos else [])
with colB:
    cantidad_add = st.number_input("Cantidad", min_value=0.0, value=1.0, step=1.0)

if mapa_trabajos and st.button("➕ Agregar trabajo a la cotización", use_container_width=True):
    t = mapa_trabajos[seleccion_trabajo]
    materiales_txt = "\n".join(
        f"- {tm.material.nombre}" + (f" ({tm.material.marca})" if tm.material.marca else "")
        for tm in t.materiales_rel
    )
    st.session_state.carrito.append({
        "trabajo_id": t.id,
        "nombre": t.nombre,
        "descripcion": t.descripcion or "",
        "materiales_texto": materiales_txt,
        "cantidad": cantidad_add,
        "unidad": t.unidad,
        "observacion": t.observaciones or "",
    })
    st.success(f"'{t.nombre}' agregado a la cotización.")

if not trabajos:
    st.warning("No hay trabajos en el catálogo todavía. Ve a 'Catálogo de Trabajos' para crear alguno.")

st.subheader("Trabajos agregados")
if not st.session_state.carrito:
    st.info("Aún no has agregado trabajos a esta cotización.")
else:
    for i, item in enumerate(st.session_state.carrito):
        with st.expander(f"{i+1}. {item['nombre']}  ·  cantidad: {item['cantidad']} {item['unidad'] or ''}", expanded=False):
            item["descripcion"] = st.text_area("Descripción", value=item["descripcion"], key=f"desc_{i}", height=90)
            item["materiales_texto"] = st.text_area("Materiales incluidos", value=item["materiales_texto"], key=f"mat_{i}", height=90)
            colx, coly, colz = st.columns([1, 1, 1])
            item["cantidad"] = colx.number_input("Cantidad", value=float(item["cantidad"]), key=f"cant_{i}")
            item["unidad"] = coly.text_input("Unidad", value=item["unidad"] or "", key=f"uni_{i}")
            item["observacion"] = st.text_input("Observación", value=item.get("observacion", ""), key=f"obs_{i}")
            if colz.button("🗑️ Quitar", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()

st.divider()

# ==========================================================================
# 4. Condiciones comerciales
# ==========================================================================
st.header("4. Condiciones Comerciales")
valor_total = st.number_input("Valor total de la cotización (COP)", min_value=0, step=100000, value=0)
st.caption(f"Valor formateado: {formato_moneda(valor_total)}")

notas_disponibles = session.query(Nota).all()
notas_marcadas = st.multiselect(
    "Notas (materiales suministrados por el propietario, etc.)",
    options=[n.texto for n in notas_disponibles],
)
nota_extra = st.text_input("Otra nota (opcional, se añade a la lista anterior si la escribes)")
if nota_extra:
    notas_marcadas = notas_marcadas + [nota_extra]

observaciones_generales = st.text_area("Notas adicionales para el documento (opcional)", height=70)

st.divider()

# ==========================================================================
# 5. Vista previa
# ==========================================================================
st.header("5. Vista previa")

config = session.query(Configuracion).first()
if config is None:
    config = Configuracion()
    session.add(config)
    session.commit()

forma_pago_texto = construir_texto_forma_pago(anticipo_pct, tipo_pago)

nombre_cliente_preview = nombre if seleccion_cliente == "➕ Nuevo cliente" else clientes[opciones_cliente.index(seleccion_cliente) - 1].nombre

with st.container(border=True):
    st.markdown(f"**Cliente:** {nombre_cliente_preview or '(sin definir)'}")
    st.markdown(f"**Tipo de cotización:** {tipo_cotizacion}")
    st.markdown(f"**Plazo:** {plazo_dias} días hábiles  |  **Garantía:** {garantia_meses} meses")
    st.markdown(f"**Forma de pago:** {forma_pago_texto}")
    st.markdown(f"**Valor total:** {formato_moneda(valor_total)}")
    if notas_marcadas:
        st.markdown("**Notas:** " + "; ".join(notas_marcadas))
    st.markdown("**Trabajos incluidos:**")
    if st.session_state.carrito:
        for i, item in enumerate(st.session_state.carrito, start=1):
            st.markdown(f"{i}. {item['nombre']} — {item['cantidad']} {item['unidad'] or ''}")
    else:
        st.markdown("_Sin trabajos agregados_")

st.divider()

# ==========================================================================
# 6. Generar PDF
# ==========================================================================
st.header("6. Generar PDF")

puede_generar = bool(st.session_state.carrito) and (
    (seleccion_cliente == "➕ Nuevo cliente" and nombre) or
    (seleccion_cliente != "➕ Nuevo cliente")
)

if not puede_generar:
    st.warning("Completa al menos el nombre del cliente y agrega un trabajo para poder generar el PDF.")

if st.button("📄 Generar Cotización en PDF", type="primary", disabled=not puede_generar):
    # Guardar / obtener cliente
    if seleccion_cliente == "➕ Nuevo cliente":
        nuevo_cliente = Cliente(
            nombre=nombre, documento=documento, telefono=telefono, correo=correo,
            direccion=direccion, ciudad=ciudad, conjunto=conjunto, torre=torre,
            apartamento=apartamento, observaciones=observaciones_cliente,
        )
        session.add(nuevo_cliente)
        session.commit()
        cliente_obj = nuevo_cliente
    else:
        cliente_obj = session.get(Cliente, cliente_id_existente)

    cotizacion = Cotizacion(
        id_cliente=cliente_obj.id,
        fecha=date.today(),
        tipo_cotizacion=tipo_cotizacion,
        valor_total=valor_total,
        plazo_dias_habiles=plazo_dias,
        forma_pago_anticipo=anticipo_pct,
        forma_pago_tipo=tipo_pago,
        forma_pago_texto=forma_pago_texto,
        garantia_meses=garantia_meses,
        notas_ids="",
        observaciones_generales=observaciones_generales,
        estado="Borrador",
    )
    session.add(cotizacion)
    session.commit()

    for orden, item in enumerate(st.session_state.carrito, start=1):
        session.add(ItemCotizacion(
            id_cotizacion=cotizacion.id,
            id_trabajo=item["trabajo_id"],
            orden=orden,
            nombre_trabajo=item["nombre"],
            descripcion=item["descripcion"],
            cantidad=item["cantidad"],
            unidad=item["unidad"],
            observacion=item.get("observacion", ""),
            materiales_texto=item["materiales_texto"],
        ))
    session.commit()

    items_db = session.query(ItemCotizacion).filter_by(id_cotizacion=cotizacion.id).order_by(ItemCotizacion.orden).all()

    logo_path = config.logo_path
    if not logo_path or not os.path.exists(logo_path):
        logo_path = generar_logo_placeholder(config.nombre_empresa or "CU")

    empresa = {
        "nombre_empresa": config.nombre_empresa,
        "responsable": config.responsable,
        "celular": config.celular,
        "correo": config.correo,
        "ciudad": config.ciudad,
        "logo_path": logo_path,
        "objetivos": config.objetivos,
        "texto_institucional": config.texto_institucional,
    }

    os.makedirs("data/pdfs", exist_ok=True)
    output_path = f"data/pdfs/Cotizacion_{cotizacion.id}_{cliente_obj.nombre.replace(' ', '_')}.pdf"
    generar_pdf_cotizacion(cotizacion, cliente_obj, items_db, empresa, notas_marcadas, output_path)

    cotizacion.pdf_path = output_path
    session.commit()

    with open(output_path, "rb") as f:
        st.download_button(
            "⬇️ Descargar PDF de la cotización",
            data=f.read(),
            file_name=os.path.basename(output_path),
            mime="application/pdf",
            type="primary",
        )
    st.success("¡Cotización generada y guardada en el historial!")
    st.session_state.carrito = []

session.close()
