from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, EventoLocal, MotorAlertas

app = Flask(__name__)

# Mapeo de Sucursales
BRANCH_MAP = {
    "Sucursal 1 - Monterrey Norte 📍": 1,
    "Sucursal 2 - Monterrey Sur 📍": 2,
    "Sucursal 3 - Centro 📍": 3
}

# Datos iniciales estructurados por sucursal que cumplen con las reglas numéricas de Ariel:
# - dias_para_caducar <= 3 (Alerta Roja)
# - volumen_ocupado / volumen_total >= 0.90 (Alerta Amarilla)
# - afluencia_estimada >= 100 (Alerta Morada)
INITIAL_DATA = {
    1: {
        "perecederos": [
            {"id": "S1-RED-1", "producto": "Sándwich de Jamón", "dias_para_caducar": 2, "trafico_sucursal": "alto"},
            {"id": "S1-RED-2", "producto": "Leche Fresca 1L", "dias_para_caducar": 1, "trafico_sucursal": "bajo"}
        ],
        "bodegas": [
            {"id": "S1-YEL-1", "volumen_total_m3": 100.0, "volumen_ocupado_m3": 95.0, "producto_estancado": "Cerveza 12-pack"}
        ],
        "eventos": [
            {"id": "S1-PUR-1", "nombre_evento": "Partido de Fútbol Local", "afluencia_estimada": 300}
        ]
    },
    2: {
        "perecederos": [
            {"id": "S2-RED-1", "producto": "Yogur Griego 1kg", "dias_para_caducar": 2, "trafico_sucursal": "medio"},
            {"id": "S2-RED-2", "producto": "Queso Panela 400g", "dias_para_caducar": 1, "trafico_sucursal": "bajo"}
        ],
        "bodegas": [
            {"id": "S2-YEL-1", "volumen_total_m3": 100.0, "volumen_ocupado_m3": 92.0, "producto_estancado": "Botanas y Sabritas"}
        ],
        "eventos": []
    },
    3: {
        "perecederos": [
            {"id": "S3-RED-1", "producto": "Ensalada César Preparada", "dias_para_caducar": 2, "trafico_sucursal": "alto"}
        ],
        "bodegas": [],
        "eventos": [
            {"id": "S3-PUR-1", "nombre_evento": "Concierto Masivo en Macroplaza", "afluencia_estimada": 500}
        ]
    }
}

state_data = copy.deepcopy(INITIAL_DATA)
executed_count = 0

def generar_alertas():
    """
    Procesa los datos de cada sucursal a través de MotorAlertas (Ariel)
    sin inventar ninguna regla ni campo.
    """
    alertas_dict = {}

    for nombre_sucursal, id_suc in BRANCH_MAP.items():
        suc_data = state_data.get(id_suc, {"perecederos": [], "bodegas": [], "eventos": []})
        suc_alertas = []

        # 1. Alertas Rojas (FEFO)
        for item in suc_data.get("perecederos", []):
            lote = LotePerecedero(
                producto=item["producto"],
                dias_para_caducar=item["dias_para_caducar"],
                trafico_sucursal=item["trafico_sucursal"]
            )
            res = MotorAlertas.procesar_alerta_roja(lote)
            if res:
                res["id"] = item["id"]
                res["critical"] = True
                suc_alertas.append(res)

        # 2. Alertas Amarillas (FIFO)
        for item in suc_data.get("bodegas", []):
            bodega = Bodega(
                volumen_total_m3=item["volumen_total_m3"],
                volumen_ocupado_m3=item["volumen_ocupado_m3"],
                producto_estancado=item["producto_estancado"]
            )
            res = MotorAlertas.procesar_alerta_amarilla(bodega)
            if res:
                res["id"] = item["id"]
                res["critical"] = False
                suc_alertas.append(res)

        # 3. Alertas Moradas (Eventos & Demanda)
        for item in suc_data.get("eventos", []):
            if item.get("afluencia_estimada", 0) >= 100:
                evento = EventoLocal(
                    nombre_evento=item["nombre_evento"],
                    afluencia_estimada=item["afluencia_estimada"]
                )
                res = MotorAlertas.procesar_alerta_morada(evento)
                if res:
                    res["id"] = item["id"]
                    res["critical"] = False
                    suc_alertas.append(res)

        alertas_dict[nombre_sucursal] = suc_alertas

    return alertas_dict

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify({
        "alerts": generar_alertas(),
        "executed_count": executed_count
    })

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count
    data = request.get_json() or {}
    branch_name = data.get("branch")
    alert_id = str(data.get("alert_id", ""))

    id_suc = BRANCH_MAP.get(branch_name, 1)
    suc_data = state_data.get(id_suc, {})

    removido = False

    # Filtrar solo en la sucursal seleccionada
    new_perecederos = [i for i in suc_data.get("perecederos", []) if i["id"] != alert_id]
    if len(new_perecederos) < len(suc_data.get("perecederos", [])):
        suc_data["perecederos"] = new_perecederos
        removido = True

    new_bodegas = [i for i in suc_data.get("bodegas", []) if i["id"] != alert_id]
    if len(new_bodegas) < len(suc_data.get("bodegas", [])):
        suc_data["bodegas"] = new_bodegas
        removido = True

    new_eventos = [i for i in suc_data.get("eventos", []) if i["id"] != alert_id]
    if len(new_eventos) < len(suc_data.get("eventos", [])):
        suc_data["eventos"] = new_eventos
        removido = True

    if removido:
        executed_count += 1

    return jsonify({
        "success": True,
        "alerts": generar_alertas(),
        "executed_count": executed_count
    })

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global state_data, executed_count
    state_data = copy.deepcopy(INITIAL_DATA)
    executed_count = 0
    return jsonify({
        "success": True,
        "alerts": generar_alertas(),
        "executed_count": executed_count
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor con alertas independientes por sucursal iniciado en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
