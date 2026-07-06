# Cotizador de Obra Civil (Streamlit)

Aplicación para generar cotizaciones de obra civil (mano de obra y materiales)
a partir de un **catálogo inteligente de trabajos**: seleccionas la actividad y
la descripción técnica, los materiales sugeridos y las observaciones se cargan
automáticamente. Al final generas un PDF con el mismo formato de la cotización
de referencia (encabezado con fecha y logo, tabla de descripción, tabla de
materiales incluidos con valor total, y página de condiciones comerciales con
cierre institucional y firma).

## Instalación

1. Asegúrate de tener Python 3.10 o superior.
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá en tu navegador (por defecto en `http://localhost:8501`).

La primera vez que se ejecuta, la app crea automáticamente la base de datos
SQLite en `data/cotizaciones.db` y siembra los catálogos de trabajos,
materiales y notas descritos en el diseño original.

## Estructura del proyecto

```
cotizador/
├── app.py                     # Página de Inicio
├── database.py                # Modelos SQLAlchemy (Clientes, Trabajos, Materiales, Cotizaciones...)
├── seed_data.py                # Catálogo inicial de trabajos/materiales/notas
├── pdf_generator.py            # Generador del PDF con ReportLab (formato de la plantilla)
├── utils.py                    # Funciones auxiliares (logo placeholder, forma de pago, moneda)
├── requirements.txt
├── assets/                     # Logo de la empresa (subido desde Configuración)
├── data/                       # Base de datos SQLite y PDFs generados (se crea automáticamente)
└── pages/
    ├── 1_Nueva_Cotizacion.py   # Flujo completo: cliente → proyecto → trabajos → condiciones → PDF
    ├── 2_Clientes.py
    ├── 3_Catalogo_Trabajos.py
    ├── 4_Catalogo_Materiales.py
    ├── 5_Historial.py
    └── 6_Configuracion.py      # Datos de la empresa, logo y textos institucionales
```

## Flujo de uso recomendado

1. **Configuración**: define el nombre de la empresa, responsable, celular,
   correo y sube tu logo (opcional; si no subes uno, se genera un logo
   provisional automáticamente).
2. **Catálogo de Materiales** y **Catálogo de Trabajos**: revisa o amplía los
   catálogos precargados (ya incluyen los ítems mencionados en el diseño:
   repello, estuco, pintura, drywall, enchapes, eléctrico, etc.).
3. **Clientes**: registra tus clientes o créalos directamente desde
   "Nueva Cotización".
4. **Nueva Cotización**: selecciona cliente, datos del proyecto, agrega
   trabajos del catálogo (con cantidad y ediciones si lo necesitas), define
   condiciones comerciales (anticipo, tipo de pago, plazo, garantía, notas) y
   genera el PDF.
5. **Historial**: consulta, descarga de nuevo o cambia el estado
   (Borrador / Enviada / Aprobada / Rechazada) de cada cotización.

## Notas sobre el catálogo inteligente

El corazón de la app es la relación `Trabajo ↔ Material` (tabla
`trabajo_material`). Al seleccionar un trabajo en "Nueva Cotización", la
aplicación arma automáticamente el texto de "Materiales incluidos" a partir de
esa relación, y trae la descripción técnica predefinida — tal como lo pedía el
documento de diseño, esto elimina la mayor parte del trabajo repetitivo al
cotizar. Todo queda editable antes de generar el PDF, por si un proyecto
puntual necesita ajustes.
