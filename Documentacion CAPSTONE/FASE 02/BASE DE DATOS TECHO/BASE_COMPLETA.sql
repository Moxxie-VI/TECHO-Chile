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

DROP SEQUENCE seq_proyecto;
DROP SEQUENCE seq_trabajador;
DROP SEQUENCE seq_cliente;
DROP SEQUENCE seq_ficha_inmueble;
DROP SEQUENCE seq_estado_inmueble;
DROP SEQUENCE seq_registro_posventa;
DROP SEQUENCE seq_reporte;
DROP SEQUENCE seq_casa;
DROP SEQUENCE seq_departamento;
DROP SEQUENCE seq_constructora;
DROP SEQUENCE seq_privilegio;


DROP PACKAGE pkg_proyecto;
DROP PACKAGE pkg_postventa;
DROP PACKAGE pkg_inmueble;

DROP PROCEDURE crear_proyecto;
DROP PROCEDURE asignar_trabajador_a_proyecto;
DROP PROCEDURE registrar_postventa;
DROP PROCEDURE actualizar_estado_inmueble;

DROP FUNCTION fn_nombre_trabajador;
DROP FUNCTION fn_dias_reclamo;
DROP FUNCTION fn_porcentaje_avance_proyecto;

DROP TYPE varray_contactos_proyecto;
DROP TYPE t_contacto_proyecto;



CREATE SEQUENCE seq_proyecto START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_trabajador START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_cliente START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_ficha_inmueble START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_estado_inmueble START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_registro_posventa START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_reporte START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_casa START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_departamento START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_constructora START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_privilegio START WITH 1 INCREMENT BY 1 NOCACHE;

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


ALTER TABLE casa ADD CONSTRAINT casa_pk PRIMARY KEY ( idcasa );

ALTER TABLE cliente ADD CONSTRAINT cliente_pkv1 PRIMARY KEY ( idcliente );

ALTER TABLE cliente ADD CONSTRAINT cliente_rutcliente_correo_un UNIQUE ( rutcliente,correo );

ALTER TABLE constructora ADD CONSTRAINT constructora_pk PRIMARY KEY ( idconstructora );

ALTER TABLE constructora ADD CONSTRAINT constructora_rut_un UNIQUE ( rut_constructora );

ALTER TABLE departamento ADD CONSTRAINT departamento_pk PRIMARY KEY ( iddepartamento );

ALTER TABLE estado_inmueble ADD CONSTRAINT estado_inmueble_pk PRIMARY KEY ( idestado );

ALTER TABLE ficha_inmueble ADD CONSTRAINT ficha_inmueble_pk PRIMARY KEY ( idinmueble );

ALTER TABLE privilegio ADD CONSTRAINT privilegio_pk PRIMARY KEY ( id_privilegio );

ALTER TABLE proyecto ADD CONSTRAINT proyecto_pk PRIMARY KEY ( idproyecto );

ALTER TABLE registro_posventa ADD CONSTRAINT registro_posventa_pk PRIMARY KEY ( idregistro );

ALTER TABLE trabajador ADD CONSTRAINT trabajador_pk PRIMARY KEY ( idtrabajador );

ALTER TABLE trabajador ADD CONSTRAINT trabajador_ruttrabajador_correo_un UNIQUE ( ruttrabajador,correo );


ALTER TABLE cliente
    ADD CONSTRAINT cliente_reg_posventa_fk FOREIGN KEY ( registro_posventa_idregistro )
        REFERENCES registro_posventa ( idregistro );


ALTER TABLE estado_inmueble
    ADD CONSTRAINT estado_inmueble_ficha_fk FOREIGN KEY ( ficha_inmueble_idinmueble )
        REFERENCES ficha_inmueble ( idinmueble );

ALTER TABLE ficha_inmueble
    ADD CONSTRAINT ficha_inmueble_casa_fk FOREIGN KEY ( casa_idcasa )
        REFERENCES casa ( idcasa );

ALTER TABLE ficha_inmueble
    ADD CONSTRAINT ficha_inmueble_departamento_fk FOREIGN KEY ( departamento_iddepartamento )
        REFERENCES departamento ( iddepartamento );

ALTER TABLE ficha_inmueble
    ADD CONSTRAINT ficha_inmueble_proyecto_fk FOREIGN KEY ( proyecto_idproyecto )
        REFERENCES proyecto ( idproyecto );

