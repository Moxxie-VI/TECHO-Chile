
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
