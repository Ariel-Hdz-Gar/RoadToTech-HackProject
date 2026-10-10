from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, LoteEstancado, EventoLocal, MotorAlertas

# Intentar importar db_connector si TigerGraph está disponible; si no, o falla, fallback a mock_db
try:
    from db_connector import obtener_datos_dashboard
except Exception:
    obtener_datos_dashboard = None

import mock_db

app = Flask(__name__)

BRANCH_MAP = {
    "Sucursal 1 - Monterrey Norte 📍": 1,
    "Sucursal 2 - Monterrey Sur 📍": 2,
    "Sucursal 3 - Centro 📍": 3
}

# Generamos datos multi-sucursal iniciales alineados a las estructuras exactas de Ariel
INITIAL_STORE_DATA = {
    1: {
        "perecederos": copy.deepcopy(mock_db.db_perecederos),
        "bodegas": copy.deepcopy(mock_db.db_bodegas),
        "estancados": copy.deepcopy(mock_db.db_estancados),
        "eventos": copy.deepcopy(mock_db.db_eventos)
    },
    2: {
        "perecederos": [
            {"id_registro": "p2_1", "id_sucursal": 2, "producto": "Yogur Griego 1L", "dias_para_caducar": 2, "stock_actual": 8, "punto_reorden": 30},
            {"id_registro": "p2_2", "id_sucursal": 2, "producto": "Queso Panela", "dias_para_caducar": 1, "stock_actual": 12, "punto_reorden": 25}
        ],
        "bodegas": [
            {"id_registro": "b2_1", "id_sucursal": 2, "volumen_total_m3": 60.0, "volumen_ocupado_m3": 54.0, "producto_estancado": "Sabritas Familiar"}
        ],
        "estancados": [
            {"id_registro": "e2_1", "id_sucursal": 2, "producto": "Café Gourmet Soluble", "dias_sin_vender": 22, "producto_cruzado": "Galletas Avena"}
        ],
        "eventos": []
    },
    3: {
        "perecederos": [
            {"id_registro": "p3_1", "id_sucursal": 3, "producto": "Ensalada Preparada César", "dias_para_caducar": 2, "stock_actual": 5, "punto_reorden": 20}
        ],
        "bodegas": [],
        "estancados": [
            {"id_registro": "e3_1", "id_sucursal": 3, "producto": "Vino Tinto Reserva", "dias_sin_vender": 35, "producto_cruzado": "Queso Maduro"}
        ],
        "eventos": [
            {"id_registro": "ev3_1", "id_sucursal": 3, "nombre_evento": "Festival Macroplaza", "afluencia_estimada": 450, "dias_para_evento": 1}
        ]
    }
}

# Si TigerGraph responde datos reales, los usamos para la sucursal 1
def sincronizar_con_tigergraph():
    if obtener_datos_dashboard:
        try:
            tg_per, tg_bod, tg_est, tg_ev = obtener_datos_dashboard()
            if tg_per or tg_bod or tg_est or tg_ev:
                INITIAL_STORE_DATA[1]["perecederos"] = tg_per or INITIAL_STORE_DATA[1]["perecederos"]
                INITIAL_STORE_DATA[1]["bodegas"] = tg_bod or INITIAL_STORE_DATA[1]["bodegas"]
                INITIAL_STORE_DATA[1]["estancados"] = tg_est or INITIAL_STORE_DATA[1]["estancados"]
                INITIAL_STORE_DATA[1]["eventos"] = tg_ev or INITIAL_STORE_DATA[1]["eventos"]
                print(" Conectado con éxito a datos de TigerGraph!")
        except Exception as e:
            print(" Fallback a datos mock locales (TigerGraph no accesible):", e)

sincronizar_con_tigergraph()

# Estado mutable en vivo
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
            print(f"Error procesando alerta roja: {e}")

    # 2. Alerta Amarilla (FIFO / Bodega)
    for item in suc_items.get("bodegas", []):
        try:
            al = MotorAlertas.procesar_alerta_amarilla(Bodega(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            print(f"Error procesando alerta amarilla: {e}")

    # 3. Alerta Azul (Estancados / Semiperecederos)
    for item in suc_items.get("estancados", []):
        try:
            al = MotorAlertas.procesar_alerta_azul(LoteEstancado(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            print(f"Error procesando alerta azul: {e}")

    # 4. Alerta Morada (Demanda Predictiva / Eventos)
    for item in suc_items.get("eventos", []):
        try:
            al = MotorAlertas.procesar_alerta_morada(EventoLocal(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                alertas.append(al)
        except Exception as e:
            print(f"Error procesando alerta morada: {e}")

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
    print("[RetailPulse] Servidor Web conectado al Motor de Reglas de Ariel en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
