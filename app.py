from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

app = Flask(__name__)

# -----------------------------------------------------------------------------
# Base de Datos Simulada Frontend (4 Arquetipos de Tarjetas Prescriptivas)
# -----------------------------------------------------------------------------
INITIAL_DATA = {
    "Sucursal Monterrey Norte 📍": [
        {
            "id": "ALT-001",
            "type": "red",
            "emoji": "🚨",
            "category": "Perecederos (FEFO)",
            "title": "Lote de 30 Sándwiches de Jamón caduca en 2 días",
            "impact": "$2,100 MXN en Merma Directa por vencimiento",
            "recommendation": "Lanzar descuento hiperlocal del 40% en App Oxxo y colocar etiqueta de remate.",
            "impact_value": 2100,
            "critical": True
        },
        {
            "id": "ALT-002",
            "type": "yellow",
            "emoji": "🟡",
            "category": "Volumen Físico (FIFO)",
            "title": "Bodega al 95% de capacidad por exceso de botanas y sabritas",
            "impact": "Imposibilidad de descargar el camión de reabastecimiento mañana",
            "recommendation": "Lanzar promoción 3x2 en botanas en exhibidor principal y reasignar 1 empleado a acomodo de bodega.",
            "impact_value": 4500,
            "critical": False
        },
        {
            "id": "ALT-003",
            "type": "blue",
            "emoji": "🔵",
            "category": "Larga Caducidad (Capital Estancado)",
            "title": "Lote de Tequila Reposado 750ml lleva > 45 días sin movimiento",
            "impact": "$5,800 MXN en Capital Financiero Inmovilizado",
            "recommendation": "Activar Venta Cruzada Automática: 15% de descuento en botella al llevar hielos y refrescos mezcladores.",
            "impact_value": 5800,
            "critical": False
        },
        {
            "id": "ALT-004",
            "type": "purple",
            "emoji": "🟣",
            "category": "Demanda Predictiva (Punto de Reorden & Personal)",
            "title": "Concierto Masivo a 2km en 3 días (Est. 25,000 asistentes)",
            "impact": "Riesgo alto de desabasto en cerveza y filas > 15 min en cajas",
            "recommendation": "Pedir sobresurtido predictivo de cerveza (+50 cajas) y programar 2 cajeros extra en turno tarde.",
            "impact_value": 15000,
            "critical": False
        }
    ],
    "Sucursal Monterrey Sur 📍": [
        {
            "id": "ALT-005",
            "type": "red",
            "emoji": "🚨",
            "category": "Perecederos (FEFO)",
            "title": "Lote de 15 Leches Frescas vence en 24 horas",
            "impact": "$650 MXN en Merma Directa",
            "recommendation": "Activar paquete combo promocional con café preparado.",
            "impact_value": 650,
            "critical": True
        },
        {
            "id": "ALT-006",
            "type": "blue",
            "emoji": "🔵",
            "category": "Larga Caducidad (Capital Estancado)",
            "title": "Lote de Whisky Importado 1L suma 52 días sin ventas",
            "impact": "$7,200 MXN inmovilizados en inventario",
            "recommendation": "Reubicar producto a isla de cajas y activar 15% de descuento en combo con hieleras.",
            "impact_value": 7200,
            "critical": False
        }
    ],
    "Sucursal Centro 📍": [
        {
            "id": "ALT-007",
            "type": "purple",
            "emoji": "🟣",
            "category": "Demanda Predictiva (Evento Deportivo)",
            "title": "Partido de Fútbol Clásico en 24 hrs",
            "impact": "Incremento del 300% en demanda de botanas y bolsas de hielo",
            "recommendation": "Surtir 20 bolsas de hielo adicionales y habilitar caja rápida en turno noche.",
            "impact_value": 8500,
            "critical": False
        }
    ]
}

alerts_db = copy.deepcopy(INITIAL_DATA)
executed_count = 0

# -----------------------------------------------------------------------------
# Endpoints HTTP REST API
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify({
        "alerts": alerts_db,
        "executed_count": executed_count
    })

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count
    data = request.get_json() or {}
    branch = data.get("branch")
    alert_id = data.get("alert_id")

    if branch in alerts_db:
        alerts_db[branch] = [a for a in alerts_db[branch] if a["id"] != alert_id]
        executed_count += 1
        return jsonify({
            "success": True,
            "alerts": alerts_db,
            "executed_count": executed_count
        })
    
    return jsonify({"success": False, "error": "Sucursal no encontrada"}), 400

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global alerts_db, executed_count
    alerts_db = copy.deepcopy(INITIAL_DATA)
    executed_count = 0
    return jsonify({
        "success": True,
        "alerts": alerts_db,
        "executed_count": executed_count
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor con 4 Arquetipos iniciado en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
