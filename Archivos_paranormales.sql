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

-- INSERT CASO
INSERT INTO CASO (titulo, categoria, estado, fecha_incidente, id_investigador_lead, id_lugar) VALUES
('Robo en el Parque Central', 'Robo', 'Abierto', '2024-01-15', 1, 1),
('Incendio en Zona Industrial', 'Incendio', 'Cerrado', '2023-11-02', 5, 5),
('Desaparición en Bosque del Norte', 'Desaparición', 'En Proceso', '2024-02-20', 3, 2),
('Fraude Digital Masivo', 'Cibercrimen', 'Abierto', '2024-03-10', 2, 1),
('Homicidio en Puerto Azul', 'Homicidio', 'En Proceso', '2024-01-28', 1, 3);

-- INSERT CASO_INVESTIGADOR
INSERT INTO CASO_INVESTIGADOR (id_caso, id_investigador, rol, fecha_asignacion) VALUES
(1, 1, 'Líder', '2024-01-15'),
(1, 4, 'Apoyo', '2024-01-16'),
(2, 5, 'Líder', '2023-11-02'),
(3, 3, 'Líder', '2024-02-20'),
(3, 1, 'Apoyo', '2024-02-21'),
(4, 2, 'Líder', '2024-03-10'),
(4, 1, 'Apoyo', '2024-03-11'),
(5, 1, 'Líder', '2024-01-28'),
(5, 3, 'Forense', '2024-01-29');

-- INSERT EVIDENCIA
INSERT INTO EVIDENCIA (id_caso, tipo, descripcion, nivel_credibilidad, fecha_recoleccion) VALUES
(1, 'Huella', 'Huella dactilar encontrada en un banco del parque', 'Alta', '2024-01-16'),
(1, 'Video', 'Grabación de cámara de seguridad', 'Media', '2024-01-16'),
(2, 'Residuo', 'Restos de acelerante en el suelo', 'Alta', '2023-11-03'),
(3, 'Objeto Personal', 'Mochila encontrada cerca del sendero', 'Alta', '2024-02-21'),
(3, 'Ropa', 'Chaqueta rasgada con manchas', 'Media', '2024-02-22'),
(4, 'Registro Digital', 'IP vinculada al ataque', 'Alta', '2024-03-11'),
(5, 'Arma Blanca', 'Cuchillo con huellas parciales', 'Alta', '2024-01-29'),
(5, 'Sangre', 'Muestra de sangre en el muelle', 'Alta', '2024-01-29');

-- INSERT TESTIGO
INSERT INTO TESTIGO (id_caso, nombre, contacto, declaracion, fiabilidad) VALUES
(1, 'Javier López', 'javier@mail.com', 'Vio a un hombre correr tras escuchar un grito.', 7),
(1, 'María Santos', 'maria@mail.com', 'Escuchó ruidos extraños cerca del parque.', 5),
(2, 'Pedro Gómez', 'pedro@mail.com', 'Vio humo antes de que iniciara el incendio.', 8),
(3, 'Lucía Herrera', 'lucia@mail.com', 'Vio a la persona desaparecida caminando sola.', 6),
(4, 'Andrés Molina', 'andres@mail.com', 'Recibió un correo sospechoso antes del ataque.', 9),
(5, 'Elena Rivas', 'elena@mail.com', 'Escuchó una discusión fuerte en el muelle.', 7);

-- INSERT INFORME
INSERT INTO INFORME (id_caso, id_investigador, contenido, conclusion, fecha_emision) VALUES
(1, 1, 'Se revisaron cámaras y se recolectaron huellas.', 'Se requiere análisis adicional.', '2024-01-20'),
(2, 5, 'El incendio fue provocado con acelerante.', 'Caso cerrado por falta de sospechosos.', '2023-11-10'),
(3, 3, 'Se hallaron objetos personales cerca del sendero.', 'Posible secuestro.', '2024-02-25'),
(4, 2, 'Ataque digital coordinado desde múltiples IP.', 'Investigación continúa.', '2024-03-12'),
(5, 1, 'Se encontró arma blanca con huellas parciales.', 'Se sospecha de un conflicto previo.', '2024-01-30');
