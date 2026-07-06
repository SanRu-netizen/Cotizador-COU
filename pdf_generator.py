"""
Genera el PDF de la cotización con el mismo formato de la plantilla de
referencia: encabezado con fecha y logo, tabla de descripción de trabajos,
tabla de materiales incluidos con valor total, y página de condiciones
comerciales con cierre institucional y firma.
"""
import os
from datetime import date

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
)

HEADER_GRAY = colors.HexColor("#E6E6E6")
ROW_GRAY = colors.HexColor("#F2F2F2")
BORDER_GRAY = colors.HexColor("#BFBFBF")

MESES_ES = {
    1: "ene.", 2: "feb.", 3: "mar.", 4: "abr.", 5: "may.", 6: "jun.",
    7: "jul.", 8: "ago.", 9: "sep.", 10: "oct.", 11: "nov.", 12: "dic.",
}


def fecha_formateada(d: date) -> str:
    return f"{d.day:02d} de {MESES_ES[d.month]} del {d.year}"


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Cell", fontName="Helvetica", fontSize=9.5, leading=13,
    ))
    styles.add(ParagraphStyle(
        name="CellBold", parent=styles["Cell"], fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="CellCenter", parent=styles["Cell"], alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="TitleDoc", fontName="Helvetica-Bold", fontSize=13, leading=16,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=10.5, leading=15,
    ))
    styles.add(ParagraphStyle(
        name="Cond", fontName="Helvetica-Bold", fontSize=11, leading=14,
        spaceBefore=10, spaceAfter=4,
    ))
    return styles


def _make_header_footer(empresa: dict, fecha_str: str):
    """Devuelve una función para dibujar encabezado (fecha + logo) en cada página."""
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.drawString(2 * cm, letter[1] - 1.6 * cm, f"{empresa.get('ciudad', 'Bogotá D.C.')}   {fecha_str}")

        logo_path = empresa.get("logo_path")
        if logo_path and os.path.exists(logo_path):
            try:
                canvas.drawImage(
                    logo_path, letter[0] - 4.3 * cm, letter[1] - 2.1 * cm,
                    width=2.3 * cm, height=1.4 * cm, preserveAspectRatio=True, mask="auto"
                )
            except Exception:
                pass
        canvas.restoreState()
    return _draw


