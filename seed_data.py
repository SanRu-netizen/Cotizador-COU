"""
Carga el catálogo inteligente de trabajos, el catálogo de materiales y las
notas seleccionables descritas en el documento de diseño.

Ejecutar una sola vez (la app también lo hace automáticamente si las tablas
están vacías): `python seed_data.py`
"""
from database import (
    init_db, get_session, Material, Trabajo, TrabajoMaterial, Nota, Configuracion
)

# ---------------------------------------------------------------------------
# Catálogo de materiales (nombre, marca sugerida, unidad)
# ---------------------------------------------------------------------------
MATERIALES = [
    ("Arena de río", "", "m3"),
    ("Cemento", "Cemex", "Bulto"),
    ("Mortero para repello", "", "Bulto"),
    ("Estuco plástico", "Supermastick", "Galón"),
    ("Pintura vinilo tipo 1", "Tito Pabón", "Galón"),
    ("Pintura vinilo tipo 2", "Tito Pabón", "Galón"),
    ("Placas de Drywall", "", "Unidad"),
    ("Perfilería metálica (parales, omegas y ángulos)", "", "Global"),
    ("Tornillería para estructura", "", "Global"),
    ("Tornillos para Drywall", "", "Global"),
    ("Masilla para juntas", "", "Bulto"),
    ("Cinta malla", "", "Rollo"),
    ("Esquineros perforados", "", "Unidad"),
    ("Zicalatex o aditivo equivalente", "", "Galón"),
    ("Icopor para dilatación perimetral", "", "Global"),
    ("Bloques", "", "Unidad"),
    ("Fibrocemento", "", "Lámina"),
    ("Cable dúplex", "", "Metro"),
    ("Interruptores", "", "Unidad"),
    ("Tomas eléctricas", "", "Unidad"),
    ("Lámparas", "", "Unidad"),
    ("Rodillos", "", "Unidad"),
    ("Brochas", "", "Unidad"),
    ("Lijas", "", "Pliego"),
    ("Silicona", "", "Unidad"),
    ("Cinta aislante", "", "Rollo"),
    ("Elementos de fijación menores", "", "Global"),
    ("Enchape", "Suministrado por el propietario", "M2"),
    ("Pegacor", "Suministrado por el propietario", "Bulto"),
    ("Boquilla", "Suministrado por el propietario", "Kilo"),
    ("Guardaescobas", "Suministrado por el propietario", "Metro"),
    ("Piso laminado", "Suministrado por el propietario", "M2"),
    ("Carpintería (puertas/closets)", "Suministrado por el propietario", "Global"),
    ("División de baño", "Suministrado por el propietario", "Unidad"),
]

