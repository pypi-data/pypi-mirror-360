import pytest
from unittest.mock import patch, MagicMock
from src.glgrpa.Email import Email

@pytest.fixture
def email_dev(tmp_path) -> Email:
    """Fixture para inicializar la clase Email en modo dev"""
    return Email(
        smtp_server='smtp.dev.example.com',
        smtp_port=587,
        smtp_username='usuario',
        smtp_password='contraseña',
        nombre_trabajador_virtual='Trabajador Virtual',
        nombre_aprendizaje='Aprendizaje'
    )
def test_set_configuracion_con_diccionario(email_dev: Email):
    """ Prueba para verificar que se establece correctamente la configuración con un diccionario """
    # Preparación
    configuracion = {
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'smtp_username': '',
        'smtp_password': '',
        'entorno': 'test',
        'nombre_aprendizaje': '',
        'nombre_trabajador_virtual': ''
    }
    
    # Llamada al método
    email_dev.set_configuracion(configuracion)
    
    # Verificación
    assert email_dev.get_configuracion() == configuracion
    assert email_dev.get_configuracion("smtp_server") == "smtp.example.com"
    assert email_dev.get_configuracion("smtp_port") == 587

def test_set_configuracion_con_clave(email_dev: Email):
    """Prueba para verificar que se lanza una excepción al establecer una configuración con una clave única"""
    # Preparación
    smtp_server = "smtp.example.com"
    smtp_port = 587
    
    # Llamada al método
    email_dev.set_configuracion("smtp_server", smtp_server)
    email_dev.set_configuracion("smtp_port", smtp_port)
    
    # Verificación
    assert email_dev.get_configuracion("smtp_server") == smtp_server
    assert email_dev.get_configuracion("smtp_port") == smtp_port
    
def test_set_configuracion_invalida_con_diccionario(email_dev: Email):
    """Prueba para verificar que se lanza una excepción al establecer una configuración inválida con un diccionario"""
    # Preparación
    configuracion_invalida = {
        "servidor": "smtp.example.com",
        "puerto": 587,
        "nombre_usuario": "",
        "clave_usuario": ""
    }
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(KeyError, match="La clave 'servidor' no es válida en la configuración."):
        email_dev.set_configuracion(configuracion_invalida)

def test_set_configuracion_invalida_con_clave(email_dev: Email):
    """Prueba para verificar que se lanza una excepción al establecer una configuración inválida con una clave única"""
    # Preparación
    configuracion_invalida = "servidor"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(KeyError, match="La clave 'servidor' no es válida en la configuración."):
        email_dev.set_configuracion(configuracion_invalida, "smtp.example.com")

@patch("smtplib.SMTP")
def test_enviar_email(mock_smtp, email_dev: Email):
    """Prueba para verificar que se envía un correo electrónico correctamente usando mocks"""
    # Preparación
    email_dev.set_configuracion({
        'smtp_server': 'smtp.mockserver.com',
        'smtp_port': 587,
        'smtp_username': 'mockuser@example.com',
        'smtp_password': 'mockpassword'
    })
    destinatario = ["recipient@example.com"]
    asunto = "Asunto de prueba"
    adjunto = None

    # Mock del servidor SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Llamada al método
    resultado = email_dev.enviar_email(destinatario, asunto)

    # Verificación
    assert resultado is True
    mock_smtp.assert_called_once_with('smtp.mockserver.com', 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with('mockuser@example.com', 'mockpassword')
    mock_server.send_message.assert_called_once()

@patch("smtplib.SMTP")
def test_enviar_email_invalido(mock_smtp, email_dev: Email):
    """Prueba para verificar que se lanza una excepción al enviar un correo electrónico con una configuración inválida"""
    # Preparación
    email_dev.set_configuracion({
        'smtp_server': 'smtp.mockserver.com',
        'smtp_port': 587,
        'smtp_username': 'mockuser@example.com',
        'smtp_password': 'mockpassword'
    })
    destinatario = ["recipient@example.com"]
    asunto = "Asunto de prueba"
    adjunto = None

    # Mock del servidor SMTP que lanza una excepción
    mock_server = MagicMock()
    mock_server.send_message.side_effect = Exception("Error al enviar correo.")
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Llamada al método y verificación de la excepción
    with pytest.raises(Exception, match="Error al enviar correo."):
        email_dev.enviar_email(destinatario, asunto)