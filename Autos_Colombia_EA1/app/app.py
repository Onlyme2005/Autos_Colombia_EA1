from datetime import datetime
from pathlib import Path
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = Path(__file__).with_name('autos_colombia.db')

SCHEMA = '''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT NOT NULL UNIQUE,
    telefono TEXT,
    estado TEXT NOT NULL DEFAULT 'ACTIVO'
);
CREATE TABLE IF NOT EXISTS vehiculo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    marca TEXT,
    color TEXT,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);
CREATE TABLE IF NOT EXISTS celda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    zona TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'LIBRE'
        CHECK (estado IN ('LIBRE', 'OCUPADA', 'INHABILITADA'))
);
CREATE TABLE IF NOT EXISTS movimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entrada TEXT NOT NULL,
    salida TEXT,
    estado TEXT NOT NULL DEFAULT 'ACTIVO'
        CHECK (estado IN ('ACTIVO', 'CERRADO')),
    vehiculo_id INTEGER NOT NULL,
    celda_id INTEGER NOT NULL,
    FOREIGN KEY(vehiculo_id) REFERENCES vehiculo(id),
    FOREIGN KEY(celda_id) REFERENCES celda(id)
);
CREATE TABLE IF NOT EXISTS novedad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    prioridad TEXT NOT NULL DEFAULT 'MEDIA'
        CHECK (prioridad IN ('BAJA', 'MEDIA', 'ALTA')),
    movimiento_id INTEGER NOT NULL,
    FOREIGN KEY(movimiento_id) REFERENCES movimiento(id)
);
CREATE TABLE IF NOT EXISTS pago (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor >= 0),
    metodo TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE', 'PAGADO', 'ANULADO')),
    movimiento_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY(movimiento_id) REFERENCES movimiento(id)
);
CREATE INDEX IF NOT EXISTS idx_movimiento_estado ON movimiento(estado);
CREATE INDEX IF NOT EXISTS idx_vehiculo_placa ON vehiculo(placa);
CREATE INDEX IF NOT EXISTS idx_pago_estado ON pago(estado);
'''


def conn():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def now():
    return datetime.now().isoformat(timespec='seconds')


def body():
    return request.get_json(silent=True) or {}


def row_dict(row):
    return dict(row) if row else None


def init_db():
    with conn() as c:
        c.executescript(SCHEMA)
        c.execute("INSERT OR IGNORE INTO usuario(nombre, documento, telefono) VALUES (?, ?, ?)",
                  ('Ana Torres', '100000001', '3000000000'))
        user = c.execute('SELECT id FROM usuario WHERE documento=?', ('100000001',)).fetchone()
        c.execute("INSERT OR IGNORE INTO vehiculo(placa, tipo, marca, color, usuario_id) VALUES (?, ?, ?, ?, ?)",
                  ('ABC123', 'AUTOMOVIL', 'Mazda', 'Gris', user['id']))
        c.execute("INSERT OR IGNORE INTO celda(codigo, zona) VALUES (?, ?)", ('A-01', 'Norte'))
        c.execute("INSERT OR IGNORE INTO celda(codigo, zona) VALUES (?, ?)", ('A-02', 'Norte'))


@app.get('/api/health')
def health():
    return {'ok': True, 'servicio': 'Autos Colombia'}


# ------------------------- Usuarios -------------------------
@app.get('/api/usuarios')
def listar_usuarios():
    buscar = request.args.get('buscar', '').strip()
    with conn() as c:
        if buscar:
            rows = c.execute('''SELECT * FROM usuario
                WHERE nombre LIKE ? OR documento LIKE ? ORDER BY nombre''',
                (f'%{buscar}%', f'%{buscar}%')).fetchall()
        else:
            rows = c.execute('SELECT * FROM usuario ORDER BY nombre').fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/usuarios')
def crear_usuario():
    data = body()
    nombre = (data.get('nombre') or '').strip()
    documento = (data.get('documento') or '').strip()
    telefono = (data.get('telefono') or '').strip()
    if not nombre or not documento:
        return {'error': 'nombre y documento son obligatorios'}, 400
    try:
        with conn() as c:
            cur = c.execute('INSERT INTO usuario(nombre, documento, telefono) VALUES (?, ?, ?)',
                            (nombre, documento, telefono))
            usuario_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return {'error': 'el documento ya está registrado'}, 409
    return {'id': usuario_id, 'mensaje': 'Usuario creado'}, 201


@app.get('/api/usuarios/<int:usuario_id>')
def obtener_usuario(usuario_id):
    with conn() as c:
        usuario = c.execute('SELECT * FROM usuario WHERE id=?', (usuario_id,)).fetchone()
        if not usuario:
            return {'error': 'usuario no encontrado'}, 404
        vehiculos = c.execute('SELECT * FROM vehiculo WHERE usuario_id=? ORDER BY placa', (usuario_id,)).fetchall()
    result = dict(usuario)
    result['vehiculos'] = [dict(v) for v in vehiculos]
    return jsonify(result)


