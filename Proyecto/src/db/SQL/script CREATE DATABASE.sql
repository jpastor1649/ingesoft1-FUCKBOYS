-- CREATE DATABASE apartamentos;
-- USE apartamentos; 

DROP TABLE IF EXISTS gas;
DROP TABLE IF EXISTS energia;
DROP TABLE IF EXISTS acueducto;
DROP TABLE IF EXISTS correspondencia;
DROP TABLE IF EXISTS recibos;
DROP TABLE IF EXISTS pagos;
DROP TABLE IF EXISTS lecturas;
DROP TABLE IF EXISTS arrendos;
DROP TABLE IF EXISTS apartamentos;
DROP TABLE IF EXISTS inquilinos;





CREATE TABLE inquilinos (
	inq_id 					INT 			UNSIGNED		PRIMARY KEY,
    inq_nombre				CHAR(50)		NOT NULL,
    inq_edad				TINYINT			UNSIGNED		NOT NULL
);

CREATE TABLE apartamentos (
	apar_id 				SMALLINT		UNSIGNED 		PRIMARY KEY,
    apar_cantidadPersonas	TINYINT			UNSIGNED		NOT NULL,
    apar_observaciones		TEXT
);

CREATE TABLE arrendos (
    arre_inq_id				INT				UNSIGNED		NOT NULL,
	arre_apar_id			SMALLINT		UNSIGNED 		NOT NULL,
    arre_fechaInicio		DATE 			NOT NULL,
    arre_fechaFin			DATE 			NOT NULL,
    arre_mes				CHAR(50)		NOT NULL,
	arre_valor				INT				UNSIGNED		NOT NULL,
    arre_fechaPago			DATE,
    arre_estado				ENUM('CANCELADO', 'PENDIENTE', 'CERRADO')	NOT NULL,
    arre_observaciones		TEXT,
    
    PRIMARY KEY(arre_fechaInicio, arre_apar_id, arre_inq_id),
    FOREIGN KEY(arre_inq_id) REFERENCES inquilinos(inq_id),
    FOREIGN KEY(arre_apar_id) REFERENCES apartamentos(apar_id)
);

CREATE TABLE lecturas (
	lec_id					INT					UNSIGNED		NOT NULL		AUTO_INCREMENT 			PRIMARY KEY,
	lec_apar_id				SMALLINT(3)			UNSIGNED		NOT NULL,
    lec_fecha				DATE				NOT NULL,
    lec_servicio			ENUM('ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL')		NOT NULL,
    lec_mes					CHAR(50)			NOT NULL,
    lec_consumoInicial		DECIMAL(10, 3)		NOT NULL,
    lec_consumoFinal		DECIMAL(10, 3)		NOT NULL,
	
    -- Índice único para garantizar unicidad de la tupla (apto, fecha, servicio)
	UNIQUE KEY ux_lectura_apto_fecha_servicio (lec_apar_id, lec_fecha, lec_servicio),
    
      -- FK simple hacia apartamentos
	CONSTRAINT fk_lecturas_apartamentos
		FOREIGN KEY (lec_apar_id)
		REFERENCES apartamentos(apar_id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

CREATE TABLE pagos (
	pago_lec_apar_id		SMALLINT(3)		UNSIGNED,
    pago_lec_fecha			DATE			NOT NULL,
    pago_lec_servicio		ENUM('ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL')		NOT NULL,
    pago_mes 				CHAR(50)	 	NOT NULL,
    pago_fechaPago			DATE,
    pago_tipoLectura		ENUM('FACTURA', 'LECTURA CONTADOR INTERNO')			NOT NULL,
    pago_consumo			TINYINT			UNSIGNED 		NOT NULL,
    pago_valorTotal			INT				UNSIGNED		NOT NULL,
    pago_estado				ENUM('CANCELADO', 'PENDIENTE', 'CERRADO'),
	pago_observacion		TEXT,
    
    PRIMARY KEY(pago_lec_apar_id, pago_lec_fecha, pago_lec_servicio),

	-- FK compuesta hacia lecturas (usa el índice único ux_lectura_apto_fecha_servicio)
	CONSTRAINT fk_pagos_lecturas
		FOREIGN KEY (pago_lec_apar_id, pago_lec_fecha, pago_lec_servicio)
		REFERENCES lecturas (lec_apar_id, lec_fecha, lec_servicio)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

CREATE TABLE recibos (
	reci_id					INT 			AUTO_INCREMENT							PRIMARY KEY,
    reci_fecha				DATE			NOT NULL,
    reci_servicio			ENUM('ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL')		NOT NULL,
    reci_mes				CHAR(50) 		NOT NULL,
    reci_consumoInicial		DECIMAL(10, 3)		NOT NULL,
    reci_consumoFinal		DECIMAL(10, 3)		NOT NULL
);

CREATE TABLE correspondencia (
	corre_reci_id			INT				AUTO_INCREMENT		NOT NULL,
    corre_apar_id 			SMALLINT		UNSIGNED 			NOT NULL,
    
    PRIMARY KEY(corre_reci_id, corre_apar_id),
    FOREIGN KEY(corre_reci_id) REFERENCES recibos(reci_id),
    FOREIGN KEY(corre_apar_id) REFERENCES apartamentos(apar_id)
);

CREATE TABLE acueducto (
	acue_reci_id					INT 				PRIMARY KEY,
    acue_piso						TINYINT(1)			UNSIGNED		NOT NULL,
    acue_consumo					DECIMAL(10, 3)		NOT NULL,
	acue_cargoFijoAcueducto			DECIMAL(10, 3)		NOT NULL,
	acue_tarifaAcueducto			DECIMAL(10, 3)		NOT NULL,
    acue_cargoFijoAlcantarillado	DECIMAL(10, 3)		NOT NULL,
    acue_tarifaAlacantarillado		DECIMAL(10, 3)		NOT NULL,
    acue_descuento					TINYINT(2)			UNSIGNED		NOT NULL,
		
	FOREIGN KEY(acue_reci_id) REFERENCES recibos(reci_id)
);

CREATE TABLE energia (
	ener_reci_id					INT 				PRIMARY KEY,
    ener_piso						TINYINT(1)			UNSIGNED		NOT NULL,
    ener_consumo					DECIMAL(10, 3)		NOT NULL,
    ener_tarifaKWH					DECIMAL(10, 3)		NOT NULL,
	ener_descuento					TINYINT(2)			UNSIGNED		NOT NULL,
    
    FOREIGN KEY(ener_reci_id) REFERENCES recibos(reci_id)
);

CREATE TABLE gas (
	gas_reci_id						INT 				PRIMARY KEY,
    gas_consumo						DECIMAL(10, 3)		NOT NULL,
    gas_tarifaFija					DECIMAL(10, 3)		NOT NULL,
    gas_tarifaM3					DECIMAL(10, 3)		NOT NULL,
    
    FOREIGN KEY(gas_reci_id) REFERENCES recibos(reci_id)
);



