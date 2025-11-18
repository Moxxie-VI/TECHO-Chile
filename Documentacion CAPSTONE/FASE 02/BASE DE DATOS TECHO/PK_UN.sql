
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