ALTER TABLE proyecto
    ADD CONSTRAINT proyecto_constructora_fk FOREIGN KEY ( constructora_idconstructora )
        REFERENCES constructora ( idconstructora );

ALTER TABLE registro_posventa
    ADD CONSTRAINT registro_posventa_proyecto_fk FOREIGN KEY ( proyecto_idproyecto )
        REFERENCES proyecto ( idproyecto );

ALTER TABLE reporte
    ADD CONSTRAINT reporte_proyecto_fk FOREIGN KEY ( proyecto_idproyecto )
        REFERENCES proyecto ( idproyecto );

ALTER TABLE trabajador
    ADD CONSTRAINT trabajador_privilegio_fk FOREIGN KEY ( privilegio_id_privilegio )
        REFERENCES privilegio ( id_privilegio );

ALTER TABLE trabajador
    ADD CONSTRAINT trabajador_proyecto_fk FOREIGN KEY ( proyecto_idproyecto )
        REFERENCES proyecto ( idproyecto );



-- 1 CONSTRUCTORA
INSERT INTO constructora (idconstructora, rut_constructora, nomconstuct, direccion, correo)
    VALUES (1, '76123456-7', 'Constructora Andes', 'Av. Las Torres 1234, Santiago', 'contacto@andes.cl');

INSERT INTO constructora (idconstructora, rut_constructora, nomconstuct, direccion, correo)
    VALUES (2, '77987654-3', 'Constructora Pacifico', 'Calle del Mar 456, Vinia del Mar', 'info@pacifico.cl');

-- 2 PROYECTO
INSERT INTO proyecto (idproyecto, codigoproyecto, nomproyecto, ubicacion, fechainicio, fechaestimtermi, constructora_idconstructora)
    VALUES (1, 'PRJ-AND-001', 'Altos de la Cordillera', 'La Florida, Santiago',
        TO_DATE('2024-01-15', 'YYYY-MM-DD'), TO_DATE('2025-12-30', 'YYYY-MM-DD'), 1);

INSERT INTO proyecto (idproyecto, codigoproyecto, nomproyecto, ubicacion, fechainicio, fechaestimtermi, constructora_idconstructora)
    VALUES (2, 'PRJ-PAC-002', 'Mar Azul', 'Reniaca, Vinia del Mar',
        TO_DATE('2023-06-01', 'YYYY-MM-DD'), TO_DATE('2025-03-15', 'YYYY-MM-DD'), 2);

-- 3 PRIVILEGIO
INSERT INTO privilegio (id_privilegio, tipoprivilegio)
    VALUES (1, 'Administrador');

INSERT INTO privilegio (id_privilegio, tipoprivilegio)
    VALUES (2, 'Trabajador');

INSERT INTO privilegio (id_privilegio, tipoprivilegio)
    VALUES (3, 'Cliente');

-- 4 TRABAJADOR
INSERT INTO trabajador (idtrabajador, ruttrabajador, nombretrab, apellidotrab, telefono,
                        area, cargo, correo, contrasenna, privilegio_id_privilegio, proyecto_idproyecto)
    VALUES (1, '18234567-2', 'Maria', 'Gonzalez', 987654321, 'Construccion', 'Maestro', 
        'maria.gonzalez@andes.cl', '12345', 2, 1);

INSERT INTO trabajador (idtrabajador, ruttrabajador, nombretrab, apellidotrab, telefono,
                        area, cargo, correo, contrasenna, privilegio_id_privilegio, proyecto_idproyecto)
    VALUES (2, '17111222-9', 'Carlos', 'Rojas', 912345678, 'Administracion', 'Supervisor de Proyecto',
        'carlos.rojas@pacifico.cl', 'admin2024', 1, 2);

-- 5 CASA
INSERT INTO casa (idcasa, modelocasa, cantcuarto, cantbanno, livicomecoci, piso, plano)
    VALUES (1, 'Modelo Andes A', 3, 2, 'Living-Comedor-Cocina integrada', '1', EMPTY_BLOB());

-- 6 DEPARTAMENTO
INSERT INTO departamento (iddepartamento, modelodepartamento, cantcuarto, cantbanno, livicomecoci, piso, plano)
    VALUES (1, 'Depto Vista Mar', 2, 1, 'Living-Comedor-Cocina americana', '5', EMPTY_BLOB());

