# src/tests/test_Terminal.py
# Pruebas unitarias para la clase Terminal

# Librerías para pruebas unitarias
import pytest
from unittest.mock import patch, Mock

# Librerías propias
from src.glgrpa.Terminal import Terminal

# Librerías para controlar el tiempo
from datetime import datetime
import time
import os
from pathlib import Path

@pytest.fixture
def terminal_dev():
    """Fixture para inicializar la clase Terminal en modo dev"""
    return Terminal(dev=True)

@pytest.fixture
def terminal_prod():
    """Fixture para inicializar la clase Terminal en modo producción"""
    return Terminal(dev=False)

def test_obtener_hora_actual(terminal_dev: Terminal):
    """Prueba para verificar el formato de la hora actual"""
    formato = "%Y-%m-%d %H:%M:%S"
    hora_actual = terminal_dev.obtener_hora_actual(formato)
    assert datetime.strptime(hora_actual, formato), "El formato de la hora no es válido"

@patch("time.sleep", return_value=None)
def test_tiempo_espera_dev(mock_sleep: Mock, terminal_dev: Terminal):
    """Prueba para verificar que el tiempo de espera es 1 segundo en modo dev"""
    terminal_dev.demora()
    mock_sleep.assert_called_once_with(1)

@patch("time.sleep", return_value=None)
def test_tiempo_espera_prod(mock_sleep: Mock, terminal_prod: Terminal):
    """Prueba para verificar que el tiempo de espera es 5 segundos en modo producción"""
    terminal_prod.demora()
    mock_sleep.assert_called_once_with(5)

def test_mostrar_imprime_en_consola(terminal_dev: Terminal, capsys):
    """Prueba que la función mostrar imprime el mensaje en consola"""
    mensaje = "Mensaje de prueba"
    terminal_dev.mostrar(mensaje)
    captured = capsys.readouterr()
    assert mensaje in captured.out

def test_mostrar_crea_log_y_registra_mensaje(terminal_dev: Terminal, capsys):
    """Prueba que mostrar imprime en consola y registra en el archivo log"""
    mensaje = "Mensaje para log"
    terminal_dev.mostrar(mensaje)
    captured = capsys.readouterr()
    assert mensaje in captured.out

    # Verifica que el archivo log existe y contiene el mensaje
    ruta_log = Terminal._ruta_archivo_log 
    assert ruta_log is not None
    print(f"Ruta del log: {ruta_log}")
    assert Path(ruta_log).exists()
    with open(ruta_log, encoding="utf-8") as f:
        contenido = f.read()
    assert mensaje in contenido