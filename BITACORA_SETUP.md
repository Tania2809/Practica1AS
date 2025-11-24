# Configuración de la Bitácora - VidaDial

## Pasos para activar la funcionalidad de Bitácora

### 1. Crear la tabla en la base de datos

Ejecuta el siguiente script SQL en tu base de datos:

```sql
CREATE TABLE IF NOT EXISTS bitacora (
    idBitacora INT AUTO_INCREMENT PRIMARY KEY,
    fechaSemana VARCHAR(20) NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    drenajeInicial DECIMAL(10, 2),
    ufTotal DECIMAL(10, 2),
    tiempoMedioPerm DECIMAL(10, 2),
    liquidoIngerido DECIMAL(10, 2),
    cantidadOrina DECIMAL(10, 2),
    glucosa DECIMAL(10, 2),
    presionArterial VARCHAR(20),
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fechaActualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices opcionales para mejorar búsquedas
ALTER TABLE bitacora ADD INDEX idx_fechaSemana (fechaSemana);
ALTER TABLE bitacora ADD INDEX idx_horaInicio (horaInicio);
```

### 2. Archivos creados/modificados

- **`templates/bitacora.html`**: Formulario principal con 3 secciones
  - Fecha y Horario
  - Registro de Sesión
  - Mediciones y Registros Clínicos

- **`templates/tablaBitacora.html`**: Tabla para mostrar registros

- **`static/js/app.js`**: 
  - Agregado controlador `bitacoraCtrl`
  - Funciones: guardarBitacora, buscar, editar, eliminar
  - Corregida ruta del controlador en $routeProvider

- **`app.py`**: 
  - Rutas: `/bitacora`, `/bitacora/all`, `/bitacora/agregar`, `/bitacora/buscar`, `/bitacora/editar/<id>`, `/bitacora/eliminar`
  - Función `triggerUpdateBitacora()` para actualizaciones en tiempo real con Pusher

- **`templates/index.html`**: Agregado enlace a Bitácora en el menú

### 3. Funcionalidades disponibles

✅ **Crear registros**: Completa el formulario con las 3 secciones y haz clic en "Registrar"

✅ **Buscar registros**: Utiliza el campo de búsqueda por semana para filtrar

✅ **Editar registros**: Haz clic en el botón "✏️" para editar un registro

✅ **Eliminar registros**: Haz clic en el botón "🗑️" con confirmación de seguridad

### 4. Campos del formulario

**Fecha y Horario:**
- Fecha por Semana (selector de semana)
- Hora Inicio (hora)
- Hora Fin (hora)

**Registro de Sesión:**
- Drenaje Inicial (mL)
- UF Total (mL)
- T. Medio Perm. (minutos)

**Mediciones y Registros Clínicos:**
- Cantidad de Líquido Ingerido en 24 hrs (mL)
- Cantidad de Orina 24 hrs (mL)
- Medición de Glucosa (mg/dL)
- Presión Arterial (mmHg)

### 5. Notas importantes

- La tabla se mostrará automáticamente al cargar la página de Bitácora
- Los cambios se sincronizarán en tiempo real mediante Pusher
- Todos los campos son requeridos en el formulario
- Los valores numéricos aceptan decimales con 2 posiciones
- La presión arterial puede ingresarse en formato libre (ej: 120/80)

## Estructura de la base de datos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| idBitacora | INT PRIMARY KEY | ID único |
| fechaSemana | VARCHAR(20) | Fecha por semana (W3-2025, etc.) |
| horaInicio | TIME | Hora de inicio |
| horaFin | TIME | Hora de finalización |
| drenajeInicial | DECIMAL(10,2) | Drenaje inicial en mL |
| ufTotal | DECIMAL(10,2) | UF Total en mL |
| tiempoMedioPerm | DECIMAL(10,2) | Tiempo medio de permanencia en minutos |
| liquidoIngerido | DECIMAL(10,2) | Líquido ingerido en 24hrs (mL) |
| cantidadOrina | DECIMAL(10,2) | Cantidad de orina en 24hrs (mL) |
| glucosa | DECIMAL(10,2) | Medición de glucosa (mg/dL) |
| presionArterial | VARCHAR(20) | Presión arterial (formato libre) |
| fechaCreacion | TIMESTAMP | Fecha de creación |
| fechaActualizacion | TIMESTAMP | Fecha de última actualización |
