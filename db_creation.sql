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
    region VARCHAR(100),
    description VARCHAR(255),
    active INT,
    date_alert DATE,
    FOREIGN KEY (fk_type) REFERENCES Type_alert(id)
);

CREATE TABLE IF NOT EXISTS Region (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100)
)

CREATE TABLE IF NOT EXISTS Department (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100),
    FOREIGN KEY (region) REFERENCES Region(id)
)

CREATE TABLE IF NOT EXISTS Cities (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100),
    FOREIGN KEY (department) REFERENCES Department(id)
)

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
)

INSERT INTO Type_alert (label) VALUES 
('Tempête'),
('Inondation'),
('Canicule'),
('Neige/Verglas');