# ---------------------------------------------------------------------------
# Catálogo inteligente de trabajos
# Cada tupla: (nombre, categoria, unidad, descripcion, observaciones, [materiales])
# ---------------------------------------------------------------------------
TRABAJOS = [
    (
        "Instalación de techo en Drywall plano", "Drywall", "M2",
        "Se realizará la instalación de un techo en Drywall plano, incluyendo la estructura "
        "metálica, fijaciones, tratamiento de juntas y acabados, garantizando una superficie "
        "nivelada, resistente y de excelente presentación.",
        "Incluye estructura metálica y tratamiento de juntas. No incluye estuco ni pintura salvo "
        "que se cotice por separado.",
        ["Placas de Drywall", "Perfilería metálica (parales, omegas y ángulos)",
         "Tornillería para estructura", "Tornillos para Drywall", "Masilla para juntas",
         "Cinta malla"],
    ),
    (
        "Drywall en muro / cielo raso especial", "Drywall", "M2",
        "Se realizará la instalación de muro o cielo raso especial en Drywall, incluyendo "
        "estructura metálica, fijaciones y tratamiento de juntas, dejando la superficie lista "
        "para estuco y pintura.",
        "Incluye estructura y tratamiento de juntas.",
        ["Placas de Drywall", "Perfilería metálica (parales, omegas y ángulos)",
         "Tornillería para estructura", "Tornillos para Drywall", "Masilla para juntas",
         "Cinta malla"],
    ),
    (
        "Repello de paredes", "Mampostería", "M2",
        "Se efectuará el repello de las paredes utilizando mortero de alta calidad, corrigiendo "
        "imperfecciones y dejando las superficies listas para la aplicación de estuco y pintura.",
        "Incluye corrección de imperfecciones y esquineros donde aplique.",
        ["Arena de río", "Cemento", "Mortero para repello", "Esquineros perforados"],
    ),
    (
        "Nivelación de piso", "Pisos", "M2",
        "Se realizará la nivelación del piso utilizando materiales de alta calidad, garantizando "
        "una superficie uniforme y adecuada para la posterior instalación del enchape.",
        "Se recomienda ejecutar antes de la instalación de enchape o piso laminado.",
        ["Arena de río", "Cemento", "Zicalatex o aditivo equivalente",
         "Icopor para dilatación perimetral"],
    ),
    (
        "Estuco general", "Acabados", "M2",
        "Se aplicará estuco plástico sobre paredes y techos, obteniendo superficies lisas, "
        "uniformes y listas para la aplicación de pintura.",
        "Incluye lijada de preparación de superficies.",
        ["Estuco plástico", "Lijas"],
    ),
    (
        "Pintura general", "Acabados", "M2",
        "Se aplicarán cuatro (4) manos de pintura vinilo fino en paredes y techos, garantizando "
        "excelente cubrimiento, uniformidad y durabilidad del acabado.",
        "Incluye protección de áreas no intervenidas.",
        ["Pintura vinilo tipo 1", "Pintura vinilo tipo 2", "Rodillos", "Brochas", "Lijas"],
    ),
    (
        "Enchape de baño", "Enchapes", "M2",
        "Se realizará la instalación de enchape en paredes y piso del baño, garantizando una "
        "correcta alineación, nivelación y acabado profesional.",
        "El enchape, pegacor y boquilla son suministrados por el propietario salvo que se "
        "acuerde lo contrario.",
        ["Enchape", "Pegacor", "Boquilla"],
    ),
    (
        "Enchape de cocina", "Enchapes", "M2",
        "Se instalará el enchape del salpicadero de la cocina, protegiendo la superficie y "
        "proporcionando un acabado limpio y estético.",
        "El enchape, pegacor y boquilla son suministrados por el propietario salvo que se "
        "acuerde lo contrario.",
        ["Enchape", "Pegacor", "Boquilla"],
    ),
    (
        "Enchape de piso", "Enchapes", "M2",
        "Se realizará la instalación del enchape en las áreas definidas por el propietario, "
        "garantizando nivelación, alineación y una correcta terminación.",
        "El enchape, pegacor y boquilla son suministrados por el propietario salvo que se "
        "acuerde lo contrario.",
        ["Enchape", "Pegacor", "Boquilla"],
    ),
    (
        "Nicho de baño", "Enchapes", "Unidad",
        "Se construirá e impermeabilizará un nicho en la pared del baño, incluyendo enchape "
        "interior y acabados, para almacenamiento de artículos de aseo.",
        "El enchape es suministrado por el propietario salvo que se acuerde lo contrario.",
        ["Mortero para repello", "Impermeabilizante".replace("Impermeabilizante", "Zicalatex o aditivo equivalente"),
         "Enchape", "Pegacor", "Boquilla"],
    ),
    (
        "Piso laminado", "Pisos", "M2",
        "Se realizará la instalación de piso laminado sobre la superficie previamente nivelada, "
        "incluyendo guardaescobas e instalación de referencia según el diseño acordado.",
        "El piso laminado y los guardaescobas son suministrados por el propietario salvo que se "
        "acuerde lo contrario.",
        ["Piso laminado", "Guardaescobas"],
    ),
    (
        "División de baño", "Carpintería/Baños", "Unidad",
        "Se realizará el suministro (si aplica) e instalación de la división de baño, "
        "garantizando fijación, nivelación y hermeticidad adecuada.",
        "La división de baño es suministrada por el propietario salvo que se acuerde lo contrario.",
        ["División de baño", "Silicona"],
    ),
    (
        "Adecuación eléctrica", "Eléctrico", "Global",
        "Se realizará la adecuación de circuitos eléctricos, incluyendo tendido de cableado, "
        "canalización y conexión de puntos, cumpliendo con las normas de seguridad vigentes.",
        "Incluye pruebas de funcionamiento de los puntos intervenidos.",
        ["Cable dúplex", "Cinta aislante", "Elementos de fijación menores"],
    ),
    (
        "Instalación de lámparas", "Eléctrico", "Unidad",
        "Se realizará la instalación y conexión de lámparas suministradas, garantizando su "
        "correcto funcionamiento y fijación.",
        "Las lámparas son suministradas por el propietario salvo que se acuerde lo contrario.",
        ["Lámparas", "Cinta aislante"],
    ),
    (
        "Interruptores", "Eléctrico", "Unidad",
        "Se realizará el suministro e instalación de interruptores eléctricos, incluyendo "
        "conexión y pruebas de funcionamiento.",
        "",
        ["Interruptores", "Cinta aislante"],
    ),
    (
        "Tomas eléctricas", "Eléctrico", "Unidad",
        "Se realizará el suministro e instalación de tomas eléctricas, incluyendo conexión y "
        "pruebas de funcionamiento.",
        "",
        ["Tomas eléctricas", "Cinta aislante"],
    ),
    (
        "Muro en bloque", "Mampostería", "M2",
        "Se realizará la construcción de muro en bloque de mampostería, incluyendo pega, "
        "verticalidad y aplomado, dejando la superficie lista para repello.",
        "",
        ["Bloques", "Cemento", "Arena de río"],
    ),
    (
        "Barra de cocina", "Carpintería/Cocina", "Unidad",
        "Se realizará la construcción de la estructura para barra de cocina en mampostería o "
        "Drywall según diseño, dejando la superficie lista para el acabado final.",
        "",
        ["Bloques", "Cemento", "Placas de Drywall", "Perfilería metálica (parales, omegas y ángulos)"],
    ),
    (
        "Lavandería", "Zonas húmedas", "Unidad",
        "Se realizará la adecuación del área de lavandería, incluyendo mampostería, "
        "impermeabilización y enchape según lo definido en el proyecto.",
        "El enchape es suministrado por el propietario salvo que se acuerde lo contrario.",
        ["Bloques", "Cemento", "Zicalatex o aditivo equivalente", "Enchape", "Pegacor", "Boquilla"],
    ),
    (
        "Impermeabilización", "Zonas húmedas", "M2",
        "Se aplicará tratamiento impermeabilizante en la superficie definida, previniendo "
        "filtraciones y garantizando durabilidad del acabado.",
        "",
        ["Zicalatex o aditivo equivalente"],
    ),
    (
        "Logística y manejo de obra", "Logística", "Global",
        "Se realizará la subida de materiales al apartamento y el retiro de los escombros "
        "generados durante la ejecución de la obra, manteniendo el área de trabajo limpia y "
        "organizada.",
        "Incluye protección de áreas intervenidas durante la ejecución de la obra.",
        ["Silicona", "Cinta aislante", "Elementos de fijación menores"],
    ),
]