-- 7 FICHA_INMUEBLE
INSERT INTO ficha_inmueble (idinmueble, tipoinmueble, proyecto_idproyecto, casa_idcasa, departamento_iddepartamento)
    VALUES (1, 'Casa', 1, 1, 1);

-- 8 ESTADO_INMUEBLE
INSERT INTO estado_inmueble (idestado, folioinmueble, estado, observacion, ficha_inmueble_idinmueble)
    VALUES (1, 1001, 'En construccion', 'Terminaciones interiores pendientes', 1);

-- 9 REGISTRO_POSVENTA
INSERT INTO registro_posventa (idregistro, tipocatastro, observacion, imagen, proyecto_idproyecto)
    VALUES (1, 'Filtracion', 'Filtracion leve en banio principal', EMPTY_BLOB(), 1);

-- 10 REPORTE
INSERT INTO reporte (idreporte, reporteestado, reporteproyecto, proyecto_idproyecto)
    VALUES (1, 'Activo', 'Revision mensual de avances', 1);

-- 11 CLIENTE
INSERT INTO cliente (idcliente, rutcliente, nombrecli, apellidocli, telefono, correo, contrasenna, registro_posventa_idregistro)
    VALUES (1, '19876543-2', 'Luis', 'Perez', 987112233, 'luis.perez@gmail.com', 'cliente2024', 1);


--COMMIT;

------------------------------------------------------------------
-- 1. COLUMNAS REQUERIDAS PARA LA LÓGICA
------------------------------------------------------------------

ALTER TABLE registro_posventa
  ADD fecha_reclamo DATE DEFAULT SYSDATE;

ALTER TABLE estado_inmueble
  ADD fecha_estado DATE DEFAULT SYSDATE;


------------------------------------------------------------------
-- 2. TYPES (CONTACTO + VARRAY CONTACTOS DE PROYECTO)
------------------------------------------------------------------

CREATE OR REPLACE TYPE t_contacto_proyecto AS OBJECT (
    nombre   VARCHAR2(200),
    rol      VARCHAR2(100),
    telefono VARCHAR2(20),
    correo   VARCHAR2(200)
);
/

CREATE OR REPLACE TYPE varray_contactos_proyecto AS VARRAY(5) OF t_contacto_proyecto;
/


------------------------------------------------------------------
-- 3. TRIGGERS
------------------------------------------------------------------

-- 3.1 PROYECTO: validar fechas y setear PK
CREATE OR REPLACE TRIGGER trg_bi_proyecto
BEFORE INSERT ON proyecto
FOR EACH ROW
BEGIN
    IF :NEW.idproyecto IS NULL THEN
        :NEW.idproyecto := seq_proyecto.NEXTVAL;
    END IF;

    IF :NEW.fechainicio > :NEW.fechaestimtermi THEN
        RAISE_APPLICATION_ERROR(
            -20001,
            'fechaestimtermi no puede ser menor que fechainicio'
        );
    END IF;
END;
/
-- Tabla: PROYECTO (idproyecto, fechainicio, fechaestimtermi, ...)


-- 3.2 TRABAJADOR: setear PK, validar RUT, ofuscar contraseña
CREATE OR REPLACE TRIGGER trg_bi_trabajador
BEFORE INSERT ON trabajador
FOR EACH ROW
DECLARE
    v_len NUMBER;

    FUNCTION fn_reverse(p_txt VARCHAR2) RETURN VARCHAR2 IS
        v_out VARCHAR2(4000) := '';
    BEGIN
        IF p_txt IS NULL THEN
            RETURN NULL;
        END IF;

        FOR i IN REVERSE 1 .. LENGTH(p_txt) LOOP
            v_out := v_out || SUBSTR(p_txt, i, 1);
        END LOOP;

        RETURN v_out;
    END fn_reverse;

BEGIN
    IF :NEW.idtrabajador IS NULL THEN
        :NEW.idtrabajador := seq_trabajador.NEXTVAL;
    END IF;

    v_len := LENGTH(:NEW.ruttrabajador);
    IF v_len < 8 OR v_len > 12 THEN
        RAISE_APPLICATION_ERROR(
            -20002,
            'RUT trabajador con formato inválido'
        );
    END IF;

    IF :NEW.contrasenna IS NOT NULL THEN
        :NEW.contrasenna :=
            RAWTOHEX(
                UTL_RAW.CAST_TO_RAW(
                    fn_reverse(:NEW.contrasenna)
                )
            );
    END IF;
