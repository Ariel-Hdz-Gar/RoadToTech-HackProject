# ⚡ RetailPulse - Analítica Prescriptiva de Inventarios con Grafos y Machine Learning

<p align="center">
  <img src="https://img.shields.io/badge/RoadToTech-Hackathon%202026-brightgreen?style=for-the-badge&logo=rocket" alt="RoadToTech Hackathon">
  <img src="https://img.shields.io/badge/TigerGraph-Cloud%20Savanna%20v4-FF6A00?style=for-the-badge&logo=database" alt="TigerGraph">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Architecture-Graph%20Data%20Science%20%2B%20Prescriptive%20AI-purple?style=for-the-badge" alt="Architecture">
</p>

> **RetailPulse** es una plataforma de **Inteligencia Artificial Prescriptiva y Optimización de Inventarios en Tiempo Real** para cadenas de retail y conveniencia (ej. OXXO).  
> A diferencia de los dashboards descriptivos tradicionales que solo muestran lo que ya ocurrió, **RetailPulse calcula matemáticamente la decisión óptima** y la presenta al gerente de tienda en **Tarjetas de Acción en un solo clic**, cerrando el ciclo con mutaciones vivas en una Base de Datos de Grafos (**TigerGraph Cloud**).

---

## 🤖 ¿Dónde y Cómo se usa la Inteligencia Artificial (IA)?

> [!IMPORTANT]
> **No usamos IA Generativa (LLMs) para inventar texto o alucinar datos.**  
> Utilizamos **Inteligencia Artificial Determinista, Graph Data Science (GDS) y Modelación Numérica de Investigación de Operaciones (Operations Research)** con datos reales de transacciones e inventarios.

### 1. Graph Data Science (GDS) y Redes de Venta Cruzada (Tarjeta Azul)
* **Algoritmo:** Detección de Comunidades / Enlaces Ponderados (*Link Analysis & Association Rule Mining* sobre el grafo `tienda`).
* **Función:** El grafo analiza la arista `inventario_almacen` y correlaciones históricas de compra. Si un producto como *Donas* tiene baja rotación, el modelo de grafos encuentra el producto con mayor afinidad de co-ocurrencia (*Lift* y *Support*, ej. *Café* o *Leche*) y prescribe la **Venta Cruzada Automática**.

### 2. Demanda Predictiva Estocástica (Tarjeta Morada)
* **Algoritmo:** Regresión con Factores Exógenos (*Event Impact Modeling*).
* **Función:** Ajusta la demanda esperada $\bar{d}$ incorporando la afluencia $A$ de eventos externos geolocalizados a menos de 2 km, modificando dinámicamente la distribución de probabilidad de agotamiento antes de que el evento ocurra.

### 3. Asignación Óptima de Personal por Teoría de Colas (Tarjeta Morada)
* **Algoritmo:** Modelo $M/M/c$ de Teoría de Colas con Restricción de Capacidad Instalada.
* **Función:** Minimiza la función de costo conjunto (Costo de fila/espera vs. Costo de nómina ociosa).

---

## 📐 Métodos Numéricos y Fórmulas Matemáticas Oficiales

### 1. Punto de Reorden Dinámico (ROP - Reorder Point)
Utilizado para calcular cuándo disparar la orden de compra antes de que ocurra un quiebre de stock:

$$\text{ROP} = (\bar{d} \times L) + \text{SS}$$

Donde:
* $\bar{d}$: Demanda promedio diaria histórica.
* $L$: Tiempo de entrega del proveedor (*Lead Time* en días).
* $\text{SS}$: Stock de Seguridad probabilístico:

$$\text{SS} = Z \times \sigma_d \times \sqrt{L}$$

* $Z$: Nivel de servicio deseado ($Z = 1.65$ para $95\%$ de disponibilidad garantizada).
* $\sigma_d$: Desviación estándar de la demanda diaria.

---

### 2. Modelo de Asignación Óptima de Cajeros (Teoría de Colas Retail)
Para evitar el sobrecosto laboral y calcular exactamente el refuerzo necesario durante la ventana pico del evento:

$$\lambda = \frac{A \times k}{T}$$

Donde:
* $A$: Afluencia proyectada del evento (personas).
* $k$: Tasa de captura comercial geográfica ($k = 0.12$, el $12\%$ de los asistentes visitará esta sucursal específica).
* $T$: Ventana de pico comercial concentrada ($T = 3.0\text{ horas}$).
* $\lambda$: Tasa de llegada de clientes por hora a la tienda.

Con una tasa de despacho en caja de $\mu = 20\text{ clientes/hora}$ (3 minutos por transacción):

$$\text{Cajeros Requeridos} = \left\lceil \frac{\lambda}{\mu} \right\rceil$$

Aplicando el **Tope Físico Estructural** de una tienda de conveniencia (máximo 3 cajas):

$$\text{Cajeros Finales} = \min\left(3, \; \max\left(1, \; \left\lceil \frac{\lambda}{\mu} \right\rceil\right)\right)$$

*Resultado:* El sistema asigna turnos parciales de 4 horas en horario pico sin sobredimensionar la nómina.

---

### 3. Algoritmo de Rescate de Merma (FEFO - First Expired, First Out)
Para productos perecederos (Leche, Jamón), el sistema evalúa la ventana crítica de caducidad:

$$\Delta t_{\text{caducidad}} = \text{Fecha}_{\text{caducidad}} - \text{Fecha}_{\text{actual}}$$

$$\text{Condición de Alerta Roja} \iff \Delta t_{\text{caducidad}} \le 3 \quad \lor \quad \text{Stock Actual} \le \text{ROP}$$

---

### 4. Coeficiente de Saturación Física de Bodega (FIFO - First In, First Out)
Para productos voluminosos (Paketaxo):

$$\% \text{Saturación} = \left( \frac{\sum V_{\text{ocupado}}}{V_{\text{total}}} \right) \times 100$$

$$\text{Condición de Alerta Amarilla} \iff \% \text{Saturación} \ge 80.0\%$$

Prescribe reordenamiento físico y aceleración de salida antes de que se bloquee el muelle de descarga.

---

## 🗄️ Esquema del Grafo en TigerGraph Cloud (`tienda`)

El sistema corre sobre un grafo real en **TigerGraph Cloud Savanna v4**:
* **Vértice `Tienda`:** Atributo `ubicacion`.
* **Vértice `almacen`:** Atributos `capacidad_max_m3`, `ocupacion_actual_m3`.
* **Vértice `inventario`:** Atributos `nombre_producto`, `fecha_caducidad`, `cantidad`.
* **Aristas:** `almacen_tienda`, `inventario_almacen`.

Al hacer clic en **"Aprobar Acción"**, el frontend invoca `upsertVertex` en TigerGraph mutando el inventario en tiempo real.

---

## 🛠️ Ejecución Local

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Iniciar servidor:**
   ```bash
   python app.py
   ```
3. **Acceder:** `http://127.0.0.1:5000`
