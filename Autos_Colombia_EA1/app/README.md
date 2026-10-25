# Autos Colombia — API Iteración 1

## Ejecutar localmente

1. Instala Python 3.10+.
2. En esta carpeta crea un entorno virtual: `python -m venv .venv`.
3. Actívalo en Windows con `.venv\\Scripts\\activate` o en macOS/Linux con `source .venv/bin/activate`.
4. Instala dependencias: `pip install -r requirements.txt`.
5. Inicia la API: `python app.py`.
6. Abre `http://127.0.0.1:5000/api/health`.

La aplicación crea automáticamente `autos_colombia.db` y las tablas `usuario`, `vehiculo`, `celda`, `movimiento`, `novedad` y `pago`.

## Endpoints

### Usuarios

- `GET /api/usuarios?buscar=Ana` — listar o buscar usuarios.
- `POST /api/usuarios` — crear usuario. Body: `{ "nombre": "Carlos Pérez", "documento": "100000002", "telefono": "3111111111" }`.
- `GET /api/usuarios/<id>` — consultar usuario con sus vehículos.
- `PUT /api/usuarios/<id>` — actualizar nombre, documento, teléfono y estado.

### Vehículos

- `GET /api/vehiculos?placa=ABC` — listar o buscar por placa.
- `POST /api/vehiculos` — crear vehículo. Body: `{ "placa": "XYZ789", "tipo": "AUTOMOVIL", "marca": "Renault", "color": "Blanco", "usuario_id": 2 }`.
- `GET /api/vehiculos/<id>` — consultar vehículo.
- `PUT /api/vehiculos/<id>` — actualizar vehículo.

### Celdas

- `GET /api/celdas` — listar todas las celdas.
- `GET /api/celdas?estado=LIBRE` — listar por estado.
- `POST /api/celdas` — crear celda. Body: `{ "codigo": "B-01", "zona": "Sur" }`.
- `PUT /api/celdas/<id>` — actualizar código, zona y estado.

### Entradas y salidas

- `GET /api/movimientos/activos` — consultar vehículos dentro.
- `POST /api/entradas` — registrar entrada. Body: `{ "placa": "ABC123", "celda_id": 1 }`.
- `POST /api/salidas/<movimiento_id>` — registrar salida, liberar celda y crear pago pendiente.

### Novedades

- `GET /api/novedades` — listar novedades.
- `POST /api/novedades` — crear novedad. Body: `{ "movimiento_id": 1, "descripcion": "Rayón leve", "prioridad": "MEDIA" }`.

### Pagos

- `GET /api/pagos` — listar pagos.
- `GET /api/pagos?estado=PENDIENTE` — listar pagos pendientes.
- `POST /api/pagos` — confirmar pago. Body: `{ "movimiento_id": 1, "metodo": "TRANSFERENCIA" }`.

### Reportes

- `GET /api/reportes/resumen` — consultar totales de usuarios, vehículos, celdas, movimientos, novedades y pagos.

## Pruebas probadas en postman como ejemplo

1. Consultar `GET /api/usuarios` y obtener un `usuario_id`.
2. Crear un vehículo con `POST /api/vehiculos`.
3. Consultar o crear una celda con `GET /api/celdas` o `POST /api/celdas`.
4. Registrar entrada con `POST /api/entradas`.
5. Registrar una novedad con `POST /api/novedades`.
6. Registrar salida con `POST /api/salidas/<id>`.
7. Consultar el pago pendiente con `GET /api/pagos?estado=PENDIENTE`.
8. Confirmar el pago con `POST /api/pagos`.
9. Consultar `GET /api/reportes/resumen`.