END;
/
-- Tabla: TRABAJADOR (idtrabajador, ruttrabajador, contrasenna, ...)


-- 3.3 CLIENTE: setear PK, validar correo, ofuscar contraseña
CREATE OR REPLACE TRIGGER trg_bi_cliente
BEFORE INSERT ON cliente
FOR EACH ROW
DECLARE
    FUNCTION fn_reverse(p_txt VARCHAR2) RETURN VARCHAR2 IS
        v_out VARCHAR2(4000) := '';
    BEGIN
        IF p_txt IS NULL THEN
            RETURN NULL;
        END IF;

        FOR i IN REVERSE 1 .. LENGTH(p_txt) LOOP
            v_out := v_out || SUBSTR(p_txt, i, 1);
        END LOOP;

        RETURN v_out;
    END fn_reverse;
BEGIN
    IF :NEW.idcliente IS NULL THEN
        :NEW.idcliente := seq_cliente.NEXTVAL;
    END IF;

    IF INSTR(:NEW.correo, '@') = 0 THEN
        RAISE_APPLICATION_ERROR(
            -20003,
            'Correo cliente inválido'
        );
    END IF;

    IF :NEW.contrasenna IS NOT NULL THEN
        :NEW.contrasenna :=
            RAWTOHEX(
                UTL_RAW.CAST_TO_RAW(
                    fn_reverse(:NEW.contrasenna)
                )
            );
    END IF;
END;
/
-- Tabla: CLIENTE (idcliente, correo, contrasenna, ...)


-- 3.4 REGISTRO_POSVENTA: setear PK y fecha del reclamo
CREATE OR REPLACE TRIGGER trg_bi_registro_posventa
BEFORE INSERT ON registro_posventa
FOR EACH ROW
BEGIN
    IF :NEW.idregistro IS NULL THEN
        :NEW.idregistro := seq_registro_posventa.NEXTVAL;
    END IF;

    IF :NEW.fecha_reclamo IS NULL THEN
        :NEW.fecha_reclamo := SYSDATE;
    END IF;
END;
/
-- Tabla: REGISTRO_POSVENTA (idregistro, fecha_reclamo, ...)


-- 3.5 ESTADO_INMUEBLE: setear PK y fecha de estado
CREATE OR REPLACE TRIGGER trg_bi_estado_inmueble
BEFORE INSERT ON estado_inmueble
FOR EACH ROW
BEGIN
    IF :NEW.idestado IS NULL THEN
        :NEW.idestado := seq_estado_inmueble.NEXTVAL;
    END IF;

    IF :NEW.fecha_estado IS NULL THEN
        :NEW.fecha_estado := SYSDATE;
    END IF;
END;
/
-- Tabla: ESTADO_INMUEBLE (idestado, fecha_estado, ficha_inmueble_idinmueble, ...)


-- 3.6 AUDITORÍA: cada nuevo estado_inmueble genera un registro en REPORTE
CREATE OR REPLACE TRIGGER trg_ai_estado_inmueble_reporte
AFTER INSERT ON estado_inmueble
FOR EACH ROW
DECLARE
    v_idproyecto proyecto.idproyecto%TYPE;
    v_nomproy    proyecto.nomproyecto%TYPE;
BEGIN
    SELECT f.proyecto_idproyecto,
           p.nomproyecto
    INTO   v_idproyecto,
           v_nomproy
    FROM   ficha_inmueble f
           JOIN proyecto p
             ON p.idproyecto = f.proyecto_idproyecto
    WHERE  f.idinmueble = :NEW.ficha_inmueble_idinmueble;

    INSERT INTO reporte (
        idreporte,
        reporteestado,
        reporteproyecto,
        proyecto_idproyecto
    ) VALUES (
        seq_reporte.NEXTVAL,
        'Inmueble '||:NEW.ficha_inmueble_idinmueble||
        ' estado="'||:NEW.estado||'" obs="'||:NEW.observacion||'"',
        'Proyecto '||v_nomproy,
        v_idproyecto
    );
END;
/
-- Tabla: REPORTE (idreporte, reporteestado, reporteproyecto, proyecto_idproyecto)


