import pytest
import os
import platform
from unittest.mock import patch, Mock, call
from src.glgrpa.Windows import Windows
from datetime import datetime

@pytest.fixture
def windows_dev(tmp_path) -> Windows:
    """Fixture para inicializar la clase Windows en modo dev"""
    return Windows(dev=True)

    
@pytest.fixture
def mock_carpeta_descargas(tmp_path: str):
    """Fixture para simular la carpeta de descargas personalizada"""
    descarga_personalizada = tmp_path / "DescargaPersonalizada"
    os.makedirs(descarga_personalizada, exist_ok=True)
    
    # Simular la variable de entorno según el sistema operativo
    if platform.system() == "Windows":
        with patch.dict("os.environ", {"USERPROFILE": str(tmp_path)}):
            yield descarga_personalizada
    else:
        with patch.dict("os.environ", {"HOME": str(tmp_path)}):
            yield descarga_personalizada
    

@patch("os.listdir", return_value=["archivo1.txt", "archivo2.txt"])
@patch("os.remove")
def test_purgar_carpeta_descargas_personalizada(mock_remove: Mock, mock_listdir: Mock, windows_dev: Windows, mock_carpeta_descargas):
    """Prueba para verificar que se eliminan los archivos de la carpeta de descargas"""
    windows_dev.carpeta_descargas_personalizada = mock_carpeta_descargas
    windows_dev.purgar_carpeta_descargas_personalizada()
    mock_listdir.assert_called_once_with(mock_carpeta_descargas)
    mock_remove.assert_has_calls([
        call(os.path.join(mock_carpeta_descargas, "archivo1.txt")),
        call(os.path.join(mock_carpeta_descargas, "archivo2.txt"))
    ])

@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
def test_crear_carpeta_si_no_existe(mock_makedirs: Mock, mock_exists: Mock, windows_dev: Windows):
    """Prueba para verificar que se crea una carpeta si no existe"""
    carpeta = "C:\\Ruta\\NuevaCarpeta"
    resultado = windows_dev.crear_carpeta_si_no_existe(carpeta)
    mock_exists.assert_called_once_with(carpeta)
    mock_makedirs.assert_called_once_with(carpeta)
    assert resultado is True

@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
def test_crear_carpeta_si_no_existe_ya_existe(mock_makedirs: Mock, mock_exists: Mock, windows_dev: Windows):
    """Prueba para verificar que no se crea una carpeta si ya existe"""
    carpeta = "C:\\Ruta\\CarpetaExistente"
    resultado = windows_dev.crear_carpeta_si_no_existe(carpeta)
    mock_exists.assert_called_once_with(carpeta)
    mock_makedirs.assert_not_called()
    assert resultado is True

@patch("os.listdir", return_value=["archivo1.txt", "archivo2.txt"])
@patch("os.path.getmtime", side_effect=[100, 200])
def test_buscar_ultimo_archivo(mock_getmtime: Mock, mock_listdir: Mock, windows_dev: Windows):
    """test_buscar_ultimo_archivo"""
    ruta = "C:\\Ruta\\Descargas"
    extension = ".txt"
    resultado = windows_dev.buscar_ultimo_archivo(ruta, extension)
    mock_listdir.assert_called_once_with(ruta)
    mock_getmtime.assert_has_calls([
        call(os.path.join(ruta, "archivo1.txt")),
        call(os.path.join(ruta, "archivo2.txt"))
    ])
    assert resultado == os.path.join(ruta, "archivo2.txt")

@patch("os.listdir", return_value=[])
def test_buscar_ultimo_archivo_no_encontrado(mock_listdir: Mock, windows_dev: Windows):
    """Prueba para verificar que se lanza una excepción si no se encuentran archivos"""
    ruta = "C:\\Ruta\\Descargas"
    extension = ".txt"
    with pytest.raises(FileNotFoundError):
        windows_dev.buscar_ultimo_archivo(ruta, extension)
    mock_listdir.assert_called_once_with(ruta)

@patch("os.rename")
@patch("os.makedirs")
@patch("os.path.exists", side_effect=[False, False])
@patch("os.path.basename", return_value="archivo.txt")
def test_mover_archivo(mock_basename: Mock, mock_exists: Mock, mock_makedirs: Mock, mock_rename: Mock, windows_dev: Windows):
    """Prueba para verificar que se mueve un archivo correctamente"""
    ruta_archivo = "C:\\Ruta\\archivo.txt"
    ruta_destino = "C:\\Destino"
    
    # Ejecutar el método
    resultado = windows_dev.mover_archivo(ruta_archivo, ruta_destino)
    
    # Verificar que se obtengo el nombre del archivo
    mock_basename.assert_called_once_with(ruta_archivo)
    
    # Verificar que se chequea la existencia de la carpeta y el archivo
    mock_exists.assert_has_calls([
        call(ruta_destino),
        call(os.path.join(ruta_destino, "archivo.txt"))
    ])
    
    # Verificar que se intenta crear la carpeta
    mock_makedirs.assert_called_once_with(ruta_destino)
    
    # Verificar que se mueve el archivo
    mock_rename.assert_called_once_with(ruta_archivo, os.path.join(ruta_destino, "archivo.txt"))
    
    # Verificar el resultado
    assert resultado == os.path.join(ruta_destino, "archivo.txt")

@patch("os.path.join", side_effect=lambda *args: "\\".join(args))
def test_armar_estructura_de_carpetas(mock_join: Mock, windows_dev: Windows):
    """Prueba para verificar que se arma correctamente la estructura de carpetas"""
    ruta = "C:\\Base"
    
    # Ejecutar el método
    with patch("datetime.datetime") as mock_datetime:
        # Configurar el mock de datetime
        mock_datetime.now.return_value = datetime.now()
        
        # Obtener el resultado
        resultado = windows_dev.armar_estructura_de_carpetas(ruta)
        
        # Verificar que se obtiene la fecha actual con el formato [Base\anio\mes\dia]
        anio = mock_datetime.now().strftime("%Y")
        mes = mock_datetime.now().strftime("%m")
        dia = mock_datetime.now().strftime("%d")
        assert resultado == f"C:\\Base\\{anio}\\{mes}\\{dia}"