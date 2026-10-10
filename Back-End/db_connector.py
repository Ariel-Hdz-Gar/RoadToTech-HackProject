import os
import pyTigerGraph as tg
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("TG_HOST", "https://tg-093610e2-1857-4033-9a1d-cef73f96b292.tg-2635877100.i.tgcloud.io")
GRAPHNAME = os.getenv("TG_GRAPHNAME", "tienda")
SECRET = os.getenv("TG_SECRET", "0jujff12ddervneota0heiuf5sql1894")

def conectar_tigerdata():
    try:
        conn = tg.TigerGraphConnection(
            host=HOST,
            graphname=GRAPHNAME,
            gsqlSecret=SECRET
        )
        conn.getToken(SECRET)
        return conn
    except Exception as e:
        print(f"Error conectando a TigerGraph: {e}")
        return None

def resolver_accion_tigergraph(v_id: str, tipo_alerta: str):
    conn = conectar_tigerdata()
    if not conn:
        return False
    try:
        vertex = conn.getVerticesById("inventario", v_id)
        if not vertex:
            return False
        
        attr = vertex[0].get("attributes", {})
        cant_actual = int(attr.get("cantidad", 100))
        nueva_cantidad = cant_actual
        
        if tipo_alerta == "roja":
            nueva_cantidad += 100
            print(f"[OK] Reabastecimiento (Roja) aprobado: {v_id} incrementa a {nueva_cantidad}.")
        elif tipo_alerta == "azul":
            nueva_cantidad = max(0, nueva_cantidad - 20)
            print(f"[OK] Venta cruzada (Azul) aprobada: {v_id} baja a {nueva_cantidad}.")
        elif tipo_alerta == "morada":
            nueva_cantidad += 150
            print(f"[OK] Sobresurtido (Morada) aprobado: {v_id} incrementa a {nueva_cantidad}.")
        elif tipo_alerta == "amarilla":
            nueva_cantidad = max(0, nueva_cantidad - 30)
            print(f"[OK] Optimización espacio (Amarilla) aprobada: {v_id} baja a {nueva_cantidad}.")
            
        conn.upsertVertex("inventario", v_id, attributes={"cantidad": nueva_cantidad})
        return True
    except Exception as e:
        print(f"Error actualizando en TigerGraph: {e}")
        return False

# ROPs exactos sacados de Proyecto_Completo_RetailPulse_7CS.xlsx
ROPS_EXACTOS = {
    1: {"Leche": 97, "Jamón": 62, "Donas": 57, "Paketaxo": 78, "Atún": 57, "Cerveza": 176},
    2: {"Leche": 69, "Jamón": 76, "Donas": 85, "Paketaxo": 92, "Atún": 78, "Cerveza": 120},
    3: {"Leche": 55, "Jamón": 48, "Donas": 92, "Paketaxo": 155, "Atún": 36, "Cerveza": 337},
    4: {"Leche": 111, "Jamón": 104, "Donas": 57, "Paketaxo": 120, "Atún": 92, "Cerveza": 225}
}

# Alertas activas por tienda en el Excel
ALERTAS_ACTIVAS = {
    1: {"Leche": "roja", "Jamón": "roja"},
    2: {"Donas": "roja", "Atún": "amarilla"},
    3: {"Paketaxo": "amarilla", "Cerveza": "azul"},
    4: {"Jamón": "roja", "Donas": "amarilla"}
}

def obtener_datos_dashboard():
    conn = conectar_tigerdata()
    if not conn:
        return None

    try:
        inventario_raw = conn.getVertices("inventario")
    except Exception as e:
        print(f"Error consultando vértices de TigerGraph: {e}")
        return None

    fecha_hoy = datetime.now()
    tiendas_map = {"A": 1, "B": 2, "C": 3, "D": 4}

    por_tienda = {
        1: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []},
        2: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []},
        3: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []},
        4: {"perecederos": [], "bodegas": [], "estancados": [], "eventos": []}
    }

    for item in inventario_raw:
        attr = item.get("attributes", {})
        v_id = item.get("v_id", "")
        
        partes = v_id.split("_")
        letra_tienda = partes[1] if len(partes) > 1 and partes[1] in tiendas_map else "A"
        suc_id = tiendas_map.get(letra_tienda, 1)

        prod = attr.get("nombre_producto", v_id)
        cant = int(attr.get("cantidad", 100))
        
        # Obtenemos ROP
        rop_sucursal = ROPS_EXACTOS.get(suc_id, {}).get(prod, 50)
        
        # Revisamos si este producto en esta tienda dispara alerta según el Excel
        tipo_alerta = ALERTAS_ACTIVAS.get(suc_id, {}).get(prod)

        dias_caducidad = 3

        if tipo_alerta == "roja":
            por_tienda[suc_id]["perecederos"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "producto": prod,
                "dias_para_caducar": dias_caducidad,
                "stock_actual": cant,
                "punto_reorden": rop_sucursal
            })
        elif tipo_alerta == "amarilla":
            por_tienda[suc_id]["bodegas"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "producto": prod,
                "volumen_total_m3": 100.0,
                "volumen_ocupado_m3": 90.0,
                "producto_estancado": prod
            })
        elif tipo_alerta == "azul":
            por_tienda[suc_id]["estancados"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "producto": prod,
                "dias_sin_vender": 12,
                "producto_cruzado": "Combo Promo"
            })

    return por_tienda