# mock_db.py

# Simulación de la tabla de Inventario Físico (Perecederos)
db_perecederos = [
    {"id_sucursal": 1, "producto": "Sándwich de Jamón", "dias_para_caducar": 2, "trafico_sucursal": "alto"},
    {"id_sucursal": 1, "producto": "Leche Fresca", "dias_para_caducar": 1, "trafico_sucursal": "bajo"},
    {"id_sucursal": 2, "producto": "Yogur Natural", "dias_para_caducar": 8, "trafico_sucursal": "medio"}
]

# Simulación de la tabla de Capacidades de Almacén
db_bodegas = [
    # La sucursal 1 está saturada (95%)
    {"id_sucursal": 1, "volumen_total_m3": 100.0, "volumen_ocupado_m3": 95.0, "producto_estancado": "Cerveza 12-pack"},
    # La sucursal 2 está sana (40%)
    {"id_sucursal": 2, "volumen_total_m3": 100.0, "volumen_ocupado_m3": 40.0, "producto_estancado": "Ninguno"}
]

# Simulación de la tabla de Eventos Georreferenciados
db_eventos = [
    {"id_sucursal": 1, "nombre_evento": "Partido de Fútbol Local", "afluencia_estimada": 300},
    {"id_sucursal": 2, "nombre_evento": "Ninguno", "afluencia_estimada": 0}
]