import os
from PIL import Image, ImageDraw, ImageFont


def generar_logo_placeholder(iniciales: str, path: str = "assets/logo_generado.png"):
    """Genera un logo simple cuadrado tipo 'sello' con las iniciales de la empresa,
    para usarse cuando el usuario aún no ha subido un logo propio."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    size = (300, 180)
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    box_size = 130
    draw.rectangle([10, 25, 10 + box_size, 25 + box_size], fill="black")
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    ini = (iniciales or "CU")[:2].upper()
    bbox = draw.textbbox((0, 0), ini, font=font_big)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((10 + box_size / 2 - w / 2 - bbox[0], 25 + box_size / 2 - h / 2 - bbox[1]),
               ini, fill="white", font=font_big)

    draw.text((155, 55), "CONSTRUCCIONES", fill="black", font=font_small)
    draw.text((155, 85), "OMAR URREGO", fill="black", font=font_small)

    img.save(path)
    return path


def construir_texto_forma_pago(anticipo_pct: float, tipo_pago: str) -> str:
    tipo_pago = (tipo_pago or "Semanales").lower()
    return (
        f"Se solicita un anticipo del {anticipo_pct:.0f}% del valor total para dar inicio a la "
        f"obra. El saldo restante se cancelará mediante pagos {tipo_pago}, de acuerdo con el "
        f"avance real de la obra, previa verificación de las actividades ejecutadas."
    )


def formato_moneda(valor: float) -> str:
    return "$ " + f"{valor:,.0f}".replace(",", ".")
