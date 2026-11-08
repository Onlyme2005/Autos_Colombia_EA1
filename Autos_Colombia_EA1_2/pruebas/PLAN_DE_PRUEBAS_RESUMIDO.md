# Plan de pruebas resumido — EA2

## Alcance

Se validan los requerimientos de gestión de usuarios, vehículos y celdas de la Iteración 2, además de su integración con el registro de entradas de la Iteración 1. Las pruebas se ejecutan sobre Flask, SQLite y la colección de Postman incluida.

## Ambiente

El ambiente de demostración utiliza Python 3.10 o superior, Flask, SQLite, Postman y el servidor local `http://127.0.0.1:5000`. La base de datos de prueba se crea con `init_db()`.

## Casos de prueba

### CP-01 — Crear usuario válido

**Requerimiento:** RF-09 / HU-06. **Precondición:** API activa. **Entrada:** `POST /api/usuarios` con nombre, documento y teléfono nuevos. **Resultado esperado:** HTTP 201, usuario creado en estado ACTIVO y respuesta con identificador. **Resultado obtenido:** Aprobado.

### CP-02 — Rechazar documento duplicado

**Requerimiento:** RF-09 / RNF-10. **Precondición:** existe un usuario con el documento enviado. **Entrada:** crear otro usuario con el mismo documento. **Resultado esperado:** HTTP 409 y mensaje de documento ya registrado. **Resultado obtenido:** Aprobado.

### CP-03 — Consultar y buscar usuarios

**Requerimiento:** RF-10 / HU-06. **Precondición:** existen usuarios. **Entrada:** `GET /api/usuarios?buscar=Ana`. **Resultado esperado:** HTTP 200 y listado filtrado por nombre o documento. **Resultado obtenido:** Aprobado.

### CP-04 — Actualizar usuario

**Requerimiento:** RF-11 / HU-06. **Precondición:** existe un usuario. **Entrada:** `PUT /api/usuarios/{id}` con datos válidos. **Resultado esperado:** HTTP 200 y datos actualizados sin eliminar historial. **Resultado obtenido:** Aprobado.

### CP-05 — Crear vehículo para usuario activo

**Requerimiento:** RF-13 / HU-07. **Precondición:** existe un usuario ACTIVO. **Entrada:** `POST /api/vehiculos` con placa, tipo, marca, color y usuario_id. **Resultado esperado:** HTTP 201 y vehículo relacionado. **Resultado obtenido:** Aprobado.

### CP-06 — Rechazar placa duplicada

**Requerimiento:** RF-13 / RNF-10. **Precondición:** existe la placa enviada. **Entrada:** crear vehículo con la misma placa. **Resultado esperado:** HTTP 409. **Resultado obtenido:** Aprobado.

### CP-07 — Consultar vehículos por placa

**Requerimiento:** RF-14 / HU-07. **Precondición:** existe un vehículo. **Entrada:** `GET /api/vehiculos?placa=ABC`. **Resultado esperado:** HTTP 200 y vehículo coincidente con nombre del usuario. **Resultado obtenido:** Aprobado.

### CP-08 — Crear celda válida

**Requerimiento:** RF-16 / HU-09. **Precondición:** código no existente. **Entrada:** `POST /api/celdas` con código y zona. **Resultado esperado:** HTTP 201, estado LIBRE y nuevo identificador. **Resultado obtenido:** Aprobado.

### CP-09 — Rechazar código de celda duplicado

**Requerimiento:** RF-16 / RNF-10. **Precondición:** existe el código. **Entrada:** crear una celda con el mismo código. **Resultado esperado:** HTTP 409. **Resultado obtenido:** Aprobado.

### CP-10 — Filtrar celdas libres

**Requerimiento:** RF-17 / HU-08. **Precondición:** existen celdas con diferentes estados. **Entrada:** `GET /api/celdas?estado=LIBRE`. **Resultado esperado:** HTTP 200 y solo celdas LIBRE. **Resultado obtenido:** Aprobado.

### CP-11 — Impedir inhabilitar celda ocupada

**Requerimiento:** RF-18/RF-19 / HU-09. **Precondición:** celda con movimiento ACTIVO. **Entrada:** `PUT /api/celdas/{id}` con estado INHABILITADA. **Resultado esperado:** HTTP 409 y la celda permanece OCUPADA. **Resultado obtenido:** Aprobado.

### CP-12 — Integración con entrada

**Requerimiento:** RF-20 / HU-10. **Precondición:** vehículo asociado a usuario ACTIVO y celda LIBRE. **Entrada:** `POST /api/entradas`. **Resultado esperado:** HTTP 201, movimiento ACTIVO y celda OCUPADA. **Resultado obtenido:** Aprobado.

### CP-13 — Rechazar entrada de usuario inactivo

**Requerimiento:** RF-12/RF-20. **Precondición:** usuario INACTIVO con vehículo registrado. **Entrada:** registrar entrada con su placa. **Resultado esperado:** HTTP 404 y no se crea movimiento. **Resultado obtenido:** Aprobado.

## Criterios de salida

La iteración se considera aprobada cuando todos los casos críticos CP-01, CP-02, CP-05, CP-06, CP-08, CP-10, CP-11 y CP-12 estén aprobados, no existan duplicidades de documentos, placas o códigos, y el flujo entrada-salida conserve la integridad de celdas y movimientos.


