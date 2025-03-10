CREATE DATABASE meteo ;


CREATE TABLE Users
	(
	id INT PRIMAREY KEY NOT NULL AUTO-INCREMENT,
	email VARCHAR(255),
	password VARCHAR(255),
	city VARCHAR(100),
	region VARCHAR(100)
	)
;

CREATE TABLE Alerts
	(
	id INT PRIMAREY KEY NOT NULL AUTO-INCREMENT,
	FOREIGN KEY (fk_type) REFERENCES Type_alert(id),
	region VARCHAR(100),
	description VARCHAR(255),
	active INT,
	date_alert DATE
	)
;

CREATE TABLE Type_alert
	(
	id INT PRIMAREY KEY NOT NULL AUTO-INCREMENT,
	label VARCHAR(100)
	)
;