@app.put('/api/usuarios/<int:usuario_id>')
def actualizar_usuario(usuario_id):
    data = body()
    nombre = (data.get('nombre') or '').strip()
    documento = (data.get('documento') or '').strip()
    telefono = (data.get('telefono') or '').strip()
    estado = (data.get('estado') or 'ACTIVO').upper()
    if not nombre or not documento or estado not in ('ACTIVO', 'INACTIVO'):
        return {'error': 'nombre, documento y estado válido son obligatorios'}, 400
    try:
        with conn() as c:
            cur = c.execute('''UPDATE usuario SET nombre=?, documento=?, telefono=?, estado=? WHERE id=?''',
                            (nombre, documento, telefono, estado, usuario_id))
            if cur.rowcount == 0:
                return {'error': 'usuario no encontrado'}, 404
    except sqlite3.IntegrityError:
        return {'error': 'el documento ya está registrado'}, 409
    return {'mensaje': 'Usuario actualizado'}


# ------------------------- Vehículos -------------------------
@app.get('/api/vehiculos')
def listar_vehiculos():
    placa = request.args.get('placa', '').upper().strip()
    usuario_id = request.args.get('usuario_id')
    sql = '''SELECT v.*, u.nombre AS usuario_nombre
             FROM vehiculo v JOIN usuario u ON u.id=v.usuario_id WHERE 1=1'''
    params = []
    if placa:
        sql += ' AND v.placa LIKE ?'
        params.append(f'%{placa}%')
    if usuario_id:
        sql += ' AND v.usuario_id=?'
        params.append(usuario_id)
    sql += ' ORDER BY v.placa'
    with conn() as c:
        rows = c.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/vehiculos')
def crear_vehiculo():
    data = body()
    placa = (data.get('placa') or '').upper().strip()
    tipo = (data.get('tipo') or '').upper().strip()
    marca = (data.get('marca') or '').strip()
    color = (data.get('color') or '').strip()
    usuario_id = data.get('usuario_id')
    if not placa or not tipo or not usuario_id:
        return {'error': 'placa, tipo y usuario_id son obligatorios'}, 400
    try:
        with conn() as c:
            user = c.execute("SELECT id FROM usuario WHERE id=? AND estado='ACTIVO'", (usuario_id,)).fetchone()
            if not user:
                return {'error': 'usuario no encontrado o inactivo'}, 404
            cur = c.execute('''INSERT INTO vehiculo(placa, tipo, marca, color, usuario_id)
                               VALUES (?, ?, ?, ?, ?)''', (placa, tipo, marca, color, usuario_id))
            vehiculo_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return {'error': 'la placa ya está registrada'}, 409
    return {'id': vehiculo_id, 'mensaje': 'Vehículo creado'}, 201


@app.get('/api/vehiculos/<int:vehiculo_id>')
def obtener_vehiculo(vehiculo_id):
    with conn() as c:
        row = c.execute('''SELECT v.*, u.nombre AS usuario_nombre
                           FROM vehiculo v JOIN usuario u ON u.id=v.usuario_id WHERE v.id=?''', (vehiculo_id,)).fetchone()
    if not row:
        return {'error': 'vehículo no encontrado'}, 404
    return jsonify(dict(row))


@app.put('/api/vehiculos/<int:vehiculo_id>')
def actualizar_vehiculo(vehiculo_id):
    data = body()
    placa = (data.get('placa') or '').upper().strip()
    tipo = (data.get('tipo') or '').upper().strip()
    marca = (data.get('marca') or '').strip()
    color = (data.get('color') or '').strip()
    usuario_id = data.get('usuario_id')
    if not placa or not tipo or not usuario_id:
        return {'error': 'placa, tipo y usuario_id son obligatorios'}, 400
    try:
        with conn() as c:
            cur = c.execute('''UPDATE vehiculo SET placa=?, tipo=?, marca=?, color=?, usuario_id=? WHERE id=?''',
                            (placa, tipo, marca, color, usuario_id, vehiculo_id))
            if cur.rowcount == 0:
                return {'error': 'vehículo no encontrado'}, 404
    except sqlite3.IntegrityError:
        return {'error': 'la placa no es válida o ya está registrada'}, 409
    return {'mensaje': 'Vehículo actualizado'}


# ------------------------- Celdas -------------------------
@app.get('/api/celdas')
def listar_celdas():
    estado = request.args.get('estado')
    with conn() as c:
        if estado:
            rows = c.execute('SELECT * FROM celda WHERE estado=? ORDER BY codigo', (estado.upper(),)).fetchall()
        else:
            rows = c.execute('SELECT * FROM celda ORDER BY codigo').fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/celdas')
