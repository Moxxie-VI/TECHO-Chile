
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

