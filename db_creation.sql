CREATE DATABASE IF NOT EXISTS meteo;

USE meteo;

CREATE TABLE IF NOT EXISTS Type_alert (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Type_sky (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Users (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    email VARCHAR(255),
    password VARCHAR(255),
    city VARCHAR(100),
);

CREATE TABLE IF NOT EXISTS Alerts (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    description VARCHAR(255),
    active INT,
    date_alert DATE,
    FOREIGN KEY (fk_type) REFERENCES Type_alert(id)
    FOREIGN KEY (region) REFERENCES Regions(id)
);

CREATE TABLE IF NOT EXISTS Regions (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Departments (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100),
    FOREIGN KEY (region) REFERENCES Region(id)
);

CREATE TABLE IF NOT EXISTS Cities (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100),
    FOREIGN KEY (department) REFERENCES Departments(id)
);

CREATE TABLE IF NOT EXISTS Weather (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    date_weather DATE,
    temperature_min FLOAT,
    temperature_max FLOAT,
    pressure FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    sunrise TIME,
    sunset TIME,
    FOREIGN KEY (fk_type) REFERENCES Type_sky(id)
    FOREIGN KEY (city) REFERENCES Cities(id)
);

INSERT INTO Type_alert (label) VALUES 
('Tempête'),
('Inondation'),
('Canicule'),
('Neige/Verglas');

INSERT INTO Type_sky (label) VALUES
('Ciel ensoleillé'),
('Ciel dégagé'),
('Ciel nuageux'),
('Ciel orageux'),
('Ciel menaçant');

-- Entrées tests au sein des tables ;


INSERT INTO Regions VALUES
(1, 'Bretagne'),
(2, 'Alsace'),
(3, 'Île-de-France');

INSERT INTO Departments VALUES
(1, 'Ille-et-Vilaine', 1),
(2, "Côtes d'Armor", 1),
(3, 'Morbihan', 1),
(4, 'Finistère', 1);

INSERT INTO Cities VALUES
(1, 'Rennes', 1),
(2, 'Saint-Brieuc', 2),
(3, 'Saint-Malo', 1),
(4, 'Brest', 4),
(5, 'Lorient', 3),
(6, 'Vannes', 3),
(7, 'Quimper', 4);

INSERT INTO Alerts VALUES
(1, 'Gigantesque tempête de flammes dans le sas d'entrée d'un bâtiment de Bruz', 1, 19/03/2025, 3, 1),
(2, 'Vite fait du vent', 1, 19/03/2025, 1, 2);

INSERT INTO Weather VALUES
(1, 19/03/2025, 18, 21, 50, 42, 172, 06:30, 20:13, 4, 5),
(2, 19/03/2025, 31, 36, 25, 8, 21, 05:02, 23:56, 1, 1);

INSERT INTO Users VALUES
(1, 'frederic@gmail.com', 'jemappellecyril', 6),
(2, 'admin@admin.com', 'admin', 5),
(3, 'nasradmin@raison.fort', '0101', 1);