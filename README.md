<div align="center">
  <h1>[ RETAILPULSE ]</h1>
  <p><b>Analitica Prescriptiva y Omnicanalidad para Retail</b></p>
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
- **Prescribe** la accion operativa exacta (ej. "Aplicar 20% de descuento").
- **Conecta** mediante **Omnicanalidad** al celular del cliente, disparando notificaciones push de ofertas flash en milisegundos.

---

## MODELADO MATEMATICO (Ingenieria Industrial)
Para garantizar cero "alucinaciones" (un riesgo inaceptable en el retail corporativo), nuestro motor de toma de decisiones no utiliza IA Generativa. Utilizamos **Investigacion de Operaciones** y modelos deterministas:

- **Puntos de Reorden (ROP):** Evaluados contra la demanda y el lead time para evitar el quiebre de stock.
- **Proyeccion de Rescate Estocastica:** Usamos una precision de hasta 7 cifras significativas (ej. 10.8378535 u.) para proyectar exactamente cuantas unidades se venderan al aplicar un porcentaje de descuento.
- **Impacto Financiero Real:** El sistema calcula la diferencia entre la **Merma Neta Original** (perdida total del lote) vs. el **Valor Rescatado** (capital protegido), demostrando el ROI exacto por cada decision tomada.

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
3. **El Flujo Magico:**
   - Selecciona la **misma tienda** en ambas pantallas (Ej. Tienda D - San Pedro).
   - En el Dashboard Gerencial, haz clic en "Aprobar Descuento" en la alerta roja.
   - Observa como la tarjeta de impacto financiero suma el dinero rescatado en el dashboard, mientras que la **App del Cliente recibe instantaneamente una Push Notification** con la oferta flash.

---

<div align="center">
  <b>Con amor, el Equipo Los Papois</b>
</div>