------------------------------------------------------------------
-- 4. FUNCIONES
------------------------------------------------------------------

-- 4.1 nombre completo trabajador
CREATE OR REPLACE FUNCTION fn_nombre_trabajador (
    p_idtrabajador IN trabajador.idtrabajador%TYPE
) RETURN VARCHAR2
IS
    v_full VARCHAR2(300);
BEGIN
    SELECT nombretrab || ' ' || apellidotrab
    INTO   v_full
    FROM   trabajador
    WHERE  idtrabajador = p_idtrabajador;

    RETURN v_full;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
/
-- Usa tabla TRABAJADOR


-- 4.2 días que lleva abierto un reclamo postventa
CREATE OR REPLACE FUNCTION fn_dias_reclamo (
    p_idregistro IN registro_posventa.idregistro%TYPE
) RETURN NUMBER
IS
    v_dias NUMBER;
BEGIN
    SELECT TRUNC(SYSDATE - fecha_reclamo)
    INTO   v_dias
    FROM   registro_posventa
    WHERE  idregistro = p_idregistro;

    RETURN v_dias;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
/
-- Usa tabla REGISTRO_POSVENTA


-- 4.3 % de avance del proyecto (unidades listas vs total)
CREATE OR REPLACE FUNCTION fn_porcentaje_avance_proyecto (
    p_idproyecto IN proyecto.idproyecto%TYPE
) RETURN NUMBER
IS
    v_total   NUMBER;
    v_listos  NUMBER;
BEGIN
    SELECT COUNT(*)
    INTO   v_total
    FROM   ficha_inmueble fi
    WHERE  fi.proyecto_idproyecto = p_idproyecto;

    IF v_total = 0 THEN
        RETURN 0;
    END IF;

    SELECT COUNT(*)
    INTO   v_listos
    FROM (
        SELECT fi.idinmueble,
               (
                 SELECT ei.estado
                 FROM   estado_inmueble ei
                 WHERE  ei.ficha_inmueble_idinmueble = fi.idinmueble
                 ORDER BY ei.fecha_estado DESC
                 FETCH FIRST 1 ROWS ONLY
               ) AS estado_actual
        FROM   ficha_inmueble fi
        WHERE  fi.proyecto_idproyecto = p_idproyecto
    )
    WHERE UPPER(estado_actual) = 'LISTO ENTREGA';

    RETURN ROUND((v_listos / v_total) * 100, 2);
END;
/
-- Usa FICHA_INMUEBLE y ESTADO_INMUEBLE


------------------------------------------------------------------
-- 5. PROCEDIMIENTOS
------------------------------------------------------------------

-- 5.1 crear_proyecto
CREATE OR REPLACE PROCEDURE crear_proyecto (
    p_codigoproyecto      IN proyecto.codigoproyecto%TYPE,
    p_nomproyecto         IN proyecto.nomproyecto%TYPE,
    p_ubicacion           IN proyecto.ubicacion%TYPE,
    p_fechainicio         IN proyecto.fechainicio%TYPE,
    p_fechaestimtermi     IN proyecto.fechaestimtermi%TYPE,
    p_idconstructora      IN proyecto.constructora_idconstructora%TYPE,
    p_id_generado         OUT proyecto.idproyecto%TYPE
) IS
BEGIN
    INSERT INTO proyecto (
        idproyecto,
        codigoproyecto,
        nomproyecto,
        ubicacion,
        fechainicio,
        fechaestimtermi,
        constructora_idconstructora
    ) VALUES (
        seq_proyecto.NEXTVAL,
        p_codigoproyecto,
        p_nomproyecto,
        p_ubicacion,
        p_fechainicio,
        p_fechaestimtermi,
        p_idconstructora
    )
    RETURNING idproyecto INTO p_id_generado;
END;
/
-- Inserta PROYECTO aplicando validaciones del trigger


-- 5.2 asignar_trabajador_a_proyecto
CREATE OR REPLACE PROCEDURE asignar_trabajador_a_proyecto (
    p_idtrabajador IN trabajador.idtrabajador%TYPE,
    p_idproyecto   IN proyecto.idproyecto%TYPE
) IS
    v_dummy NUMBER;
