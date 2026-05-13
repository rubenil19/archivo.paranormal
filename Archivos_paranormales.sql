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

-- TABLA EVIDENCIA
CREATE TABLE EVIDENCIA (
    id_evidencia INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    tipo VARCHAR(100),
    descripcion TEXT,
    nivel_credibilidad VARCHAR(50),
    fecha_recoleccion DATE,
    FOREIGN KEY (id_caso) REFERENCES CASO(id_caso)
);

-- TABLA TESTIGO
CREATE TABLE TESTIGO (
    id_testigo INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    nombre VARCHAR(100),
    contacto VARCHAR(100),
    declaracion TEXT,
    fiabilidad INT,
    FOREIGN KEY (id_caso) REFERENCES CASO(id_caso)
);

-- TABLA INFORME
CREATE TABLE INFORME (
    id_informe INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    id_investigador INT NOT NULL,
    contenido TEXT,
    conclusion TEXT,
    fecha_emision DATE,
    FOREIGN KEY (id_caso) REFERENCES CASO(id_caso),
    FOREIGN KEY (id_investigador) REFERENCES INVESTIGADOR(id_investigador)
);

-- INSERT INVESTIGADOR
INSERT INTO INVESTIGADOR (nombre, especialidad, nivel_acceso, fecha_ingreso) VALUES
('Laura Méndez', 'Criminalística', 'Alto', '2018-03-12'),
('Carlos Ruiz', 'Cibercrimen', 'Medio', '2020-07-01'),
('Ana Torres', 'Forense', 'Alto', '2017-11-23'),
('Miguel Salas', 'Perfilación', 'Bajo', '2021-02-14'),
('Sofía Delgado', 'Balística', 'Medio', '2019-09-05');

-- INSERT LUGAR
INSERT INTO LUGAR (nombre, pais, region, latitud, longitud, tipo_zona) VALUES
('Parque Central', 'España', 'Madrid', 40.4168, -3.7038, 'Urbana'),
('Bosque del Norte', 'España', 'Navarra', 42.8125, -1.6458, 'Rural'),
('Puerto Azul', 'España', 'Valencia', 39.4699, -0.3763, 'Costera'),
('Cerro del Águila', 'España', 'Granada', 37.1773, -3.5986, 'Montañosa'),
('Zona Industrial 7', 'España', 'Bilbao', 43.2630, -2.9350, 'Industrial');
