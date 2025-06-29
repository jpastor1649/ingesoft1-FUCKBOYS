DROP PROCEDURE IF EXISTS sp_insetar_recibos_acueducto;
DROP PROCEDURE IF EXISTS sp_insetar_recibos_energia;
DROP PROCEDURE IF EXISTS sp_insetar_recibos_gas;


DELIMITER $$
CREATE PROCEDURE sp_insetar_recibos_acueducto 
(IN fecha DATE, IN mes CHAR(50), IN consumoInicial DECIMAL(10,3), IN consumoFinal DECIMAL(10,3), IN piso TINYINT, IN cargoFijoAcue DECIMAL(10,3),
IN tarifaAcue DECIMAL(10,3), IN cargoFijoAlca DECIMAL(10,3), IN tarifaAlca DECIMAL(10,3), IN descuento TINYINT) 
BEGIN
	DECLARE new_reci_id INT;
    DECLARE consumo DECIMAL(10,3);
	
    -- Insertar en la tabla 'recibos'
    INSERT INTO recibos(reci_fecha, reci_servicio, reci_mes, reci_consumoInicial, reci_consumoFinal) VALUES (fecha, 'ACUEDUCTO Y ASEO', mes, consumoInicial, consumoFinal);
    
    -- Obtener el ID generado
    SET new_reci_id = last_insert_id();
    
    -- Obtener consumo
    SET consumo = consumoFinal - consumoInicial;
    
    -- Insertar en la tabla 'acueducto'
	INSERT INTO acueducto VALUES (new_reci_id, piso, consumo, cargoFijoAcue, tarifaAcue, cargoFijoAlca, tarifaAlca, descuento);
    
    -- Insertar en tabla 'correspondencia'
    IF piso = 1 THEN
		INSERT INTO correspondencia VALUES (new_reci_id, 1);
        INSERT INTO correspondencia VALUES (new_reci_id, 101);
        INSERT INTO correspondencia VALUES (new_reci_id, 401);
    ELSE
		INSERT INTO correspondencia VALUES (new_reci_id, 201);
        INSERT INTO correspondencia VALUES (new_reci_id, 202);
        INSERT INTO correspondencia VALUES (new_reci_id, 301);
        INSERT INTO correspondencia VALUES (new_reci_id, 302);
    END IF;

END;
$$
DELIMITER ;



DELIMITER $$
CREATE PROCEDURE sp_insetar_recibos_energia 
(IN fecha DATE, IN mes CHAR(50), IN consumoInicial DECIMAL(10,3), IN consumoFinal DECIMAL(10,3), IN piso TINYINT, IN tarifaKWH DECIMAL(10,3), IN descuento TINYINT) 
BEGIN
	DECLARE new_reci_id INT;
    DECLARE consumo DECIMAL(10,3);
	
    -- Insertar en la tabla 'recibos'
    INSERT INTO recibos(reci_fecha, reci_servicio, reci_mes, reci_consumoInicial, reci_consumoFinal) VALUES (fecha, 'ENERGIA', mes, consumoInicial, consumoFinal);
    
    -- Obtener el ID generado
    SET new_reci_id = last_insert_id();
    
    -- Obtener consumo
    SET consumo = consumoFinal - consumoInicial;
    
    -- Insertar en la tabla 'energia'
	INSERT INTO energia VALUES (new_reci_id, piso, consumo, tarifaKWH, descuento);
    
    -- Insertar en tabla 'correspondencia'
    IF piso = 1 THEN
		INSERT INTO correspondencia VALUES (new_reci_id, 1);	-- AUNQUE NO SE TOME LECTURA DEL LOCAL, SE GUARDA PARA FUTURAS OCASIONES
        INSERT INTO correspondencia VALUES (new_reci_id, 101);
        INSERT INTO correspondencia VALUES (new_reci_id, 401);
    ELSE
        INSERT INTO correspondencia VALUES (new_reci_id, 301);
        INSERT INTO correspondencia VALUES (new_reci_id, 302);
    END IF;

END;
$$
DELIMITER ;



DELIMITER $$
CREATE PROCEDURE sp_insetar_recibos_gas 
(IN fecha DATE, IN mes CHAR(50), IN consumoInicial DECIMAL(10,3), IN consumoFinal DECIMAL(10,3), IN consumo DECIMAL(10,3), IN apto SMALLINT, IN tarifaFija DECIMAL(10,3), IN tarifaM3 DECIMAL(10,3)) 
BEGIN
	DECLARE new_reci_id INT;
	
    -- Insertar en la tabla 'recibos'
    INSERT INTO recibos(reci_fecha, reci_servicio, reci_mes, reci_consumoInicial, reci_consumoFinal) VALUES (fecha, 'GAS NATURAL', mes, consumoInicial, consumoFinal);
    
    -- Obtener el ID generado
    SET new_reci_id = last_insert_id();
    
    -- Insertar en la tabla 'gas'
	INSERT INTO gas VALUES (new_reci_id, consumo, tarifaFija, tarifaM3);	-- El consumo se ingresa en vez de calcularlo, dado que el recibo tiene factores de corrección
    
    -- Insertar en tabla 'correspondencia'
    IF apto = 201 THEN
        INSERT INTO correspondencia VALUES (new_reci_id, 201);
	ELSEIF apto = 202 THEN
		INSERT INTO correspondencia VALUES (new_reci_id, 202);
	ELSEIF apto = 301 THEN
		INSERT INTO correspondencia VALUES (new_reci_id, 301);
	ELSEIF apto = 302 THEN
		INSERT INTO correspondencia VALUES (new_reci_id, 302);
	ELSE
		INSERT INTO correspondencia VALUES (new_reci_id, 101);
        INSERT INTO correspondencia VALUES (new_reci_id, 401);
    END IF;

END;
$$
DELIMITER ;

