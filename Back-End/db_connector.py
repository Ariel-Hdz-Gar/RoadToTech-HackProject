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
        print(f"Error conectando a TigerGraph: {e}")
        return None

def resolver_accion_tigergraph(v_id: str, tipo_alerta: str):
    """
    Cuando el gerente aprueba la acción, actualizamos el inventario en TigerGraph:
    - Roja (FEFO / Reabastecimiento): Reabastece inventario a 250 unidades
    """
    conn = conectar_tigerdata()
    if not conn:
        return False
    try:
        if tipo_alerta == "roja":
            conn.upsertVertex("inventario", v_id, attributes={"cantidad": 250})
            print(f"[OK] TigerGraph actualizado en la nube: {v_id} reabastecido con exito.")
        return True
    except Exception as e:
        print(f"Error actualizando en TigerGraph: {e}")
        return False

# Perfiles de consumo diferenciados por sucursal
PERFILES_SUCURSAL = {
    1: {
        "nombre": "Tienda A - Monterrey Norte (Zona Estadio)",
        "evento": "Clásico Regio (Estadio Universitario)",
        "afluencia": 600,
        "dias_evento": 2,
        "producto_evento": "Cerveza y Botanas",
        "ropa": {"Leche": 90, "Jamón": 60, "Donas": 12, "Paketaxo": 10, "Atún": 20, "Cerveza": 15}
    },
    2: {
        "nombre": "Tienda B - Monterrey Sur (Campus Universitario)",
        "evento": "Semana de Exámenes y Feria Estudiantil",
        "afluencia": 280,
        "dias_evento": 1,
        "producto_evento": "Café, Donas y Snacks",
        "ropa": {"Leche": 70, "Jamón": 45, "Donas": 25, "Paketaxo": 12, "Atún": 18, "Cerveza": 8}
    },
    3: {
        "nombre": "Tienda C - Centro (Macroplaza)",
        "evento": "Festival de Música y Gastronomía",
        "afluencia": 850,
        "dias_evento": 3,
        "producto_evento": "Bebidas Hidratantes, Cerveza y Enlatados",
        "ropa": {"Leche": 80, "Jamón": 55, "Donas": 15, "Paketaxo": 8, "Atún": 30, "Cerveza": 22}
    },
    4: {
        "nombre": "Tienda D - San Pedro (Distrito Financiero)",
        "evento": "Cierre de Trimestre Corporativo y Exposiciones",
        "afluencia": 320,
        "dias_evento": 2,
        "producto_evento": "Alimentos Preparados, Panadería y Lácteos",
        "ropa": {"Leche": 110, "Jamón": 80, "Donas": 18, "Paketaxo": 6, "Atún": 25, "Cerveza": 10}
    }
}

def obtener_datos_dashboard():
    """ 
    Extrae los datos reales de TigerGraph y los clasifica por Tienda (A=1, B=2, C=3, D=4)
    con ROP dinámicos por perfil socioeconómico y eventos diferenciados.
    """
    conn = conectar_tigerdata()
    if not conn:
        return None

    try:
        inventario_raw = conn.getVertices("inventario")
    except Exception as e:
        print(f"Error consultando vértices de TigerGraph: {e}")
        return None

    fecha_hoy = datetime.strptime("2026-10-10", "%Y-%m-%d")
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
        perfil = PERFILES_SUCURSAL.get(suc_id, PERFILES_SUCURSAL[1])

        prod = attr.get("nombre_producto", v_id)
        cant = int(attr.get("cantidad", 100))
        
        dias_caducidad = 3
        if "fecha_caducidad" in attr and attr["fecha_caducidad"]:
            try:
                fecha_cad = datetime.strptime(str(attr["fecha_caducidad"])[:10], "%Y-%m-%d")
                dias_caducidad = (fecha_cad - fecha_hoy).days
            except Exception:
                dias_caducidad = 2

        # ROP específico para esta sucursal y producto
        rop_sucursal = perfil["ropa"].get(prod, 50)

        # 1. Alerta Roja: Perecederos críticos (Leche, Jamón)
        if prod in ["Leche", "Jamón"]:
            por_tienda[suc_id]["perecederos"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "producto": prod,
                "dias_para_caducar": max(1, dias_caducidad),
                "stock_actual": cant,
                "punto_reorden": rop_sucursal
            })

        # 2. Alerta Amarilla: Volumen y saturación (Paketaxo)
        elif prod == "Paketaxo":
            volumen_ocupado = min(96.0, 72.0 + (cant / 16.0))
            por_tienda[suc_id]["bodegas"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "volumen_total_m3": 100.0,
                "volumen_ocupado_m3": round(volumen_ocupado, 1),
                "producto_estancado": f"Paketaxo ({cant} bolsas)"
            })

        # 3. Alerta Azul: Semiperecederos lenta rotación (Donas)
        elif prod == "Donas":
            dias_lenta = 16 if suc_id in [1, 4] else 22
            cruzado = "Café Americano" if suc_id == 2 else ("Leche Entera" if suc_id == 1 else "Bebida Caliente")
            por_tienda[suc_id]["estancados"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "producto": "Donas de pan paquete",
                "dias_sin_vender": dias_lenta,
                "producto_cruzado": cruzado
            })

        # 4. Alerta Morada: Evento Predictivo diferenciado por ubicación
        elif prod == "Cerveza":
            por_tienda[suc_id]["eventos"].append({
                "id_registro": v_id,
                "id_sucursal": suc_id,
                "nombre_evento": perfil["evento"],
                "afluencia_estimada": perfil["afluencia"],
                "dias_para_evento": perfil["dias_evento"]
            })

    return por_tienda