def crear_celda():
    data = body()
    codigo = (data.get('codigo') or '').upper().strip()
    zona = (data.get('zona') or '').strip()
    if not codigo or not zona:
        return {'error': 'codigo y zona son obligatorios'}, 400
    try:
        with conn() as c:
            cur = c.execute('INSERT INTO celda(codigo, zona) VALUES (?, ?)', (codigo, zona))
            celda_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return {'error': 'el código de celda ya existe'}, 409
    return {'id': celda_id, 'mensaje': 'Celda creada'}, 201


@app.put('/api/celdas/<int:celda_id>')
def actualizar_celda(celda_id):
    data = body()
    codigo = (data.get('codigo') or '').upper().strip()
    zona = (data.get('zona') or '').strip()
    estado = (data.get('estado') or '').upper().strip()
    if not codigo or not zona or estado not in ('LIBRE', 'OCUPADA', 'INHABILITADA'):
        return {'error': 'codigo, zona y estado válido son obligatorios'}, 400
    with conn() as c:
        actual = c.execute('SELECT estado FROM celda WHERE id=?', (celda_id,)).fetchone()
        if not actual:
            return {'error': 'celda no encontrada'}, 404
        if actual['estado'] == 'OCUPADA' and estado == 'INHABILITADA':
            return {'error': 'no se puede inhabilitar una celda ocupada'}, 409
        try:
            c.execute('UPDATE celda SET codigo=?, zona=?, estado=? WHERE id=?', (codigo, zona, estado, celda_id))
        except sqlite3.IntegrityError:
            return {'error': 'el código de celda ya existe'}, 409
    return {'mensaje': 'Celda actualizada'}


# ------------------------- Movimientos -------------------------
@app.get('/api/movimientos/activos')
def movimientos_activos():
    with conn() as c:
        rows = c.execute('''SELECT m.id, v.placa, c.codigo AS celda, m.entrada
            FROM movimiento m JOIN vehiculo v ON v.id=m.vehiculo_id
            JOIN celda c ON c.id=m.celda_id WHERE m.estado='ACTIVO' ORDER BY m.entrada DESC''').fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/entradas')
def registrar_entrada():
    data = body()
    placa = (data.get('placa') or '').upper().strip()
    celda_id = data.get('celda_id')
    if not placa or not celda_id:
        return {'error': 'placa y celda_id son obligatorios'}, 400
    with conn() as c:
        v = c.execute('''SELECT v.id FROM vehiculo v JOIN usuario u ON u.id=v.usuario_id
                         WHERE v.placa=? AND u.estado='ACTIVO' ''', (placa,)).fetchone()
        if not v:
            return {'error': 'vehículo no registrado o usuario inactivo'}, 404
        cell = c.execute("SELECT * FROM celda WHERE id=? AND estado='LIBRE'", (celda_id,)).fetchone()
        if not cell:
            return {'error': 'celda no disponible'}, 409
        active = c.execute("SELECT id FROM movimiento WHERE vehiculo_id=? AND estado='ACTIVO'", (v['id'],)).fetchone()
        if active:
            return {'error': 'el vehículo ya tiene una entrada activa'}, 409
        timestamp = now()
        cur = c.execute('''INSERT INTO movimiento(entrada, vehiculo_id, celda_id)
                           VALUES (?, ?, ?)''', (timestamp, v['id'], celda_id))
        c.execute("UPDATE celda SET estado='OCUPADA' WHERE id=?", (celda_id,))
    return {'id': cur.lastrowid, 'mensaje': 'Entrada registrada', 'entrada': timestamp}, 201


