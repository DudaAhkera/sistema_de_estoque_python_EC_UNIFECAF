create database sistema_estoque;

use sistema_estoque;

create table usuarios (
	id int auto_increment primary key,
    username VARCHAR(50) not null unique,
    senha VARCHAR(50) not null,
    perfil ENUM('administrador', 'comum') not null
);

create table produtos (
	id int auto_increment primary key,
    nome VARCHAR(50) not null,
    quantidade int not null,
    quantidade_minima int not null
);

ALTER TABLE usuarios MODIFY COLUMN senha VARCHAR(64);

show tables;


