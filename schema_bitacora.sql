-- Script para crear la tabla bitacora en VidaDial
-- Ejecuta este script en tu base de datos si la tabla aún no existe

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

-- Ejemplo de índices para mejorar búsquedas
ALTER TABLE bitacora ADD INDEX idx_fechaSemana (fechaSemana);
ALTER TABLE bitacora ADD INDEX idx_horaInicio (horaInicio);
