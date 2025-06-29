DROP TRIGGER IF EXISTS trg_eliminar_recibos;
DROP TRIGGER IF EXISTS trg_lecturas_validate_consumo;
DROP TRIGGER IF EXISTS trg_lecturas_validate_consumo_upd;
DROP TRIGGER IF EXISTS trg_arrendos_validate_dates_upd;
DROP TRIGGER IF EXISTS trg_arrendos_validate_dates;
DROP TRIGGER IF EXISTS trg_arrendos_set_estado;
DROP TRIGGER IF EXISTS trg_arrendos_set_estado_upd;




/*			##########################################################################################
			################################# TRIGGERS TABLA recibos #################################
			##########################################################################################			*/


DELIMITER $$
CREATE TRIGGER trg_eliminar_recibos BEFORE DELETE ON recibos FOR EACH ROW
BEGIN
	-- Borrar de tabla 'acueducto'
	DELETE FROM acueducto WHERE acue_reci_id = OLD.reci_id;
    
    -- Borrar de tabla 'energia'
	DELETE FROM energia WHERE ener_reci_id = OLD.reci_id;
    
    -- Borrar de tabla 'gas'
	DELETE FROM gas WHERE gas_reci_id = OLD.reci_id;
    
    -- Borrar de tabla 'correspondencia'
	DELETE FROM correspondencia WHERE corre_reci_id = OLD.reci_id;

END;
$$
DELIMITER ;




/*			##########################################################################################
			################################# TRIGGERS TABLA lecturas ################################
			##########################################################################################			*/




DELIMITER $$

CREATE TRIGGER trg_lecturas_validate_consumo
BEFORE INSERT ON lecturas
FOR EACH ROW
BEGIN
  IF NEW.lec_consumoFinal < NEW.lec_consumoInicial THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'ERROR: Consumo final no puede ser menor al inicial';
  END IF;
END;
$$

CREATE TRIGGER trg_lecturas_validate_consumo_upd
BEFORE UPDATE ON lecturas
FOR EACH ROW
BEGIN
  IF NEW.lec_consumoFinal < NEW.lec_consumoInicial THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'ERROR: Consumo final no puede ser menor al inicial';
  END IF;
END;
$$

DELIMITER ;



/*			##########################################################################################
			################################# TRIGGERS TABLA arrendos ################################
			##########################################################################################			*/



DELIMITER $$
CREATE TRIGGER trg_arrendos_validate_dates
BEFORE INSERT ON arrendos
FOR EACH ROW
BEGIN
  IF NEW.arre_fechaFin < NEW.arre_fechaInicio THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'ERROR: Fecha fin debe ser posterior o igual a fecha inicio';
  END IF;
END;
$$

CREATE TRIGGER trg_arrendos_validate_dates_upd
BEFORE UPDATE ON arrendos
FOR EACH ROW
BEGIN
  IF NEW.arre_fechaFin < NEW.arre_fechaInicio THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'ERROR: Fecha fin debe ser posterior o igual a fecha inicio';
  END IF;
END;
$$


CREATE TRIGGER trg_arrendos_set_estado
BEFORE INSERT ON arrendos
FOR EACH ROW
BEGIN
  IF NEW.arre_fechaPago IS NOT NULL THEN
    SET NEW.arre_estado = 'CANCELADO';
  ELSE
    SET NEW.arre_estado = 'PENDIENTE';
  END IF;
END;
$$

CREATE TRIGGER trg_arrendos_set_estado_upd
BEFORE UPDATE ON arrendos
FOR EACH ROW
BEGIN
  IF NEW.arre_fechaPago IS NOT NULL THEN
    SET NEW.arre_estado = 'CANCELADO';
  ELSE
    SET NEW.arre_estado = 'PENDIENTE';
  END IF;
END;
$$
DELIMITER ;

