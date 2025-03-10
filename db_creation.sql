CREATE DATABASE IF NOT EXISTS meteo;

USE meteo;

CREATE TABLE IF NOT EXISTS Type_alert (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    label VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Users (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    email VARCHAR(255),
    password VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Alerts (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fk_type INT NOT NULL,
    region VARCHAR(100),
    description VARCHAR(255),
    active INT,
    date_alert DATE,
    FOREIGN KEY (fk_type) REFERENCES Type_alert(id)
);

INSERT INTO Type_alert (label) VALUES 
('Tempête'),
('Inondation'),
('Canicule'),
('Neige/Verglas');