BEGIN
    SELECT 1 INTO v_dummy FROM proyecto WHERE idproyecto = p_idproyecto;
    SELECT 1 INTO v_dummy FROM trabajador WHERE idtrabajador = p_idtrabajador;

    UPDATE trabajador
    SET    proyecto_idproyecto = p_idproyecto
    WHERE  idtrabajador = p_idtrabajador;
END;
/
-- Hace el "asigna este trabajador a este proyecto"


-- 5.3 registrar_postventa
CREATE OR REPLACE PROCEDURE registrar_postventa (
    p_tipocatastro    IN registro_posventa.tipocatastro%TYPE,
    p_observacion     IN registro_posventa.observacion%TYPE,
    p_imagen          IN registro_posventa.imagen%TYPE,
    p_idproyecto      IN registro_posventa.proyecto_idproyecto%TYPE,
    p_id_generado     OUT registro_posventa.idregistro%TYPE
) IS
BEGIN
    INSERT INTO registro_posventa (
        idregistro,
        tipocatastro,
        observacion,
        imagen,
        proyecto_idproyecto,
        fecha_reclamo
    ) VALUES (
        seq_registro_posventa.NEXTVAL,
        p_tipocatastro,
        p_observacion,
        p_imagen,
        p_idproyecto,
        SYSDATE
    )
    RETURNING idregistro INTO p_id_generado;
END;
/
-- Inserta un reclamo postventa para ese proyecto


-- 5.4 actualizar_estado_inmueble
CREATE OR REPLACE PROCEDURE actualizar_estado_inmueble (
    p_idinmueble   IN estado_inmueble.ficha_inmueble_idinmueble%TYPE,
    p_estado       IN estado_inmueble.estado%TYPE,
    p_observacion  IN estado_inmueble.observacion%TYPE
) IS
BEGIN
    INSERT INTO estado_inmueble (
        idestado,
        folioinmueble,
        estado,
        observacion,
        ficha_inmueble_idinmueble,
        fecha_estado
    ) VALUES (
        seq_estado_inmueble.NEXTVAL,
        seq_estado_inmueble.CURRVAL,
        p_estado,
        p_observacion,
        p_idinmueble,
        SYSDATE
    );
END;
/
-- Inserta un nuevo registro de estado técnico del inmueble


------------------------------------------------------------------
-- 6. PACKAGES
------------------------------------------------------------------

-- 6.1 pkg_proyecto SPEC
CREATE OR REPLACE PACKAGE pkg_proyecto AS
    CURSOR c_viviendas_proyecto(p_idproyecto NUMBER) IS
        SELECT fi.idinmueble,
               fi.tipoinmueble,
               (
                 SELECT ei.estado
                 FROM   estado_inmueble ei
                 WHERE  ei.ficha_inmueble_idinmueble = fi.idinmueble
                 ORDER BY ei.fecha_estado DESC
                 FETCH FIRST 1 ROWS ONLY
               ) AS estado_actual
        FROM   ficha_inmueble fi
        WHERE  fi.proyecto_idproyecto = p_idproyecto;

    FUNCTION porcentaje_avance(p_idproyecto NUMBER) RETURN NUMBER;

    FUNCTION contactos_proyecto(p_idproyecto NUMBER)
        RETURN varray_contactos_proyecto;

    PROCEDURE crear(
        p_codigoproyecto      IN proyecto.codigoproyecto%TYPE,
        p_nomproyecto         IN proyecto.nomproyecto%TYPE,
        p_ubicacion           IN proyecto.ubicacion%TYPE,
        p_fechainicio         IN proyecto.fechainicio%TYPE,
        p_fechaestimtermi     IN proyecto.fechaestimtermi%TYPE,
        p_idconstructora      IN proyecto.constructora_idconstructora%TYPE,
        p_id_generado         OUT proyecto.idproyecto%TYPE
    );
