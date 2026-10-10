from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, EventoLocal, MotorAlertas
from mock_db import db_perecederos, db_bodegas, db_eventos

app = Flask(__name__)

# Mapeo de sucursales entre el Frontend y los IDs de Ariel (Backend)
BRANCH_MAP = {
    "Sucursal Monterrey Norte 📍": 1,
    "Sucursal Monterrey Sur 📍": 2,
    "Sucursal Centro 📍": 3
}

# Estado mutable en memoria para la sesión
state_perecederos = copy.deepcopy(db_perecederos)
state_bodegas = copy.deepcopy(db_bodegas)
state_eventos = copy.deepcopy(db_eventos)
executed_count = 0

def calcular_alertas():
    """ Procesa los datos del backend usando el motor de reglas de Ariel """
    alertas_por_sucursal = {}

    for nombre_sucursal, id_sucursal in BRANCH_MAP.items():
        list_alertas = []

        # 1. Alertas Rojas (Perecederos / Caducidad)
        for idx, item in enumerate(state_perecederos):
            if item.get("id_sucursal") == id_sucursal:
                lote = LotePerecedero(
                    producto=item["producto"],
                    dias_para_caducar=item["dias_para_caducar"],
                    trafico_sucursal=item.get("trafico_sucursal", "alto")
                )
                res = MotorAlertas.procesar_alerta_roja(lote)
                if res:
                    list_alertas.append({
                        "id": f"ALT-RED-{idx}",
                        "type": "red",
                        "emoji": "🚨",
                        "category": res["titulo"],
                        "title": res["descripcion"],
                        "impact": f"Tráfico {item.get('trafico_sucursal', 'alto').upper()} - Riesgo de merma directa",
                        "recommendation": res["recomendacion_inventario"],
                        "impact_value": 2100 if item["dias_para_caducar"] <= 2 else 950,
                        "critical": True,
                        "raw_item": item
                    })

        # 2. Alertas Amarillas (Saturación de Bodega)
        for idx, item in enumerate(state_bodegas):
            if item.get("id_sucursal") == id_sucursal:
                bodega = Bodega(
                    volumen_total_m3=item["volumen_total_m3"],
                    volumen_ocupado_m3=item["volumen_ocupado_m3"],
                    producto_estancado=item["producto_estancado"]
                )
                res = MotorAlertas.procesar_alerta_amarilla(bodega)
                if res:
                    list_alertas.append({
                        "id": f"ALT-YEL-{idx}",
                        "type": "yellow",
                        "emoji": "🟡",
                        "category": res["titulo"],
                        "title": res["descripcion"],
                        "impact": f"Producto Estancado: {item['producto_estancado']}",
                        "recommendation": f"{res['recomendacion_inventario']} | {res['recomendacion_personal']}",
                        "impact_value": 4500,
                        "critical": False,
                        "raw_item": item
                    })

        # 3. Alertas Moradas (Eventos Locales & Personal)
        for idx, item in enumerate(state_eventos):
            if item.get("id_sucursal") == id_sucursal:
                if item.get("afluencia_estimada", 0) > 0:
                    evento = EventoLocal(
                        nombre_evento=item["nombre_evento"],
                        afluencia_estimada=item["afluencia_estimada"]
                    )
                    res = MotorAlertas.procesar_alerta_morada(evento)
                    if res:
                        list_alertas.append({
                            "id": f"ALT-PUR-{idx}",
                            "type": "purple",
                            "emoji": "🟣",
                            "category": res["titulo"],
                            "title": res["descripcion"],
                            "impact": f"Pico de afluencia (+{item['afluencia_estimada']} personas)",
                            "recommendation": f"{res['recomendacion_inventario']} | {res['recomendacion_personal']}",
                            "impact_value": item["afluencia_estimada"] * 50,
                            "critical": False,
                            "raw_item": item
                        })

        alertas_por_sucursal[nombre_sucursal] = list_alertas

    return alertas_por_sucursal

# -----------------------------------------------------------------------------
# Endpoints HTTP REST API
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    alertas = calcular_alertas()
    return jsonify({
        "alerts": alertas,
        "executed_count": executed_count
    })

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count, state_perecederos, state_bodegas, state_eventos
    data = request.get_json() or {}
    branch_name = data.get("branch")
    alert_id = str(data.get("alert_id", ""))

    id_sucursal = BRANCH_MAP.get(branch_name)

    if alert_id.startswith("ALT-RED-"):
        idx = int(alert_id.replace("ALT-RED-", ""))
        if 0 <= idx < len(state_perecederos):
            state_perecederos.pop(idx)
            executed_count += 1

    elif alert_id.startswith("ALT-YEL-"):
        idx = int(alert_id.replace("ALT-YEL-", ""))
        if 0 <= idx < len(state_bodegas):
            # Liberar espacio simulado
            state_bodegas[idx]["volumen_ocupado_m3"] = 40.0
            executed_count += 1

    elif alert_id.startswith("ALT-PUR-"):
        idx = int(alert_id.replace("ALT-PUR-", ""))
        if 0 <= idx < len(state_eventos):
            state_eventos.pop(idx)
            executed_count += 1

    return jsonify({
        "success": True,
        "alerts": calcular_alertas(),
        "executed_count": executed_count
    })

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global state_perecederos, state_bodegas, state_eventos, executed_count
    state_perecederos = copy.deepcopy(db_perecederos)
    state_bodegas = copy.deepcopy(db_bodegas)
    state_eventos = copy.deepcopy(db_eventos)
    executed_count = 0
    return jsonify({
        "success": True,
        "alerts": calcular_alertas(),
        "executed_count": executed_count
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor conectado con motor_reglas.py iniciado en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
