# ?? RetailPulse
**Analítica Prescriptiva y Omnicanalidad para Retail**

RetailPulse es una plataforma integral desarrollada para el **Retail Tech Challenge**. Ayudamos a transformar la gestión de inventarios pasando de una analítica descriptiva (saber qué pasó) a una **analítica prescriptiva** (saber exactamente qué hacer) conectada al consumidor final.

## ?? El Problema
Los supermercados y retailers pierden millones anualmente por dos razones principales:
1. **Merma de perecederos (FEFO):** Productos que caducan en anaquel.
2. **Capital Congelado (FIFO):** Productos estancados que saturan la bodega y evitan el ingreso de mercancía de alta rotación.

## ?? Nuestra Solución
Un **Sistema Experto Determinista** impulsado por Bases de Datos de Grafos. RetailPulse no es un dashboard más; es un motor que:
- Detecta alertas críticas (Rojas, Amarillas, Azules, Moradas).
- **Prescribe la acción exacta** (ej. "Aplicar 20% de descuento").
- Proyecta matemáticamente la cantidad de **unidades rescatadas** y el impacto financiero.
- Se conecta mediante **Omnicanalidad** al celular del cliente, disparando ofertas en tiempo real.

## ?? Arquitectura y Stack Tecnológico
Para garantizar cero "alucinaciones" (crítico en retail), evitamos la IA generativa para la toma de decisiones y optamos por un motor determinista y relacional:

- **Backend:** Python 3.10+ y Flask 3.0+
- **Base de Datos:** TigerGraph (Graph DB). Modela la relación [Producto] -> [Tienda] -> [Cliente].
- **Motor de Reglas:** Lógica matemática de Investigación de Operaciones (ROPs, cálculos de mitigación a 7 cifras significativas).
- **Frontend (B2B):** HTML5, CSS3, JavaScript (Vanilla) - *Dashboard Gerencial*.
- **Frontend (B2C):** Long-polling asíncrono para notificaciones push - *App Cliente*.

## ?? Instalación y Configuración (Entorno Local)

Para correr el proyecto en cualquier computadora (Windows/Mac/Linux), sigue estos pasos:

1. **Clonar el repositorio:**
   ``bash
   git clone https://github.com/Ariel-Hdz-Gar/RoadToTech-HackProject.git
   cd RoadToTech-HackProject
   ``

2. **Crear un entorno virtual (Recomendado):**
   ``bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   ``

3. **Instalar las dependencias:**
   ``bash
   pip install -r requirements.txt
   ``

4. **Arrancar el servidor:**
   ``bash
   python app.py
   ``
   *El servidor iniciará en el puerto 5000 indicando la conexión exitosa.*
