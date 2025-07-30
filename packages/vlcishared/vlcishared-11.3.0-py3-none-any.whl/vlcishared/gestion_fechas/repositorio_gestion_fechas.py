import logging

from vlcishared.db.postgresql import PostgresConnector


class RepositorioGestionFechas:
    """
    Repositorio para acceder a funciones SQL relacionadas con la gestión de fechas para ETLs.
    """

    def __init__(self, etl_id):
        self.log = logging.getLogger()
        self.etl_id = etl_id
        try:
            self.conector_db = PostgresConnector.instance()
        except Exception as e:
            self.log.error("GestionFechas requiere que PostgresConnector esté inicializado previamente.")
            raise e

        self._initialized = True

    def _sql_p_gf_averiguar_ejecucion(self):
        """
        Método interno que llama a la función SQL `p_gf_averiguarejecucion`.

        La función SQL devuelve una tupla `(out_result, out_status)`:
        - out_result (str): "t" o "f", representando True o False respectivamente.
        - out_status (str): "OK" si la llamada fue exitosa, o un mensaje de error.

        Retorna:
            tuple[str, str]: Resultado y estado devueltos por la función SQL.
        """
        resultado_raw = self.conector_db.call_procedure("p_gf_averiguarejecucion", self.etl_id, is_function=True)
        raw_str = resultado_raw[0][0]
        out_result, out_status = raw_str.strip("()").split(",")
        return out_result, out_status

    def _sql_p_gf_obtener_fecha(self, campo_fecha):
        """
        Método interno que llama a la función SQL p_gf_obtener_fecha.

        La función SQL devuelve una tupla `(out_result, out_status)`:
            - out_result (str): Fecha en el formato definido en la columna `formato_fen` de la tabla `t_d_fecha_negocio_etls` de PostgreSQL. Puede devolver NULL.
            - out_status (str): "OK" si la llamada fue exitosa, o un mensaje de error.

        Retorna:
            tuple[str, str]: Resultado y estado devueltos por la función SQL.
        """
        resultado_raw = self.conector_db.call_procedure("p_gf_obtenerfecha", self.etl_id, campo_fecha, is_function=True)
        raw_str = resultado_raw[0][0].strip("()")
        parts = raw_str.split(",", 1)

        out_result = parts[0].strip() or None
        if out_result == "NULL":
            out_result = None

        out_status = parts[1].strip()
        return out_result, out_status

    def _sql_p_gf_registrar_estado_gestion_fechas(self, estado):
        """
        Método interno que llama directamente a la función SQL p_gf_registrarestadoetl.
        """
        resultado_raw = self.conector_db.call_procedure("p_gf_registrarestadoetl", self.etl_id, estado, is_function=True)
        out_status = resultado_raw[0][0]
        return out_status

    def _sql_p_gf_calcular_nueva_fecha(self):
        """
        Método interno que llama directamente a la función SQL p_gf_calcularnuevafecha.
        """
        resultado_raw = self.conector_db.call_procedure("p_gf_calcularnuevafecha", self.etl_id, is_function=True)
        out_status = resultado_raw[0][0]
        return out_status

    def _sql_p_gf_actualizar_fecha(self, campo_fecha, fecha):
        """
        Método interno que llama directamente al procedimiento SQL p_gf_actualizarFecha.
        """
        resultado_raw = self.conector_db.call_procedure("p_gf_actualizarFecha", self.etl_id, campo_fecha, fecha, "OK", is_function=False)
        out_status = resultado_raw[0][0]
        return out_status

    def hay_que_recuperar_datos(self):
        """
        Obtiene la ejecución de la ETL llamando a la función SQL `p_gf_averiguarejecucion`.

        Retorna:
            bool: True si la ETL debe ejecutarse (resultado "t"), False en caso contrario.

        Lanza:
            Exception: Si el estado devuelto no es "OK", se lanza una excepción con el mensaje de error.
        """
        out_result, out_status = self._sql_p_gf_averiguar_ejecucion()
        self.log.info(f"Se llama a p_gf_averiguar_ejecucion para ETL ID {self.etl_id}.")
        if out_status != "OK":
            raise Exception(f"Error al obtener ejecución de la ETL: {out_status}.")

        if out_result == "t":
            return True
        else:
            return False

    def obtener_fecha(self, campo_fecha):
        """
        Obtiene el valor de la fecha especificada de la ETL.

        Argumentos:
            - campo_fecha(str): nombre de la fecha que queremos recuperar. Ej: "fen", "fen_inicio", "fen_fin".

        Retorna:
            - str: Fecha en el formato definido en la columna `formato_fen` de la tabla `t_d_fecha_negocio_etls` de PostgreSQL.

        Lanza:
            Excepcion: si el estado devuelto no es "OK", se lanza una excepción con un mensaje.

        """
        fecha, out_status = self._sql_p_gf_obtener_fecha(campo_fecha)
        self.log.info(f"Se llama a p_gf_obtener_fecha para obtener la fecha {campo_fecha} de la ETL {self.etl_id}.")
        if out_status != "OK":
            raise Exception(f"Error al obtener fecha {campo_fecha}: {out_status}")

        return fecha

    def actualizar_estado_gestion_fechas(self, nuevo_estado):
        """
        Actualiza el estado de gestión de fechas de la ETL.

        Argumentos:
            - nuevo_estado(str): El estado de gestión de fechas puede tomar los valores "OK", "EN PROCESO" ó "ERROR".

        Retorna:
            - str: Retorna "OK" si el estado se actualiza correctamente o un mensaje de error.

        Lanza:
            Excepcion: si el estado no se actualiza se lanza una excepción con un mensaje.

        """
        out_status = self._sql_p_gf_registrar_estado_gestion_fechas(nuevo_estado)
        if out_status != "OK":
            raise Exception(f"Error al actualizar el estado de gestión de fechas: {out_status}")

        self.log.info(f"Se actualiza el estado de gestión de fechas de la ETL {self.etl_id} a {nuevo_estado}.")

    def calcular_siguiente_fecha(self):
        """
        Calcula la siguiente fecha a procesar automáticamente.

        Retorna:
            - str: Retorna "OK" si la nueva fecha se calcula correctamente o un mensaje de error.

        Lanza:
            Excepcion: si la fecha no se pudo calcular se lanza una excepción con un mensaje.

        """
        out_status = self._sql_p_gf_calcular_nueva_fecha()
        if out_status != "OK":
            raise Exception(f"Error al calcular nueva fecha: {out_status}")

        self.log.info("Nueva fecha calculada con éxito.")

    def actualizar_nueva_fecha(self, campo_fecha, nueva_fecha):
        """
        Setea la siguiente fecha explícitamente. En la mayoría de los casos se usa `calcular_siguiente_fecha`.

        Retorna:
            - str: Retorna "OK" si la nueva fecha se calcula correctamente o un mensaje de error.

        Lanza:
            Excepcion: si la fecha no se pudo calcular se lanza una excepción con un mensaje.

        """
        out_status = self._sql_p_gf_actualizar_fecha(campo_fecha, nueva_fecha)
        if out_status != "OK":
            raise Exception(f"Error al actualizar nueva fecha: {out_status}")

        self.log.info("Nueva fecha calculada con éxito.")
