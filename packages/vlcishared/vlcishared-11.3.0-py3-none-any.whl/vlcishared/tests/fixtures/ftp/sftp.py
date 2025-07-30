import os
import shutil
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_sftp_patch(monkeypatch):
    """
    Fixture reutilizable que mockea la clase SFTPClient para evitar conexiones reales con SFTP.

    - Reutilizable en distintos módulos donde se importe SFTPClient.
    - Mockea los métodos: list, list_sorted_date_modification, download (con shutil.copyfile), move, upload, delete y sftp.rename para evitar efectos reales.
    - Devuelve una función que permite especificar el path del import y el retorno de list().
    - Requiere pasar la ruta donde se usa SFTPClient (para monkeypatching dinámico).

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `PostgresConnector` (ej. "mi_paquete.mi_modulo.PostgresConnector").
    - list_return (list): Lista de archivos que devolverá `list()`.
    - list_side_effect (callable|None): Función a ejecutar en `list()`.
    - list_sorted_date_modification_return (list): Resultado que devolverá `list_sorted_date_modification()`.
    - list_sorted_date_modification_side_effect (callable|None): Función a ejecutar en `list_sorted_date_modification()`.
    - download_side_effect (callable|None): Función a ejecutar en `download()`, por defecto usa `patch_download_side_effect`.
    - move_side_effect (callable|None): Función a ejecutar en `move()`.
    - upload_side_effect (callable|None): Función a ejecutar en `upload()`.
    - delete_side_effect (callable|None): Función a ejecutar en `delete()`.
    - sftp_rename_side_effect (callable|None): Función a ejecutar en `sftp.rename()`.

    Uso:
        def test_xxx(mock_sftp_patch):
            mock_sftp = mock_sftp_patch("modulo.donde.importa.SFTPClient", list_return=["file1.csv"], ...)
    """

    def _patch(
        ruta_importacion: str,
        list_return=[],
        list_side_effect=None,
        list_sorted_date_modification_return=[],
        list_sorted_date_modification_side_effect=None,
        download_side_effect=patch_download_side_effect,
        move_side_effect=patch_move_side_effect,
        upload_side_effect=patch_upload_side_effect,
        delete_side_effect=patch_delete_side_effect,
        sftp_rename_side_effect=patch_sftp_rename_side_effect,
    ):
        sftp = MagicMock()

        sftp.connect.return_value = None
        sftp.close.return_value = None

        sftp.list.return_value = list_return
        if list_side_effect:
            sftp.list.side_effect = list_side_effect

        sftp.list_sorted_date_modification.return_value = list_sorted_date_modification_return
        if list_sorted_date_modification_side_effect:
            sftp.list_sorted_date_modification.side_effect = list_sorted_date_modification_side_effect

        sftp.download.side_effect = download_side_effect
        sftp.move.side_effect = move_side_effect
        sftp.upload.side_effect = upload_side_effect
        sftp.delete.side_effect = delete_side_effect

        sftp.sftp = MagicMock()
        sftp.sftp.rename.side_effect = sftp_rename_side_effect

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: sftp)
        return sftp

    return _patch


def patch_download_side_effect(origen, tmp_folder, archivo):
    """
    Simula la descarga de un archivo SFTP copiándolo desde 'origen' a 'tmp_folder'.
    """
    shutil.copyfile(os.path.join(origen, archivo), os.path.join(tmp_folder, archivo))


def patch_move_side_effect(origen, destino, archivo):
    """
    Simula el mover de un archivo SFTP moviendolo desde 'origen' a 'tmp_folder'.
    """
    shutil.move(os.path.join(origen, archivo), os.path.join(destino, archivo))


def patch_upload_side_effect(origen, destino):
    """
    Simula la subida de un archivo SFTP copiándolo desde 'origen' a 'destino'.
    """
    shutil.copyfile(origen, destino)


def patch_delete_side_effect(archivo):
    """
    Simula la eliminación de un archivo SFTP eliminandolo en la ruta recibida.
    """
    os.remove(archivo)


def patch_sftp_rename_side_effect(nombre_antiguo, nombre_nuevo):
    os.rename(nombre_antiguo, nombre_nuevo)
