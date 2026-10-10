from flask import Flask, render_template, jsonify, request
import copy
import sys
import os

# Agregar la carpeta Back-End al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "Back-End"))

from motor_reglas import LotePerecedero, Bodega, LoteEstancado, EventoLocal, MotorAlertas

try:
    from db_connector import obtener_datos_dashboard, resolver_accion_tigergraph
except Exception:
    obtener_datos_dashboard = None
    resolver_accion_tigergraph = None

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
total_saved_mxn = 0.0
total_original_loss_mxn = 0.0
active_promos_data = {1: [], 2: [], 3: [], 4: []}

def calcular_alertas_sucursal(suc_id: int):
    # ... (no changes to this function, keeping it as is) ...
    suc_items = state_data.get(suc_id, {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []})
    alertas = []

    for item in suc_items.get("perecederos", []):
        try:
            al = MotorAlertas.procesar_alerta_roja(LotePerecedero(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = True
                al["producto"] = item["producto"]
                alertas.append(al)
        except Exception:
            pass

    for item in suc_items.get("bodegas", []):
        try:
            al = MotorAlertas.procesar_alerta_amarilla(Bodega(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                al["producto"] = item["producto"]
                alertas.append(al)
        except Exception:
            pass

    for item in suc_items.get("estancados", []):
        try:
            al = MotorAlertas.procesar_alerta_azul(LoteEstancado(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                al["producto"] = item["producto"]
                alertas.append(al)
        except Exception:
            pass

    for item in suc_items.get("eventos", []):
        try:
            al = MotorAlertas.procesar_alerta_morada(EventoLocal(**item))
            if al:
                al["id"] = item["id_registro"]
                al["critical"] = False
                al["producto"] = item["producto"]
                alertas.append(al)
        except Exception:
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

@app.route("/cliente")
def cliente():
    return render_template("cliente.html")

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify({
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count,
        "total_saved_mxn": round(total_saved_mxn, 2),
        "total_original_loss_mxn": round(total_original_loss_mxn, 2)
    })

@app.route("/api/promos/<branch_name>", methods=["GET"])
def get_promos(branch_name):
    id_suc = BRANCH_MAP.get(branch_name, 1)
    promos = active_promos_data.get(id_suc, [])
    return jsonify({"promos": promos})

@app.route("/api/alerts/approve", methods=["POST"])
def approve_alert():
    global executed_count, total_saved_mxn, total_original_loss_mxn
    data = request.get_json() or {}
    branch_name = data.get("branch")
    alert_id = str(data.get("alert_id", ""))
    saved_amount = float(data.get("saved_amount", 0.0))
    original_loss = float(data.get("original_loss_amount", 0.0))
    promo_text = data.get("promo_text", "")
    producto_name = data.get("producto", "")

    id_suc = BRANCH_MAP.get(branch_name, 1)
    suc_items = state_data.get(id_suc, {})

    removido = False

    for categoria in ["perecederos", "bodegas", "estancados", "eventos"]:
        items = suc_items.get(categoria, [])
        item_to_remove = next((i for i in items if str(i.get("id_registro", "")) == alert_id), None)
        
        if item_to_remove:
            if not producto_name:
                producto_name = item_to_remove.get("producto", "")
                
            if not promo_text:
                try:
                    if categoria == "perecederos":
                        al = MotorAlertas.procesar_alerta_roja(LotePerecedero(**item_to_remove))
                    elif categoria == "bodegas":
                        al = MotorAlertas.procesar_alerta_amarilla(Bodega(**item_to_remove))
                    elif categoria == "estancados":
                        al = MotorAlertas.procesar_alerta_azul(LoteEstancado(**item_to_remove))
                    else:
                        al = MotorAlertas.procesar_alerta_morada(EventoLocal(**item_to_remove))
                    
                    if al:
                        promo_text = al.get("recomendacion_inventario", "")
                except Exception:
                    pass

            nuevos_items = [i for i in items if str(i.get("id_registro", "")) != alert_id]
            suc_items[categoria] = nuevos_items
            removido = True
            
            if resolver_accion_tigergraph:
                tipo = "roja" if categoria == "perecederos" else ("amarilla" if categoria == "bodegas" else ("azul" if categoria == "estancados" else "morada"))
                resolver_accion_tigergraph(alert_id, tipo)
            break

    if removido:
        executed_count += 1
        total_saved_mxn += saved_amount
        total_original_loss_mxn += original_loss
        
        # Registrar la promo para el cliente final
        if promo_text and producto_name:
            import uuid
            active_promos_data[id_suc].insert(0, {
                "id": str(uuid.uuid4()),
                "producto": producto_name,
                "oferta": promo_text
            })

    return jsonify({
        "success": True,
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count,
        "total_saved_mxn": round(total_saved_mxn, 2),
        "total_original_loss_mxn": round(total_original_loss_mxn, 2)
    })

@app.route("/api/alerts/reset", methods=["POST"])
def reset_alerts():
    global state_data, executed_count, total_saved_mxn, total_original_loss_mxn, active_promos_data
    state_data = copy.deepcopy(INITIAL_STORE_DATA)
    executed_count = 0
    total_saved_mxn = 0.0
    total_original_loss_mxn = 0.0
    active_promos_data = {1: [], 2: [], 3: [], 4: []}
    return jsonify({
        "success": True,
        "alerts": generar_todas_alertas(),
        "executed_count": executed_count,
        "total_saved_mxn": 0.0,
        "total_original_loss_mxn": 0.0
    })

if __name__ == "__main__":
    print("[RetailPulse] Servidor Web conectado al Motor de Reglas de Ariel y TigerGraph en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
