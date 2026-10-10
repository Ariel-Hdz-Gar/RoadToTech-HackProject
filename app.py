from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python para importar los módulos de Ariel
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, EventoLocal, MotorAlertas
from mock_db import db_perecederos, db_bodegas, db_eventos

app = Flask(__name__)

# Mapeo directo de sucursales a los IDs exactos del Backend de Ariel
BRANCH_MAP = {
    "Sucursal 1 - Monterrey Norte 📍": 1,
    "Sucursal 2 - Monterrey Sur 📍": 2,
    "Sucursal 3 - Centro 📍": 3
}

# Copias en memoria para permitir la simulación de aprobación en vivo
state_perecederos = copy.deepcopy(db_perecederos)
state_bodegas = copy.deepcopy(db_bodegas)
state_eventos = copy.deepcopy(db_eventos)
executed_count = 0

def obtener_alertas_backend(id_sucursal):
    """
    Llama directamente al MotorAlertas de Ariel (motor_reglas.py)
    usando los datos de mock_db.py sin inventar ningún dato ni texto.
    """
    alertas = []

    # 1. Alertas Rojas (Perecederos / FEFO)
    for idx, item in enumerate(state_perecederos):
        if item["id_sucursal"] == id_sucursal:
            lote = LotePerecedero(
                producto=item["producto"],
                dias_para_caducar=item["dias_para_caducar"],
                trafico_sucursal=item["trafico_sucursal"]
            )
            res = MotorAlertas.procesar_alerta_roja(lote)
            if res:
                res["id"] = f"RED-{idx}"
                res["critical"] = True
                alertas.append(res)

    # 2. Alertas Amarillas (Bodega / FIFO)
    for idx, item in enumerate(state_bodegas):
        if item["id_sucursal"] == id_sucursal:
            bodega = Bodega(
                volumen_total_m3=item["volumen_total_m3"],
                volumen_ocupado_m3=item["volumen_ocupado_m3"],
                producto_estancado=item["producto_estancado"]
            )
            res = MotorAlertas.procesar_alerta_amarilla(bodega)
            if res:
                res["id"] = f"YEL-{idx}"
                res["critical"] = False
                alertas.append(res)

    # 3. Alertas Moradas (Eventos / Cajeros y Sobresurtido)
    for idx, item in enumerate(state_eventos):
        if item["id_sucursal"] == id_sucursal:
            if item.get("afluencia_estimada", 0) > 0:
                evento = EventoLocal(
                    nombre_evento=item["nombre_evento"],
                    afluencia_estimada=item["afluencia_estimada"]
                )
                res = MotorAlertas.procesar_alerta_morada(evento)
                if res:
                    res["id"] = f"PUR-{idx}"
                    res["critical"] = False
                    alertas.append(res)

    return alertas

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    alertas_dict = {}
    for nombre_sucursal, id_suc in BRANCH_MAP.items():
        alertas_dict[nombre_sucursal] = obtener_alertas_backend(id_suc)
        
    return jsonify({
        "alerts": alertas_dict,
        "executed_count": executed_count
    })

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count, state_perecederos, state_bodegas, state_eventos
    data = request.get_json() or {}
    branch_name = data.get("branch")
    alert_id = str(data.get("alert_id", ""))

    id_sucursal = BRANCH_MAP.get(branch_name, 1)

    if alert_id.startswith("RED-"):
        idx = int(alert_id.replace("RED-", ""))
        if 0 <= idx < len(state_perecederos):
            state_perecederos.pop(idx)
            executed_count += 1

    elif alert_id.startswith("YEL-"):
        idx = int(alert_id.replace("YEL-", ""))
        if 0 <= idx < len(state_bodegas):
            state_bodegas[idx]["volumen_ocupado_m3"] = 40.0
            executed_count += 1

    elif alert_id.startswith("PUR-"):
        idx = int(alert_id.replace("PUR-", ""))
        if 0 <= idx < len(state_eventos):
            state_eventos.pop(idx)
            executed_count += 1

    alertas_dict = {}
    for nombre_sucursal, id_suc in BRANCH_MAP.items():
        alertas_dict[nombre_sucursal] = obtener_alertas_backend(id_suc)

    return jsonify({
        "success": True,
        "alerts": alertas_dict,
        "executed_count": executed_count
    })

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global state_perecederos, state_bodegas, state_eventos, executed_count
    state_perecederos = copy.deepcopy(db_perecederos)
    state_bodegas = copy.deepcopy(db_bodegas)
    state_eventos = copy.deepcopy(db_eventos)
    executed_count = 0

    alertas_dict = {}
    for nombre_sucursal, id_suc in BRANCH_MAP.items():
        alertas_dict[nombre_sucursal] = obtener_alertas_backend(id_suc)

    return jsonify({
        "success": True,
        "alerts": alertas_dict,
        "executed_count": executed_count
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor conectado con el Backend de Ariel en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
