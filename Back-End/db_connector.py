import pyTigerGraph as tg
from datetime import datetime

# Credenciales exactas y vivas del Workspace en TigerGraph Cloud Savanna v4
HOST = "https://tg-093610e2-1857-4033-9a1d-cef73f96b292.tg-2635877100.i.tgcloud.io"
GRAPHNAME = "tienda"
SECRET = "0jujff12ddervneota0heiuf5sql1894"

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
        print(f"❌ Error conectando a TigerGraph: {e}")
        return None

def obtener_datos_dashboard():
    """ Extrae los datos reales de TigerGraph y los formatea para el motor de reglas """
    conn = conectar_tigerdata()
    if not conn:
        return [], [], [], []

    try:
        inventario_raw = conn.getVertices("inventario")
        almacen_raw = conn.getVertices("almacen")
    except Exception as e:
        print(f"Error consultando vértices de TigerGraph: {e}")
        return [], [], [], []

    fecha_hoy = datetime.now()

    db_perecederos = []
    db_estancados = []
    
    # Procesar Inventario según el esquema real de Michelle:
    # inventario ['nombre_producto', 'fecha_caducidad', 'cantidad']
    for item in inventario_raw:
        attr = item.get("attributes", {})
        v_id = item.get("v_id", "")
        
        dias_caducidad = 3
        if "fecha_caducidad" in attr and attr["fecha_caducidad"]:
            try:
                fecha_cad = datetime.strptime(str(attr["fecha_caducidad"])[:10], "%Y-%m-%d")
                dias_caducidad = (fecha_cad - fecha_hoy).days
            except Exception:
                dias_caducidad = 2

        cant = attr.get("cantidad", 10)
        prod = attr.get("nombre_producto", v_id)

        # Regla: Perecedero
        db_perecederos.append({
            "id_registro": str(v_id),
            "id_sucursal": 1,
            "producto": prod,
            "dias_para_caducar": dias_caducidad,
            "stock_actual": cant,
            "punto_reorden": max(15, int(cant * 1.5))
        })

    # Procesar Almacén según el esquema real de Michelle:
    # almacen ['capacidad_max_m3', 'ocupacion_actual_m3']
    db_bodegas = []
    for item in almacen_raw:
        attr = item.get("attributes", {})
        v_id = item.get("v_id", "")
        db_bodegas.append({
            "id_registro": str(v_id),
            "id_sucursal": 1,
            "volumen_total_m3": float(attr.get("capacidad_max_m3", 100.0)),
            "volumen_ocupado_m3": float(attr.get("ocupacion_actual_m3", 92.0)),
            "producto_estancado": "Lote General Almacén"
        })

    db_eventos = []

    return db_perecederos, db_bodegas, db_estancados, db_eventos