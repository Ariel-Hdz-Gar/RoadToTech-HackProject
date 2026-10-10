import pyTigerGraph as tg
from datetime import datetime

def conectar_tigerdata():
    try:
        conn = tg.TigerGraphConnection(
            host="https://<tu-cluster-id>.i.tgcloud.io",
            graphname="tienda",          
            username="tigergraph",        
            password="mich26061226",
            restppPort="443"
        )
        conn.getToken(conn.createSecret())
        return conn
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def obtener_datos_dashboard():
    """ Extrae los datos reales de TigerGraph y los formatea para tu motor """
    conn = conectar_tigerdata()
    if not conn:
        return [], [], [], []

    # 1. Traer todos los vértices de la DB
    inventario_raw = conn.getVertices("inventario")
    almacen_raw = conn.getVertices("almacen")
    evento_raw = conn.getVertices("evento")

    # Fecha simulada actual (basada en las fechas que usó Michelle en el script)
    fecha_hoy = datetime.strptime("2026-10-09", "%Y-%m-%d")

    db_perecederos = []
    db_estancados = []
    
    # Procesar Inventario
    for item in inventario_raw:
        attr = item["attributes"]
        v_id = item["v_id"]
        
        # Calcular días para caducar
        fecha_cad = datetime.strptime(attr["fecha_caducidad"][:10], "%Y-%m-%d")
        dias_caducidad = (fecha_cad - fecha_hoy).days

        # Separar en Roja (Perecederos) y Azul (Estancados)
        if attr["categoria"] == "perecederos":
            db_perecederos.append({
                "id_registro": v_id,
                "id_sucursal": 1,
                "producto": attr["nombre_producto"],
                "dias_para_caducar": dias_caducidad,
                "stock_actual": attr["stock_actual"],
                "punto_reorden": attr["punto_reorden"]
            })
        elif attr["categoria"] == "snacks" and attr["dias_sin_vender"] >= 10:
            db_estancados.append({
                "id_registro": v_id,
                "id_sucursal": 1,
                "producto": attr["nombre_producto"],
                "dias_sin_vender": attr["dias_sin_vender"],
                "producto_cruzado": "Leche Entera" # Simulado desde el Edge en TigerGraph
            })

    # Procesar Bodegas (Alerta Amarilla)
    db_bodegas = []
    for item in almacen_raw:
        attr = item["attributes"]
        db_bodegas.append({
            "id_registro": item["v_id"],
            "id_sucursal": 1,
            "volumen_total_m3": attr["volumen_total_m3"],
            "volumen_ocupado_m3": attr["volumen_ocupado_m3"],
            "producto_estancado": "Paketaxo"
        })

    # Procesar Eventos (Alerta Morada)
    db_eventos = []
    for item in evento_raw:
        attr = item["attributes"]
        fecha_ev = datetime.strptime(attr["fecha_evento"][:10], "%Y-%m-%d")
        dias_evento = (fecha_ev - fecha_hoy).days
        
        db_eventos.append({
            "id_registro": item["v_id"],
            "id_sucursal": 1,
            "nombre_evento": attr["nombre_evento"],
            "afluencia_estimada": attr["afluencia_estimada"],
            "dias_para_evento": dias_evento
        })

    return db_perecederos, db_bodegas, db_estancados, db_eventos