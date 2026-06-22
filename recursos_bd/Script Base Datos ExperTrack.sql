-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS expertrack;
USE expertrack;

-- 1. Tabla: Usuario
CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    rol ENUM('Usuario Solicitante', 'Técnico', 'Administrador') NOT NULL,
    estatus BOOLEAN DEFAULT TRUE,
    telefono VARCHAR(15),
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- 2. Tabla: Equipo
CREATE TABLE Equipo (
    id_equipo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_equipo VARCHAR(30) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    numero_serie VARCHAR(100) UNIQUE,
    codigo_inventario VARCHAR(100) UNIQUE,
    estado_operativo ENUM('Operativo', 'Baja', 'En Mantenimiento') DEFAULT 'Operativo',
    area VARCHAR(50),
    ubicacion VARCHAR(100),
    fecha_adquisicion DATE,
    en_garantia BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_equipo_usuario FOREIGN KEY (id_usuario) 
        REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- 3. Tabla: Periferico
CREATE TABLE Periferico (
    id_periferico INT AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT NOT NULL,
    tipo VARCHAR(30),
    marca VARCHAR(50),
    numero_serie VARCHAR(100),
    id_inventario_interno VARCHAR(100),
    CONSTRAINT fk_periferico_equipo FOREIGN KEY (id_equipo) 
        REFERENCES Equipo(id_equipo) ON DELETE CASCADE
);

-- 4. Tabla: Especificacion
CREATE TABLE Especificacion (
    id_especificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT NOT NULL,
    sistema_operativo VARCHAR(50),
    procesador VARCHAR(100),
    ram VARCHAR(50),    
    tipo_ram VARCHAR(50),
    almacenamiento VARCHAR(100),
    almacenamiento_tipo VARCHAR(50),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    es_actual BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_especificacion_equipo FOREIGN KEY (id_equipo) 
        REFERENCES Equipo(id_equipo) ON DELETE CASCADE
);

-- 5. Tabla: Evento (Superentidad)
CREATE TABLE Evento (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT NOT NULL,
    id_usuario INT NOT NULL, -- Técnico asignado
    falla_reportada TEXT,    
    estado_fisico TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    validado BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_evento_equipo FOREIGN KEY (id_equipo) 
        REFERENCES Equipo(id_equipo),
    CONSTRAINT fk_evento_tecnico FOREIGN KEY (id_usuario) 
        REFERENCES Usuario(id_usuario)
);

-- 6. Tabla: Diagnostico (Hija - Especialización)
CREATE TABLE Diagnostico (
    id_evento INT PRIMARY KEY,
    fecha_diagnostico DATETIME,
    log_chatbot JSON,
    resultado_preeliminar TEXT,
    validacion_tecnico TEXT,
    CONSTRAINT fk_diagnostico_evento FOREIGN KEY (id_evento) 
        REFERENCES Evento(id_evento) ON DELETE CASCADE
);

-- 7. Tabla: Mantenimiento (Hija - Especialización)
CREATE TABLE Mantenimiento (
    id_evento INT PRIMARY KEY,
    tipo ENUM('Preventivo', 'Correctivo') NOT NULL,
    fecha_entrega DATETIME,
    descripcion_trabajo TEXT,
    piezas_reemplazadas TEXT,
    CONSTRAINT fk_mantenimiento_evento FOREIGN KEY (id_evento) 
        REFERENCES Evento(id_evento) ON DELETE CASCADE
);

-- 8. Tabla: Alerta
CREATE TABLE Alerta (
    id_alerta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL, -- Cliente a notificar
    id_equipo INT NOT NULL,
    estatus ENUM('Pendiente', 'Enviada') DEFAULT 'Pendiente',
    titulo VARCHAR(100),
    descripcion TEXT,
    fecha_programada DATE,
    CONSTRAINT fk_alerta_usuario FOREIGN KEY (id_usuario) 
        REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_alerta_equipo FOREIGN KEY (id_equipo) 
        REFERENCES Equipo(id_equipo) ON DELETE CASCADE
);