@app.post('/api/salidas/<int:movimiento_id>')
def registrar_salida(movimiento_id):
    with conn() as c:
        movement = c.execute("SELECT * FROM movimiento WHERE id=? AND estado='ACTIVO'", (movimiento_id,)).fetchone()
        if not movement:
            return {'error': 'movimiento activo no encontrado'}, 404
        finished_at = datetime.now()
        started_at = datetime.fromisoformat(movement['entrada'])
        hours = max(1, int((finished_at - started_at).total_seconds() // 3600) + 1)
        value = hours * 3000
        timestamp = finished_at.isoformat(timespec='seconds')
        c.execute("UPDATE movimiento SET salida=?, estado='CERRADO' WHERE id=?", (timestamp, movimiento_id))
        c.execute("UPDATE celda SET estado='LIBRE' WHERE id=?", (movement['celda_id'],))
        c.execute('''INSERT OR IGNORE INTO pago(fecha, valor, metodo, estado, movimiento_id)
                     VALUES (?, ?, 'EFECTIVO', 'PENDIENTE', ?)''', (timestamp, value, movimiento_id))
    return {'mensaje': 'Salida registrada', 'movimiento_id': movimiento_id, 'horas': hours,
            'valor_estimado': value, 'estado_pago': 'PENDIENTE'}


# ------------------------- Novedades -------------------------
@app.get('/api/novedades')
def listar_novedades():
    with conn() as c:
        rows = c.execute('''SELECT n.*, v.placa FROM novedad n
                            JOIN movimiento m ON m.id=n.movimiento_id
                            JOIN vehiculo v ON v.id=m.vehiculo_id
                            ORDER BY n.fecha DESC''').fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/novedades')
def crear_novedad():
    data = body()
    descripcion = (data.get('descripcion') or '').strip()
    prioridad = (data.get('prioridad') or 'MEDIA').upper()
    movimiento_id = data.get('movimiento_id')
    if not descripcion or not movimiento_id:
        return {'error': 'descripcion y movimiento_id son obligatorios'}, 400
    if prioridad not in ('BAJA', 'MEDIA', 'ALTA'):
        return {'error': 'prioridad debe ser BAJA, MEDIA o ALTA'}, 400
    with conn() as c:
        movement = c.execute('SELECT id FROM movimiento WHERE id=?', (movimiento_id,)).fetchone()
        if not movement:
            return {'error': 'movimiento no encontrado'}, 404
        cur = c.execute('''INSERT INTO novedad(fecha, descripcion, prioridad, movimiento_id)
                           VALUES (?, ?, ?, ?)''', (now(), descripcion, prioridad, movimiento_id))
    return {'id': cur.lastrowid, 'mensaje': 'Novedad registrada'}, 201


# ------------------------- Pagos -------------------------
@app.get('/api/pagos')
def listar_pagos():
    estado = request.args.get('estado')
    with conn() as c:
        sql = '''SELECT p.*, v.placa FROM pago p
                 JOIN movimiento m ON m.id=p.movimiento_id
                 JOIN vehiculo v ON v.id=m.vehiculo_id'''
        params = []
        if estado:
            sql += ' WHERE p.estado=?'
            params.append(estado.upper())
        sql += ' ORDER BY p.fecha DESC'
        rows = c.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post('/api/pagos')
def registrar_pago():
    data = body()
    movimiento_id = data.get('movimiento_id')
    metodo = (data.get('metodo') or '').upper().strip()
    valor = data.get('valor')
    if not movimiento_id or not metodo:
        return {'error': 'movimiento_id y metodo son obligatorios'}, 400
    if metodo not in ('EFECTIVO', 'TARJETA', 'TRANSFERENCIA'):
        return {'error': 'metodo debe ser EFECTIVO, TARJETA o TRANSFERENCIA'}, 400
    with conn() as c:
        pending = c.execute('SELECT * FROM pago WHERE movimiento_id=?', (movimiento_id,)).fetchone()
        if not pending:
            return {'error': 'no existe un pago pendiente para el movimiento'}, 404
        if pending['estado'] == 'PAGADO':
            return {'error': 'el movimiento ya está pagado'}, 409
        amount = float(valor) if valor is not None else pending['valor']
        if amount < 0:
            return {'error': 'el valor no puede ser negativo'}, 400
        c.execute('''UPDATE pago SET fecha=?, valor=?, metodo=?, estado='PAGADO'
                     WHERE movimiento_id=?''', (now(), amount, metodo, movimiento_id))
        payment = c.execute('SELECT * FROM pago WHERE movimiento_id=?', (movimiento_id,)).fetchone()
    return {'id': payment['id'], 'mensaje': 'Pago registrado', 'recibo': f'REC-{payment["id"]:06d}',
            'valor': payment['valor'], 'metodo': payment['metodo'], 'estado': payment['estado']}, 201


# ------------------------- Reporte -------------------------
@app.get('/api/reportes/resumen')
def resumen():
    with conn() as c:
        result = c.execute('''SELECT
            (SELECT COUNT(*) FROM usuario WHERE estado='ACTIVO') AS usuarios_activos,
            (SELECT COUNT(*) FROM vehiculo) AS vehiculos_registrados,
            (SELECT COUNT(*) FROM celda) AS celdas_totales,
            (SELECT COUNT(*) FROM celda WHERE estado='LIBRE') AS celdas_libres,
            (SELECT COUNT(*) FROM celda WHERE estado='OCUPADA') AS celdas_ocupadas,
            (SELECT COUNT(*) FROM movimiento WHERE estado='ACTIVO') AS movimientos_activos,
            (SELECT COUNT(*) FROM novedad) AS novedades,
            (SELECT COALESCE(SUM(valor), 0) FROM pago WHERE estado='PAGADO') AS total_pagado''').fetchone()
    return jsonify(dict(result))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
