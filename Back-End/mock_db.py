# mock_db.py

db_perecederos = [
    {"id_registro": "p1", "id_sucursal": 1, "producto": "Leche Entera", "dias_para_caducar": 3, "stock_actual": 10, "punto_reorden": 78},
    {"id_registro": "p2", "id_sucursal": 1, "producto": "Jamón", "dias_para_caducar": 4, "stock_actual": 15, "punto_reorden": 52}
]

db_bodegas = [
    {"id_registro": "b1", "id_sucursal": 1, "volumen_total_m3": 50.0, "volumen_ocupado_m3": 42.0, "producto_estancado": "Paketaxo"}
]

db_estancados = [
    {"id_registro": "e1", "id_sucursal": 1, "producto": "Donas de pan paquete", "dias_sin_vender": 15, "producto_cruzado": "Leche Entera"}
]

db_eventos = [
    {"id_registro": "ev1", "id_sucursal": 1, "nombre_evento": "Fin de Semana Quincenal", "afluencia_estimada": 150, "dias_para_evento": 2}
]