END pkg_proyecto;
/
-- 6.1 pkg_proyecto BODY
CREATE OR REPLACE PACKAGE BODY pkg_proyecto AS

    FUNCTION porcentaje_avance(p_idproyecto NUMBER) RETURN NUMBER IS
    BEGIN
        RETURN fn_porcentaje_avance_proyecto(p_idproyecto);
    END;

    FUNCTION contactos_proyecto(p_idproyecto NUMBER)
        RETURN varray_contactos_proyecto
    IS
        v_result varray_contactos_proyecto := varray_contactos_proyecto();
    BEGIN
        v_result.EXTEND(5);

        DECLARE
            CURSOR c_contactos IS
                SELECT nombretrab || ' ' || apellidotrab AS nombre,
                       cargo AS rol,
                       telefono,
                       correo
                FROM   trabajador
                WHERE  proyecto_idproyecto = p_idproyecto
                AND    ROWNUM <= 5;
            i PLS_INTEGER := 0;
        BEGIN
            FOR r IN c_contactos LOOP
                i := i + 1;
                v_result(i) := t_contacto_proyecto(
                    r.nombre,
                    r.rol,
                    TO_CHAR(r.telefono),
                    r.correo
                );
            END LOOP;

            v_result.TRIM(5 - i);
        END;

        RETURN v_result;
    END;

    PROCEDURE crear(
        p_codigoproyecto      IN proyecto.codigoproyecto%TYPE,
        p_nomproyecto         IN proyecto.nomproyecto%TYPE,
        p_ubicacion           IN proyecto.ubicacion%TYPE,
        p_fechainicio         IN proyecto.fechainicio%TYPE,
        p_fechaestimtermi     IN proyecto.fechaestimtermi%TYPE,
        p_idconstructora      IN proyecto.constructora_idconstructora%TYPE,
        p_id_generado         OUT proyecto.idproyecto%TYPE
    ) IS
    BEGIN
        crear_proyecto(
            p_codigoproyecto,
            p_nomproyecto,
            p_ubicacion,
            p_fechainicio,
            p_fechaestimtermi,
            p_idconstructora,
            p_id_generado
        );
    END;

END pkg_proyecto;
/
-- pkg_proyecto entrega cursor, % avance y contactos clave


-- 6.2 pkg_postventa SPEC
CREATE OR REPLACE PACKAGE pkg_postventa AS
    CURSOR c_postventa_abierta(p_idproyecto NUMBER) IS
        SELECT rp.idregistro,
               rp.tipocatastro,
               rp.observacion,
               rp.fecha_reclamo,
               p.nomproyecto
        FROM   registro_posventa rp
               JOIN proyecto p
                 ON p.idproyecto = rp.proyecto_idproyecto
        WHERE  rp.proyecto_idproyecto = p_idproyecto
        ORDER BY rp.fecha_reclamo DESC;

    FUNCTION dias_abierto(p_idregistro NUMBER) RETURN NUMBER;

    PROCEDURE crear_reclamo(
        p_tipocatastro    IN registro_posventa.tipocatastro%TYPE,
        p_observacion     IN registro_posventa.observacion%TYPE,
        p_imagen          IN registro_posventa.imagen%TYPE,
        p_idproyecto      IN registro_posventa.proyecto_idproyecto%TYPE,
        p_id_generado     OUT registro_posventa.idregistro%TYPE
    );
END pkg_postventa;
/
-- 6.2 pkg_postventa BODY
CREATE OR REPLACE PACKAGE BODY pkg_postventa AS

    FUNCTION dias_abierto(p_idregistro NUMBER) RETURN NUMBER IS
    BEGIN
        RETURN fn_dias_reclamo(p_idregistro);
    END;

    PROCEDURE crear_reclamo(
        p_tipocatastro    IN registro_posventa.tipocatastro%TYPE,
        p_observacion     IN registro_posventa.observacion%TYPE,
        p_imagen          IN registro_posventa.imagen%TYPE,
        p_idproyecto      IN registro_posventa.proyecto_idproyecto%TYPE,
        p_id_generado     OUT registro_posventa.idregistro%TYPE
    ) IS
    BEGIN
        registrar_postventa(
            p_tipocatastro,
            p_observacion,
            p_imagen,
            p_idproyecto,
            p_id_generado
        );
    END;

END pkg_postventa;
/
-- pkg_postventa maneja reclamos y SLA


