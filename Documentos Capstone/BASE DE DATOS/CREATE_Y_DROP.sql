DROP TABLE casa CASCADE CONSTRAINTS;
DROP TABLE cliente CASCADE CONSTRAINTS;
DROP TABLE constructora CASCADE CONSTRAINTS;
DROP TABLE departamento CASCADE CONSTRAINTS;
DROP TABLE estado_inmueble CASCADE CONSTRAINTS;
DROP TABLE ficha_inmueble CASCADE CONSTRAINTS;
DROP TABLE privilegio CASCADE CONSTRAINTS;
DROP TABLE proyecto CASCADE CONSTRAINTS;
DROP TABLE registro_posventa CASCADE CONSTRAINTS;
DROP TABLE reporte CASCADE CONSTRAINTS;
DROP TABLE trabajador CASCADE CONSTRAINTS;

CREATE TABLE casa (
    idcasa        NUMBER NOT NULL,
    modelocasa    VARCHAR2(1000 BYTE) NOT NULL,
    cantcuarto    NUMBER(10) NOT NULL,
    cantbanno     NUMBER(5) NOT NULL,
    livicomecoci  VARCHAR2(1000 BYTE) NOT NULL,
    piso          VARCHAR2(100 BYTE) NOT NULL,
    plano         BLOB NOT NULL
);

CREATE TABLE cliente (
    idcliente                     NUMBER NOT NULL,
    rutcliente                    VARCHAR2(10 BYTE) NOT NULL,
    nombrecli                     VARCHAR2(100 BYTE) NOT NULL,
    apellidocli                   VARCHAR2(100 BYTE) NOT NULL,
    telefono                      NUMBER(9) NOT NULL,
    correo                        VARCHAR2(100 BYTE) NOT NULL,
    contrasenna                   VARCHAR2(1000 BYTE) NOT NULL,
    registro_posventa_idregistro  NUMBER NOT NULL
);

CREATE TABLE constructora (
    idconstructora    NUMBER NOT NULL,
    rut_constructora  VARCHAR2(10 BYTE) NOT NULL,
    nomconstuct       VARCHAR2(1000 BYTE) NOT NULL,
    direccion         VARCHAR2(1000 BYTE) NOT NULL,
    correo            VARCHAR2(100 BYTE) NOT NULL
);

CREATE TABLE departamento (
    iddepartamento      NUMBER NOT NULL,
    modelodepartamento  VARCHAR2(1000 BYTE) NOT NULL,
    cantcuarto          NUMBER(10) NOT NULL,
    cantbanno           NUMBER(5) NOT NULL,
    livicomecoci        VARCHAR2(1000 BYTE) NOT NULL,
    piso                VARCHAR2(100 BYTE) NOT NULL,
    plano               BLOB NOT NULL
);

CREATE TABLE estado_inmueble (
    idestado                   NUMBER NOT NULL,
    folioinmueble              NUMBER NOT NULL,
    estado                     VARCHAR2(4000 BYTE) NOT NULL,
    observacion                VARCHAR2(4000 BYTE) NOT NULL,
    ficha_inmueble_idinmueble  NUMBER NOT NULL
);

CREATE TABLE ficha_inmueble (
    idinmueble                   NUMBER NOT NULL,
    tipoinmueble                 VARCHAR2(100 BYTE) NOT NULL,
    proyecto_idproyecto          NUMBER NOT NULL,
    casa_idcasa                  NUMBER NOT NULL,
    departamento_iddepartamento  NUMBER NOT NULL
);

CREATE TABLE privilegio (
    id_privilegio   NUMBER NOT NULL,
    tipoprivilegio  VARCHAR2(100 BYTE) NOT NULL
);

CREATE TABLE proyecto (
    idproyecto                   NUMBER NOT NULL,
    codigoproyecto               VARCHAR2(1000 BYTE) NOT NULL,
    nomproyecto                  VARCHAR2(1000 BYTE) NOT NULL,
    ubicacion                    VARCHAR2(1000 BYTE) NOT NULL,
    fechainicio                  DATE NOT NULL,
    fechaestimtermi              DATE NOT NULL,
    constructora_idconstructora  NUMBER NOT NULL
);

CREATE TABLE registro_posventa (
    idregistro           NUMBER NOT NULL,
    tipocatastro         VARCHAR2(4000 BYTE) NOT NULL,
    observacion          VARCHAR2(4000 BYTE) NOT NULL,
    imagen               BLOB NOT NULL,
    proyecto_idproyecto  NUMBER NOT NULL
);

CREATE TABLE reporte (
    idreporte            NUMBER NOT NULL,
    reporteestado        VARCHAR2(4000 BYTE) NOT NULL,
    reporteproyecto      VARCHAR2(4000 BYTE) NOT NULL,
    proyecto_idproyecto  NUMBER NOT NULL
);

CREATE TABLE trabajador (
    idtrabajador              NUMBER NOT NULL,
    ruttrabajador             VARCHAR2(10 BYTE) NOT NULL,
    nombretrab                VARCHAR2(100 BYTE) NOT NULL,
    apellidotrab              VARCHAR2(100 BYTE) NOT NULL,
    telefono                  NUMBER(9) NOT NULL,
    area                      VARCHAR2(100 BYTE) NOT NULL,
    cargo                     VARCHAR2(100 BYTE) NOT NULL,
    correo                    VARCHAR2(100 BYTE) NOT NULL,
    contrasenna               VARCHAR2(1000 BYTE) NOT NULL,
    privilegio_id_privilegio  NUMBER NOT NULL,
    proyecto_idproyecto       NUMBER NOT NULL
);
