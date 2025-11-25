# Cambios en Bitácora - Registro por Día y Búsqueda por Semana

## 📝 Cambios Realizados

### Frontend (HTML)
1. **Formulario**: Cambié el campo de entrada de `type="week"` a `type="date"`
   - Ahora registra por **día específico** en lugar de semana

2. **Búsqueda**: Se mantiene `type="week"` 
   - Búsqueda por **semana ISO** (formato: 2025-W47)
   - Agregué botón "Limpiar" para ver todos los registros

3. **Tabla**: 
   - Cambié encabezado de "Semana" a "Fecha"
   - Ahora muestra la fecha específica del día

### Backend (Python)

1. **Base de Datos**:
   - Cambié `fechaSemana VARCHAR(20)` a `fecha DATE`
   - Los índices ahora están en `fecha` en lugar de `fechaSemana`

2. **Rutas Actualizadas**:
   - `/bitacora/all`: Ordena por `fecha DESC` en lugar de `fechaSemana DESC`
   - `/bitacora/agregar`: Recibe y guarda el campo `fecha` (tipo DATE)
   - `/bitacora/buscar`: 
     - Acepta formato ISO semana (2025-W47)
     - Calcula el rango de fechas de esa semana
     - Busca registros en ese rango

### AngularJS (app.js)
1. **Nueva función**: `limpiarBusqueda()`
   - Limpia el campo de búsqueda
   - Recarga todos los registros

## 🔄 Flujo de Funcionamiento

### Registrar
```
Usuario ingresa:
- Fecha: 24-11-2025 (día específico)
- Hora Inicio: 08:00
- Hora Fin: 12:00
- Otros datos...
→ Se guarda un registro para ese día
```

### Buscar
```
Usuario selecciona semana: 2025-W47 (Nov 17-23)
→ Sistema calcula: Nov 17 hasta Nov 23
→ Muestra todos los registros de esa semana
```

## 📊 Ejemplo de Base de Datos

```sql
-- Antes
fechaSemana VARCHAR(20)  -- "W47-2025"

-- Ahora
fecha DATE  -- "2025-11-24"
```

## ✅ Validaciones

- ✅ Fecha requerida (type="date")
- ✅ Búsqueda por semana ISO correcta
- ✅ Conversión automática de semana a rango de fechas
- ✅ Botón para limpiar búsqueda
- ✅ Mensajes de error si algo falla

## 🚀 Cómo Usar

1. **Crear Registro**: 
   - Selecciona una fecha específica
   - Completa los datos
   - Haz clic en "Guardar"

2. **Buscar Registros**:
   - Selecciona una semana (ej: 2025-W47)
   - Haz clic en "Buscar"
   - Se mostrarán todos los registros de esa semana

3. **Ver Todos**:
   - Haz clic en "Limpiar"
   - Se mostrarán todos los registros

## 📅 Formato de Semana ISO
- **Formato**: YYYY-Www (ej: 2025-W47)
- **Semana 1**: Contiene el 4 de enero
- **Lunes**: Inicio de semana
- **Domingo**: Fin de semana

## ⚠️ Importante

Si ya tienes datos en la tabla antigua con `fechaSemana`:

1. Crea una tabla nueva con el schema actualizado
2. Migra los datos si es necesario
3. O ejecuta una migración ALTER TABLE

```sql
ALTER TABLE bitacora 
CHANGE COLUMN fechaSemana fecha DATE NOT NULL;
```