-- 6.3 pkg_inmueble SPEC
CREATE OR REPLACE PACKAGE pkg_inmueble AS

    TYPE rec_ficha_entrega IS RECORD (
        idinmueble        ficha_inmueble.idinmueble%TYPE,
        tipoinmueble      ficha_inmueble.tipoinmueble%TYPE,
        estado_actual     estado_inmueble.estado%TYPE,
        observacion       estado_inmueble.observacion%TYPE,
        proyecto_nombre   proyecto.nomproyecto%TYPE,
        proyecto_ubic     proyecto.ubicacion%TYPE,
        cliente_nombre    cliente.nombrecli%TYPE,
        cliente_apellido  cliente.apellidocli%TYPE,
        cliente_rut       cliente.rutcliente%TYPE,
        cliente_tel       cliente.telefono%TYPE,
        cliente_correo    cliente.correo%TYPE
    );

    PROCEDURE generar_ficha_entrega(
        p_idinmueble IN ficha_inmueble.idinmueble%TYPE,
        o_ficha      OUT rec_ficha_entrega
    );

    PROCEDURE actualizar_estado(
        p_idinmueble   IN estado_inmueble.ficha_inmueble_idinmueble%TYPE,
        p_estado       IN estado_inmueble.estado%TYPE,
        p_observacion  IN estado_inmueble.observacion%TYPE
    );

END pkg_inmueble;
/
-- 6.3 pkg_inmueble BODY
CREATE OR REPLACE PACKAGE BODY pkg_inmueble AS

    PROCEDURE generar_ficha_entrega(
        p_idinmueble IN ficha_inmueble.idinmueble%TYPE,
        o_ficha      OUT rec_ficha_entrega
    ) IS
        v_idproy proyecto.idproyecto%TYPE;
        v_nombrecli      cliente.nombrecli%TYPE;
        v_apellidocli    cliente.apellidocli%TYPE;
        v_rutcli         cliente.rutcliente%TYPE;
        v_telcli         cliente.telefono%TYPE;
        v_correocli      cliente.correo%TYPE;
    BEGIN
        -- 1. proyecto dueño del inmueble
        SELECT fi.proyecto_idproyecto
        INTO   v_idproy
        FROM   ficha_inmueble fi
        WHERE  fi.idinmueble = p_idinmueble;

        -- 2. cliente asociado a reclamo reciente del mismo proyecto (si existe)
        BEGIN
            SELECT c1.nombrecli,
                   c1.apellidocli,
                   c1.rutcliente,
                   c1.telefono,
                   c1.correo
            INTO   v_nombrecli,
                   v_apellidocli,
                   v_rutcli,
                   v_telcli,
                   v_correocli
            FROM   cliente c1
                   JOIN registro_posventa rp1
                     ON rp1.idregistro = c1.registro_posventa_idregistro
            WHERE  rp1.proyecto_idproyecto = v_idproy
            FETCH FIRST 1 ROWS ONLY;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                v_nombrecli   := NULL;
                v_apellidocli := NULL;
                v_rutcli      := NULL;
                v_telcli      := NULL;
                v_correocli   := NULL;
        END;

        -- 3. consolidar estado técnico más reciente del inmueble + proyecto + cliente
        SELECT fi.idinmueble,
               fi.tipoinmueble,
               est.estado_actual,
               est.obs_actual,
               p.nomproyecto,
               p.ubicacion,
               v_nombrecli,
               v_apellidocli,
               v_rutcli,
               v_telcli,
               v_correocli
        INTO   o_ficha
        FROM   ficha_inmueble fi
               JOIN proyecto p
                 ON p.idproyecto = fi.proyecto_idproyecto
               LEFT JOIN (
                    SELECT ei1.ficha_inmueble_idinmueble AS id_inm,
                           ei1.estado AS estado_actual,
                           ei1.observacion AS obs_actual
                    FROM   estado_inmueble ei1
                    WHERE  (ei1.ficha_inmueble_idinmueble,
                            ei1.fecha_estado)
                           IN (
                               SELECT ei2.ficha_inmueble_idinmueble,
                                      MAX(ei2.fecha_estado)
                               FROM   estado_inmueble ei2
                               GROUP BY ei2.ficha_inmueble_idinmueble
                           )
               ) est
                 ON est.id_inm = fi.idinmueble
        WHERE  fi.idinmueble = p_idinmueble;
    END;


    PROCEDURE actualizar_estado(
        p_idinmueble   IN estado_inmueble.ficha_inmueble_idinmueble%TYPE,
        p_estado       IN estado_inmueble.estado%TYPE,
        p_observacion  IN estado_inmueble.observacion%TYPE
    ) IS
    BEGIN
        actualizar_estado_inmueble(
            p_idinmueble,
            p_estado,
            p_observacion
        );
    END;

END pkg_inmueble;
/
-- pkg_inmueble arma la ficha lista para entrega de vivienda


