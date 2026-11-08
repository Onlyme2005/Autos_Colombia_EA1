# Autos Colombia — API Iteraciones 1 y 2

API REST para gestionar la operación y administración de un parqueadero. Está desarrollada con **Python, Flask y SQLite**.

## Requisitos

- Python 3.10 o superior.
- Postman, opcional, para realizar las pruebas.

## Ejecutar localmente

1. Abre una terminal en la carpeta del proyecto.
2. Crea el entorno virtual:

   ```bash
   python -m venv .venv
   ```

3. Activa el entorno virtual.

   Windows:

   ```bash
   .venv\\Scripts\\activate
   ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Inicia la API:

   ```bash
   python app.py
   ```

6. Verifica que esté funcionando:

   ```text
   http://127.0.0.1:5000/api/health
   ```

Para apagarla, presiona `Ctrl + C` en la terminal.

La aplicación crea automáticamente la base de datos SQLite `autos_colombia.db`.

## Endpoints principales

### Usuarios y vehículos

- `GET /api/usuarios` — listar usuarios.
- `POST /api/usuarios` — crear usuario.
- `GET /api/vehiculos` — listar vehículos.
- `POST /api/vehiculos` — crear vehículo.

Ejemplo de usuario:

```json
{
  "nombre": "Carlos Pérez",
  "documento": "100000002",
  "telefono": "3111111111"
}
```

Ejemplo de vehículo:

```json
{
  "placa": "XYZ789",
  "tipo": "AUTOMOVIL",
  "marca": "Renault",
  "color": "Blanco",
  "usuario_id": 1
}
```

### Celdas

- `GET /api/celdas` — listar celdas.
- `GET /api/celdas?estado=LIBRE` — consultar celdas libres.
- `POST /api/celdas` — crear celda.
- `PUT /api/celdas/<id>` — actualizar celda.

Ejemplo:

```json
{
  "codigo": "B-01",
  "zona": "Sur"
}
```

### Entradas y salidas

- `GET /api/movimientos/activos` — consultar vehículos dentro.
- `POST /api/entradas` — registrar entrada.
- `POST /api/salidas/<movimiento_id>` — registrar salida y generar pago pendiente.

Ejemplo de entrada:

```json
{
  "placa": "ABC123",
  "celda_id": 1
}
```

### Novedades y pagos

- `GET /api/novedades` — listar novedades.
- `POST /api/novedades` — registrar novedad.
- `GET /api/pagos` — listar pagos.
- `GET /api/pagos?estado=PENDIENTE` — consultar pagos pendientes.
- `POST /api/pagos` — confirmar pago.

Ejemplo de novedad:

```json
{
  "movimiento_id": 1,
  "descripcion": "Rayón leve",
  "prioridad": "MEDIA"
}
```

Ejemplo de pago:

```json
{
  "movimiento_id": 1,
  "metodo": "TRANSFERENCIA"
}
```

### Reportes

- `GET /api/reportes/resumen` — consultar el resumen de usuarios, vehículos, celdas, movimientos, novedades y pagos.

## Flujo básico de pruebas

1. `GET /api/health`.
2. Consultar usuarios y obtener un `usuario_id`.
3. Crear o consultar un vehículo.
4. Consultar una celda libre.
5. Registrar una entrada.
6. Consultar movimientos activos.
7. Registrar una novedad.
8. Registrar la salida usando el `movimiento_id`.
9. Consultar el pago pendiente.
10. Confirmar el pago.
11. Consultar el reporte general.

Para las solicitudes `POST` y `PUT`, usar en Postman:

```text
Body → raw → JSON
```

y el encabezado:

```text
Content-Type: application/json
```

## Reiniciar la base de datos

1. Detén la API con `Ctrl + C`.
2. Elimina `autos_colombia.db`.
3. Ejecuta nuevamente:

   ```bash
   python app.py
   ```
