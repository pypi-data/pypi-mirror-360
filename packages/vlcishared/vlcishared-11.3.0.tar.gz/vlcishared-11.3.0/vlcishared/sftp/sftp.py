import time

import pysftp

from vlcishared.utils.interfaces import ConnectionInterface


class SFTPClient(ConnectionInterface):
    """Clase que se conecta a un servidor sftp para descargar ficheros"""

    def __init__(self, host: str, username: str, password: str, port=22):
        """Necesita el host, username, el password y el puerto al que se va a
        conectar para inicializar el cliente"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None
        self.sftp = None

    def connect(self) -> None:
        """Intenta conectarse al servidor configurado en la instanciación"""
        try:
            self.sftp = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        except Exception as e:
            raise ConnectionRefusedError(f"Conexión fallida: {str(e)}")

    def list(self, remote_path: str) -> list:
        """Devuelve una lista con los ficheros en el directorio indicado"""
        try:
            with self.sftp.cd(remote_path):
                remote_files = self.sftp.listdir()
            return remote_files
        except Exception as e:
            raise ConnectionAbortedError(f"Fallo al listar los archivos: {str(e)}")

    def list_sorted_date_modification(self, remote_path: str) -> list:
        """Devuelve una lista con los ficheros en el directorio indicado, ordenados por fecha de modificación"""
        try:
            with self.sftp.cd(remote_path):
                remote_files_attr = self.sftp.listdir_attr()
            remote_files_attr_sorted = sorted(remote_files_attr, key=lambda attr: attr.st_mtime)
            remote_files_sorted = [attr.filename for attr in remote_files_attr_sorted]
            return remote_files_sorted
        except Exception as e:
            raise ConnectionAbortedError(f"Fallo al listar los archivos: {str(e)}")

    def download(self, remote_path: str, local_path: str, file_name: str):
        '''Descarga el fichero recibido como parámetro y
        lo guarda en el "local_path"'''
        try:
            self.sftp.get(f"{remote_path}/{file_name}", f"{local_path}/{file_name}")
        except Exception as e:
            raise ConnectionAbortedError(f"Descarga fallida: {str(e)}")

    def move(self, remote_origin_path: str, destiny_path: str, file_name: str):
        """Mueve el fichero recibido como parámetro de
        la carpeta origen a la carpeta destino"""
        try:
            self.sftp.rename(f"{remote_origin_path}/{file_name}", f"{destiny_path}/{file_name}")
        except Exception as e:
            raise ConnectionAbortedError(f"Fallo moviendo el fichero de " f"{remote_origin_path} a {destiny_path}: {str(e)}")

    def close(self):
        """Cierra la conexión al servidor SFTP"""
        if self.sftp:
            self.sftp.close()
            print(f"Conexión a {self.host} cerrada.")

    def upload(self, local_file: str, remote_path: str):
        """Sube el fichero indicado desde la máquina local al servidor SFTP"""
        try:
            self.sftp.put(local_file, remote_path)
        except Exception as e:
            raise ConnectionAbortedError(f"Subida fallida: {str(e)}")

    def delete(self, remote_file_path: str):
        """Elimina el fichero indicado en el servidor SFTP"""
        try:
            self.sftp.remove(remote_file_path)
        except Exception as e:
            raise ConnectionAbortedError(f"Error al eliminar el archivo {remote_file_path}: {str(e)}")