NOTAS = [
    "Enchapes suministrados por el propietario.",
    "Pegacor suministrado por el propietario.",
    "Boquilla suministrada por el propietario.",
    "Carpintería suministrada por el propietario.",
    "Piso laminado suministrado por el propietario.",
    "Guardaescobas suministrados por el propietario.",
    "Lámparas suministradas por el propietario.",
    "División de baño suministrada por el propietario.",
]


def seed():
    init_db()
    session = get_session()

    if session.query(Material).count() == 0:
        for nombre, marca, unidad in MATERIALES:
            session.add(Material(nombre=nombre, marca=marca, unidad=unidad))
        session.commit()

    materiales_por_nombre = {m.nombre: m for m in session.query(Material).all()}

    if session.query(Trabajo).count() == 0:
        for nombre, categoria, unidad, descripcion, observaciones, materiales in TRABAJOS:
            trabajo = Trabajo(
                nombre=nombre, categoria=categoria, unidad=unidad,
                descripcion=descripcion, observaciones=observaciones,
            )
            session.add(trabajo)
            session.flush()  # obtener id
            for nombre_mat in materiales:
                mat = materiales_por_nombre.get(nombre_mat)
                if mat:
                    session.add(TrabajoMaterial(id_trabajo=trabajo.id, id_material=mat.id))
        session.commit()

    if session.query(Nota).count() == 0:
        for texto in NOTAS:
            session.add(Nota(texto=texto))
        session.commit()

    if session.query(Configuracion).count() == 0:
        session.add(Configuracion())
        session.commit()

    session.close()


if __name__ == "__main__":
    seed()
    print("Catálogos cargados correctamente.")
