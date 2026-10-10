from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, LoteEstancado, EventoLocal, MotorAlertas

try:
    from db_connector import obtener_datos_dashboard
except Exception:
    obtener_datos_dashboard = None

import mock_db

app = Flask(__name__)

# Mapeo a las 4 Tiendas reales de TigerGraph (Tienda A, B, C, D)
BRANCH_MAP = {
    "Tienda A - Monterrey Norte 📍": 1,
    "Tienda B - Monterrey Sur 📍": 2,
    "Tienda C - Centro 📍": 3,
    "Tienda D - San Pedro 📍": 4
}

# Inicializamos estructuras
INITIAL_STORE_DATA = {
    1: {"perecederos": copy.deepcopy(mock_db.db_perecederos), "bodegas": copy.deepcopy(mock_db.db_bodegas), "estancados": copy.deepcopy(mock_db.db_estancados), "eventos": copy.deepcopy(mock_db.db_eventos)},
    2: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []},
    3: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []},
    4: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []}
}

def sincronizar_con_tigergraph():
    if obtener_datos_dashboard:
        try:
            datos_tg = obtener_datos_dashboard()
            if isinstance(datos_tg, dict):
                for suc_id, items in datos_tg.items():
                    if any(items.values()):
                        INITIAL_STORE_DATA[suc_id] = items
                print(" Conectado con éxito a datos vivos de TigerGraph (Tiendas A, B, C, D)!")
        except Exception as e:
            print(" Fallback local:", e)

sincronizar_con_tigergraph()

# Estado en vivo
state_data = copy.deepcopy(INITIAL_STORE_DATA)
executed_count = 0

def calcular_alertas_sucursal(suc_id: int):
    suc_items = state_data.get(suc_id, {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []})
    alertas = []

    # 1. Alerta Roja (FEFO / Perecederos)
    for item in suc_items.get("perecederos", []):
        try:
            al = MotorAlertas.procesar_alerta_roja(LotePerecedero(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = True
                alertas.append(al)
        except Exception as e:
            pass

    # 2. Alerta Amarilla (FIFO / Bodega)
    for item in suc_items.get("bodegas", []):
        try:
            al = MotorAlertas.procesar_alerta_amarilla(Bodega(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            pass

    # 3. Alerta Azul (Estancados / Semiperecederos)
    for item in suc_items.get("estancados", []):
        try:
            al = MotorAlertas.procesar_alerta_azul(LoteEstancado(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            pass

    # 4. Alerta Morada (Demanda Predictiva / Eventos)
    for item in suc_items.get("eventos", []):
        try:
            al = MotorAlertas.procesar_alerta_morada(EventoLocal(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            pass

    return alertas

def generar_todas_alertas():
    alertas_dict = {}
    for nombre_sucursal, suc_id in BRANCH_MAP.items():
        alertas_dict[nombre_sucursal] = calcular_alertas_sucursal(suc_id)
    return alertas_dict

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify({
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count
    })

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count
    data = request.get_json() or {}
    branch_name = data.get("branch")
    alert_id = str(data.get("alert_id", ""))

    id_suc = BRANCH_MAP.get(branch_name, 1)
    suc_items = state_data.get(id_suc, {})

    removido = False

    for categoria in ["perecederos", "bodegas", "estancados", "eventos"]:
        items = suc_items.get(categoria, [])
        nuevos_items = [i for i in items if str(i.get("id_registro", "")) != alert_id]
        if len(nuevos_items) < len(items):
            suc_items[categoria] = nuevos_items
            removido = True
            break

    if removido:
        executed_count += 1

    return jsonify({
        "success": True,
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count
    })

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global state_data, executed_count
    state_data = copy.deepcopy(INITIAL_STORE_DATA)
    executed_count = 0
    return jsonify({
        "success": True,
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor Web conectado al Motor de Reglas de Ariel y TigerGraph en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