def generar_pdf_cotizacion(cotizacion, cliente, items, empresa: dict, notas_texto: list,
                            output_path: str):
    """
    cotizacion: objeto Cotizacion (o dict con los mismos campos)
    cliente: objeto Cliente
    items: lista de ItemCotizacion (con nombre_trabajo, descripcion, materiales_texto)
    empresa: dict con nombre_empresa, responsable, celular, correo, ciudad, logo_path, objetivos, texto_institucional
    notas_texto: lista de strings con las notas seleccionadas (materiales por el propietario, etc.)
    """
    styles = _styles()
    fecha_str = fecha_formateada(cotizacion.fecha if cotizacion.fecha else date.today())

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=2.3 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )

    story = []

    # ---- Título y datos del cliente -------------------------------------------------
    tipo = "Cotización de Mano de Obra" if cotizacion.tipo_cotizacion == "Mano de obra" \
        else "Cotización de Mano de Obra y Materiales"
    story.append(Paragraph(tipo, styles["TitleDoc"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b><i>Cliente:</i></b> {cliente.nombre}", styles["Body"]))
    story.append(Spacer(1, 4))
    ubicacion = cliente.ubicacion_texto()
    if ubicacion:
        story.append(Paragraph(f"<b><i>Ubicación:</i></b> {ubicacion}.", styles["Body"]))
    story.append(Spacer(1, 14))

    # ---- Tabla: Descripción de la cotización -----------------------------------------
    story.append(_titulo_seccion("DESCRIPCIÓN DE LA COTIZACIÓN", styles))
    data = [[
        Paragraph("<b>ITEM</b>", styles["CellCenter"]),
        Paragraph("<b>Trabajos para realizar:</b>", styles["CellBold"]),
        Paragraph("<b>Descripción:</b>", styles["CellBold"]),
    ]]
    for i, item in enumerate(items, start=1):
        data.append([
            Paragraph(str(i), styles["CellCenter"]),
            Paragraph(item.nombre_trabajo or "", styles["Cell"]),
            Paragraph(item.descripcion or "", styles["Cell"]),
        ])
    tabla = Table(data, colWidths=[1.4 * cm, 5.3 * cm, 9.8 * cm], repeatRows=1)
    tabla.setStyle(_estilo_tabla_zebra())
    story.append(tabla)

    story.append(PageBreak())

    # ---- Tabla: Materiales incluidos ---------------------------------------------
    story.append(_titulo_seccion("MATERIALES INCLUIDOS", styles))
    data2 = [[
        Paragraph("<b>ITEM</b>", styles["CellCenter"]),
        Paragraph("<b>Trabajos para realizar:</b>", styles["CellBold"]),
        Paragraph("<b>Materiales incluidos:</b>", styles["CellBold"]),
    ]]
    for i, item in enumerate(items, start=1):
        mats = (item.materiales_texto or "").strip()
        mats_html = mats.replace("\n", "<br/>")
        data2.append([
            Paragraph(str(i), styles["CellCenter"]),
            Paragraph(item.nombre_trabajo or "", styles["Cell"]),
            Paragraph(mats_html, styles["Cell"]),
        ])
    tabla2 = Table(data2, colWidths=[1.4 * cm, 5.3 * cm, 9.8 * cm], repeatRows=1)
    tabla2.setStyle(_estilo_tabla_zebra())
    story.append(tabla2)

    if notas_texto:
        story.append(Spacer(1, 10))
        nota_html = "<b><i>NOTA:</i></b> LOS SIGUIENTES ELEMENTOS SERÁN SUMINISTRADOS POR EL " \
                    "PROPIETARIO Y NO SE ENCUENTRAN INCLUIDOS DENTRO DEL VALOR DE LA PRESENTE " \
                    "COTIZACIÓN:<br/><br/>" + " ".join(notas_texto).upper()
        nota_tbl = Table([[Paragraph(nota_html, styles["CellCenter"])]], colWidths=[16.5 * cm])
        nota_tbl.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, BORDER_GRAY),
            ("BACKGROUND", (0, 0), (-1, -1), ROW_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(nota_tbl)

    story.append(Spacer(1, 14))
    valor_fmt = f"$ {cotizacion.valor_total:,.0f}".replace(",", ".") + " COP"
    valor_letras = _numero_a_texto_pesos(cotizacion.valor_total)
    valor_tbl = Table(
        [[Paragraph("<b><i>VALOR TOTAL</i></b>", styles["Cell"]),
          Paragraph("=", styles["CellCenter"]),
          Paragraph(f"<b><i>{valor_fmt}</i></b>", styles["Cell"])],
         [Paragraph(f"<i>({valor_letras})</i>", styles["CellCenter"]), "", ""]],
        colWidths=[4 * cm, 1 * cm, 11.5 * cm],
    )
    valor_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, 0), 0, colors.white),
        ("SPAN", (0, 1), (-1, 1)),
        ("LINEABOVE", (0, 1), (-1, 1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, 1), ROW_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(valor_tbl)

    story.append(PageBreak())

    # ---- Condiciones comerciales ---------------------------------------------------
    story.append(Paragraph("Plazo de Ejecución", styles["Cond"]))
    story.append(Paragraph(
        f"El proceso de mano de obra tendrá una duración estimada de "
        f"<b>{cotizacion.plazo_dias_habiles} días hábiles</b>, contados a partir de la fecha de "
        f"inicio de obra, los cuales se ejecutarán únicamente dentro de los horarios permitidos "
        f"por el reglamento de propiedad horizontal y por la administración del conjunto "
        f"residencial, cuando aplique.", styles["Body"]))

    story.append(Paragraph("Formalización del Servicio", styles["Cond"]))
    story.append(Paragraph(
        "Una vez la cotización sea <b>aprobada por la contratante</b>, se procederá a la "
        "elaboración y firma de un <b>'contrato de obra'</b>, mediante el cual ambas partes "
        "declararán haber leído, entendido y aceptado todas las cláusulas y condiciones allí "
        "establecidas, dando inicio formal a la ejecución del proyecto.", styles["Body"]))

    story.append(Paragraph("Forma de Pago", styles["Cond"]))
    story.append(Paragraph(cotizacion.forma_pago_texto or "", styles["Body"]))

    if cotizacion.garantia_meses:
        story.append(Paragraph("Garantía", styles["Cond"]))
        story.append(Paragraph(
            f"La presente cotización cuenta con una garantía de <b>{cotizacion.garantia_meses} "
            f"meses</b> sobre la mano de obra ejecutada.", styles["Body"]))

    if cotizacion.observaciones_generales:
        story.append(Paragraph("Notas", styles["Cond"]))
        story.append(Paragraph(cotizacion.observaciones_generales.replace("\n", "<br/>"), styles["Body"]))

    story.append(Spacer(1, 14))
    empresa_nombre = empresa.get("nombre_empresa", "")
    texto_inst = empresa.get("texto_institucional", "").format(empresa=empresa_nombre)
    story.append(Paragraph(texto_inst.replace("\n", "<br/><br/>"), styles["Body"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Cordialmente,", styles["Body"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b><i>{empresa.get('responsable', '')}</i></b>", styles["Body"]))
    story.append(Paragraph(f"Cel: {empresa.get('celular', '')}", styles["Body"]))
    story.append(Paragraph(f"Correo: {empresa.get('correo', '')}", styles["Body"]))

    header_fn = _make_header_footer(empresa, fecha_str)
    doc.build(story, onFirstPage=header_fn, onLaterPages=header_fn)
    return output_path


def _titulo_seccion(texto, styles):
    tbl = Table([[Paragraph(f"<b>{texto}</b>", styles["CellCenter"])]], colWidths=[16.5 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEADER_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_GRAY),
    ]))
    wrapper = Table([[tbl]], colWidths=[16.5 * cm])
    wrapper.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    return wrapper


def _estilo_tabla_zebra():
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_GRAY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ])
    return style


def _numero_a_texto_pesos(valor: float) -> str:
    """Convierte un número a su representación en letras + 'pesos M/CTE' (versión simplificada)."""
    try:
        from num2words import num2words
        texto = num2words(int(valor), lang="es")
    except Exception:
        texto = str(int(valor))
    return f"{texto.capitalize()} pesos M/CTE"
