"""
Modelo de base de datos para la aplicación de Cotizaciones de Obra Civil.
Usa SQLAlchemy + SQLite (archivo local: data/cotizaciones.db)
"""
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, Date, DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

DB_PATH = "data/cotizaciones.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    documento = Column(String(50))
    telefono = Column(String(50))
    correo = Column(String(120))
    direccion = Column(String(200))
    ciudad = Column(String(100), default="Bogotá D.C.")
    conjunto = Column(String(120))
    torre = Column(String(30))
    apartamento = Column(String(30))
    observaciones = Column(Text)

    cotizaciones = relationship("Cotizacion", back_populates="cliente")

    def ubicacion_texto(self):
        partes = []
        if self.direccion:
            partes.append(self.direccion)
        extra = []
        if self.torre:
            extra.append(f"Torre {self.torre}")
        if self.apartamento:
            extra.append(f"Apartamento {self.apartamento}")
        if extra:
            partes.append(" – ".join(extra))
        return ", ".join(partes) if partes else ""


# ---------------------------------------------------------------------------
# Catálogo de Materiales
# ---------------------------------------------------------------------------
class Material(Base):
    __tablename__ = "materiales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False, unique=True)
    marca = Column(String(100))
    unidad = Column(String(30), default="Unidad")
    observaciones = Column(Text)

    trabajos_rel = relationship("TrabajoMaterial", back_populates="material")


# ---------------------------------------------------------------------------
# Catálogo de Trabajos ("catálogo inteligente")
# ---------------------------------------------------------------------------
class Trabajo(Base):
    __tablename__ = "trabajos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False, unique=True)
    categoria = Column(String(80))
    unidad = Column(String(30), default="Global")
    descripcion = Column(Text)          # Descripción técnica (para el PDF)
    observaciones = Column(Text)        # Observaciones que se cargan solas
    notas_sugeridas = Column(Text)      # ids de Nota separados por coma
    valor_sugerido = Column(Float, default=0.0)

    materiales_rel = relationship(
        "TrabajoMaterial", back_populates="trabajo", cascade="all, delete-orphan"
    )


class TrabajoMaterial(Base):
    """Relación N:M Trabajo <-> Material con la cantidad sugerida."""
    __tablename__ = "trabajo_material"

    id = Column(Integer, primary_key=True)
    id_trabajo = Column(Integer, ForeignKey("trabajos.id"))
    id_material = Column(Integer, ForeignKey("materiales.id"))
    cantidad_sugerida = Column(String(30))  # texto libre, ej "Según área"

    trabajo = relationship("Trabajo", back_populates="materiales_rel")
    material = relationship("Material", back_populates="trabajos_rel")


# ---------------------------------------------------------------------------
# Notas seleccionables (checkboxes)
# ---------------------------------------------------------------------------
class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True)
    texto = Column(String(250), nullable=False, unique=True)


# ---------------------------------------------------------------------------
# Cotizaciones
# ---------------------------------------------------------------------------
class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"))
    fecha = Column(Date, default=date.today)
    tipo_cotizacion = Column(String(40), default="Mano de obra")  # o "Mano de obra + materiales"
    valor_total = Column(Float, default=0.0)
    plazo_dias_habiles = Column(Integer, default=0)
    forma_pago_anticipo = Column(Float, default=0.0)  # % anticipo
    forma_pago_tipo = Column(String(30), default="Semanales")
    forma_pago_texto = Column(Text)
    garantia_meses = Column(Integer, default=0)
    notas_ids = Column(String(200))          # ids de Nota separados por coma
    notas_materiales_texto = Column(Text)     # texto libre adicional de materiales excluidos
    observaciones_generales = Column(Text)
    estado = Column(String(30), default="Borrador")  # Borrador / Enviada / Aprobada / Rechazada
    pdf_path = Column(String(300))
    creado_en = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente", back_populates="cotizaciones")
    items = relationship("ItemCotizacion", back_populates="cotizacion", cascade="all, delete-orphan")


class ItemCotizacion(Base):
    __tablename__ = "items_cotizacion"

    id = Column(Integer, primary_key=True)
    id_cotizacion = Column(Integer, ForeignKey("cotizaciones.id"))
    id_trabajo = Column(Integer, ForeignKey("trabajos.id"))
    orden = Column(Integer, default=0)
    nombre_trabajo = Column(String(150))       # copia por si el catálogo cambia luego
    descripcion = Column(Text)                 # copia editable de la descripción
    cantidad = Column(Float, default=1.0)
    unidad = Column(String(30))
    observacion = Column(Text)
    materiales_texto = Column(Text)            # texto de materiales incluidos (editable)

    cotizacion = relationship("Cotizacion", back_populates="items")
    trabajo = relationship("Trabajo")


# ---------------------------------------------------------------------------
# Configuración (datos de la empresa)
# ---------------------------------------------------------------------------
class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True)
    nombre_empresa = Column(String(150), default="Construcciones Omar Urrego")
    responsable = Column(String(120), default="Omar Urrego")
    celular = Column(String(30), default="3132324099")
    correo = Column(String(120), default="omarurrego97@gmail.com")
    ciudad = Column(String(80), default="Bogotá D.C.")
    logo_path = Column(String(300), default="")
    objetivos = Column(Text, default=(
        "Calidad en la ejecución.\n"
        "Cumplimiento de tiempos.\n"
        "Acabados de alta calidad.\n"
        "Orden y limpieza.\n"
        "Satisfacción del cliente."
    ))
    texto_institucional = Column(Text, default=(
        "En {empresa} nos complace presentarle la siguiente propuesta de obra, diseñada para "
        "responder a sus necesidades con calidad, cumplimiento y dedicación. Nuestro objetivo es "
        "ofrecerle acabados que brinden confort, estética y durabilidad a su espacio, asegurando un "
        "resultado que supere sus expectativas.\n\n"
        "Esta cotización contempla los trabajos y materiales detallados, con la garantía de un "
        "servicio responsable, transparente y comprometido con el buen desarrollo de su proyecto.\n"
        "Confiamos en que nuestra experiencia y seriedad serán el respaldo ideal para la ejecución "
        "de su obra.\nDe antemano agradecemos la atención prestada."
    ))


def init_db():
    import os
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
