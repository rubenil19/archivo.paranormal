-- TABLA INVESTIGADOR
DROP DATABASE IF EXISTS Archivos_Paranormales;
CREATE DATABASE Archivos_Paranormales;
USE Archivos_Paranormales;

-- TABLA INVESTIGADOR
CREATE TABLE INVESTIGADOR (
    id_investigador INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    nivel_acceso VARCHAR(50),
    fecha_ingreso DATE
);

-- TABLA LUGAR
CREATE TABLE LUGAR (
    id_lugar INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(100),
    region VARCHAR(100),
    latitud DECIMAL(10,6),
    longitud DECIMAL(10,6),
    tipo_zona VARCHAR(50)
);

-- TABLA CASO
CREATE TABLE CASO (
    id_caso INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    estado VARCHAR(50),
    fecha_incidente DATE,
    id_investigador_lead INT,
    id_lugar INT,
    FOREIGN KEY (id_investigador_lead) REFERENCES INVESTIGADOR(id_investigador),
    FOREIGN KEY (id_lugar) REFERENCES LUGAR(id_lugar)
);

-- TABLA CASO_INVESTIGADOR
CREATE TABLE CASO_INVESTIGADOR (
    id_caso INT,
    id_investigador INT,
    rol VARCHAR(100),
    fecha_asignacion DATE,
    PRIMARY KEY (id_caso, id_investigador),
    FOREIGN KEY (id_caso) REFERENCES CASO(id_caso),
    FOREIGN KEY (id_investigador) REFERENCES INVESTIGADOR(id_investigador)
);