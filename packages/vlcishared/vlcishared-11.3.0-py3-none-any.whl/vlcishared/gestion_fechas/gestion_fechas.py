import logging

from vlcishared.db.postgresql import PostgresConnector
from vlcishared.gestion_fechas.repositorio_gestion_fechas import RepositorioGestionFechas


class GestionFechas:
    """
    Clase con métodos orquestadores de gestión de fechas (recuperación automática de las ETLs).
    """

    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            raise Exception("GestionFechas no ha sido inicializado")
        return cls._instance

    def __new__(cls, etl_id):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, etl_id):
        if self._initialized:
            return
        self.log = logging.getLogger()
        self.etl_id = etl_id
        self.repo = RepositorioGestionFechas(etl_id)
        try:
            self.conector_db = PostgresConnector.instance()
        except Exception as e:
            self.log.error("GestionFechas requiere que PostgresConnector esté inicializado previamente.")
            raise e

        self._initialized = True

    def hay_que_recuperar_datos(self):
        return self.repo.hay_que_recuperar_datos()

    def comenzar_gestion_fechas(self, campo_fecha="fen"):
        """
        Orquesta el comienzo de gestión de fechas.
        Se llama después de chequear que la función `hay_que_recuperar_datos`devuelve True.
        Pone el estado de gestión de fechas "EN PROCESO" y obtiene la fecha especificada para que la ETL recupere datos.

        Argumentos:

            - campo_fecha: fecha que se quiere obtener. Por defecto es la fecha `fen`.

        Retorna:
            - str: Retorna la fecha especificada en el formato definido en la columna `formato_fen` de la tabla `t_d_fecha_negocio_etls` de PostgreSQL.

        Lanza:
            Excepcion: si la fecha no se pudo obtener se lanza una excepción con un mensaje.

        """
        try:
            fecha = self.repo.obtener_fecha(campo_fecha)
            self.repo.actualizar_estado_gestion_fechas("EN PROCESO")
            return fecha
        except Exception as e:
            self.log.exception(e)

    def fin_gestion_fechas_etl_OK(self):
        """
        Orquesta el final de gestión de fechas si la ETL ha ido bien. Pone el estado de gestión de fechas en "OK" y calcula la siguiente fecha a recuperar.

        Lanza:
            Excepcion: si la siguiente fecha no se pudo calcular se lanza una excepción con un mensaje.

        """
        try:
            self.repo.actualizar_estado_gestion_fechas("OK")
            self.repo.calcular_siguiente_fecha()
        except Exception as e:
            self.log.exception(e)

    def fin_gestion_fechas_etl_KO(self):
        """
        Orquesta el final de gestión de fechas si la ETL fue mal. Pone el estado de gestión de fechas en "ERROR" y no avanza la fecha.

        Lanza:
            Excepcion: si el estado de gestión de fechas no se pudo actualizar lanza una excepción con un mensaje.

        """
        try:
            self.repo.actualizar_estado_gestion_fechas("ERROR")
        except Exception as e:
            self.log.exception(e)
