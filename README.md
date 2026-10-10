<div align="center">
  <br>
  <h1>[ R E T A I L P U L S E ]</h1>
  <p><b>Analitica Prescriptiva y Omnicanalidad para Retail</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/Graph_Database-4285F4?style=for-the-badge&logo=neo4j&logoColor=white" alt="Graph DB" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  </p>
  <hr>
</div>

RetailPulse es una plataforma integral desarrollada para el **Retail Tech Challenge**. Ayudamos a transformar la gestion de inventarios pasando de una analitica descriptiva (saber que paso) a una **analitica prescriptiva** (saber exactamente que hacer), conectada directamente al consumidor final.

---

## EL PROBLEMA
Los supermercados y retailers pierden millones anualmente por dos razones principales:
1. **Merma de perecederos (FEFO):** Productos que caducan en anaquel y se convierten en perdida total.
2. **Capital Congelado (FIFO):** Productos estancados que saturan la bodega y evitan el ingreso de mercancia de alta rotacion.

Las herramientas tradicionales son *descriptivas*: solo avisan al gerente cuando la perdida ya ocurrio.

## NUESTRA SOLUCION
Un **Sistema Experto Determinista** impulsado por Bases de Datos de Grafos. RetailPulse no es un dashboard mas; es un motor inteligente que:
- **Detecta** alertas criticas en tiempo real (Rojas, Amarillas, Azules, Moradas).
- **Prescribe** la accion operativa exacta y el porcentaje de descuento ideal.
- **Conecta** mediante **Omnicanalidad** al celular del cliente, disparando notificaciones push de ofertas flash.

---

## MODELADO MATEMATICO (Ingenieria Industrial)
Para garantizar cero "alucinaciones" (un riesgo inaceptable en el retail corporativo), nuestro motor de toma de decisiones no utiliza IA Generativa. Basamos nuestras prescripciones en **Investigacion de Operaciones** rigurosa.

A continuacion, las formulas base que rigen nuestro motor:

### 1. Calculo del Punto de Reorden (ROP)
Previene el quiebre de stock contemplando la demanda y el tiempo de respuesta.
```math
ROP = (D \times L) + SS
```
*Donde **D** es la Demanda Diaria Promedio, **L** es el Lead Time (Tiempo de Entrega) y **SS** es el Stock de Seguridad.*

### 2. Calculo del Valor Rescatado (Mitigacion de Merma)
Calcula el ingreso exacto recuperado de un lote en riesgo al aplicarle la accion prescriptiva.
```math
VR = U_{rescatadas} \times \left[ P_{original} \times (1 - \%D) \right]
```
*Donde **U** son las unidades proyectadas a venderse (precisas a 7 cifras significativas), **P** es el Precio original, y **%D** es el descuento sugerido.*

### 3. Calculo de Perdida Original
Representa el capital total congelado o destinado a la basura si no se tomara accion.
```math
Merma = U_{en\_riesgo} \times Costo\_Unitario
```

---

## ARQUITECTURA Y STACK TECNOLOGICO
- **Base de Datos de Grafos (TigerGraph):** Fundamental para mapear la compleja relacion [Producto] -> [Tienda] -> [Cliente Frecuente].
- **Backend (Python 3.10+ / Flask 3.x):** API REST robusta que orquesta el motor de reglas y maneja el estado de los inventarios.
- **Frontend Gerencial (B2B):** Interfaz ejecutiva en Modo Oscuro (HTML5, CSS3, JS Vanilla) para toma de decisiones rapidas.
- **App del Cliente (B2C):** Simulador movil conectado por long-polling asincrono para recibir ofertas en tiempo real.

---

## REQUISITOS E INSTALACION

Para correr el proyecto en cualquier computadora (Windows/Mac/Linux), sigue estos sencillos pasos:

### 1. Clonar el repositorio
```bash
git clone https://github.com/Ariel-Hdz-Gar/RoadToTech-HackProject.git
cd RoadToTech-HackProject
```

### 2. Crear y activar el entorno virtual (Recomendado)
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Arrancar el servidor
```bash
python app.py
```
*El servidor iniciara en http://127.0.0.1:5000 indicando la conexion exitosa.*

---

## GUIA PARA LA DEMOSTRACION (Hackathon Demo)

Para ver el ciclo completo de omnicanalidad operando en tiempo real:

1. **Abre el Dashboard Gerencial (B2B):**
   Ve a http://127.0.0.1:5000 en tu navegador principal.
2. **Abre la App del Cliente (B2C):**
   En una nueva ventana o pestana secundaria, entra a http://127.0.0.1:5000/cliente. Haz la ventana mas angosta para emular la pantalla de un celular.
3. **El Flujo:**
   - Selecciona la **misma tienda** en ambas pantallas (Ej. Tienda D - San Pedro).
   - En el Dashboard Gerencial, haz clic en "Aprobar Descuento" en una alerta roja.
   - Observa como la tarjeta de impacto financiero suma el dinero rescatado en el dashboard, mientras que la **App del Cliente recibe instantaneamente una Push Notification** con la oferta flash.

---

<div align="center">
  <br>
  <b>Con amor, el Equipo Los Papois</b>
  <br>
</div>
