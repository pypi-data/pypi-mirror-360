import pytest

from src.glgrpa.Sharepoint import Sharepoint

@pytest.fixture
def sharepoint_dev(tmp_path) -> Sharepoint:
    """Fixture para inicializar la clase Sharepoint en modo dev"""
    return Sharepoint(dev=True)

def test_set_usuario_con_diccionario(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se establece correctamente el usuario con un diccionario """
    # Preparación
    usuario = {
        'nombre': 'usuario',
        'clave': 'clave'
    }
    
    # Llamada al método
    sharepoint_dev.set_usuario(usuario)
    
    # Verificación
    assert sharepoint_dev.get_usuario() == usuario
    assert sharepoint_dev.get_usuario("nombre") == "usuario"
    assert sharepoint_dev.get_usuario("clave") == "clave"
    
def test_set_usuario_con_clave(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un usuario con una clave única"""
    # Preparación
    nombre = "usuario"
    clave = "clave"
    
    # Llamada al método
    sharepoint_dev.set_usuario(nombre, clave)
    
    # Verificación
    assert sharepoint_dev.get_usuario("nombre") == nombre
    assert sharepoint_dev.get_usuario("clave") == clave
    
def test_set_usuario_invalido_con_diccionario(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un usuario inválido con un diccionario"""
    # Preparación
    usuario_invalido = {
        "nombre_usuario": "usuario",
        "clave_usuario": "clave"
    }
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="El diccionario no contiene la clave 'nombre_usuario' esperada."):
        sharepoint_dev.set_usuario(usuario_invalido)
        
def test_set_usuario_invalido_con_clave(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un usuario inválido con una clave única"""
    # Preparación
    usuario_invalido = "nombre_usuario"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="La clave no puede ser ``None`` o vacía."):
        sharepoint_dev.set_usuario(usuario_invalido)
        
def test_set_cliente_con_diccionario(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se establece correctamente el cliente con un diccionario """
    # Preparación
    cliente = {
        'nombre': 'cliente',
        'clave': 'clave'
    }
    
    # Llamada al método
    sharepoint_dev.set_cliente(cliente)
    
    # Verificación
    assert sharepoint_dev.get_cliente() == cliente
    assert sharepoint_dev.get_cliente("nombre") == "cliente"
    assert sharepoint_dev.get_cliente("clave") == "clave"
    
def test_set_cliente_con_clave(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un cliente con una clave única"""
    # Preparación
    nombre = "cliente"
    clave = "clave"
    
    # Llamada al método
    sharepoint_dev.set_cliente(nombre, clave)
    
    # Verificación
    assert sharepoint_dev.get_cliente("nombre") == nombre
    assert sharepoint_dev.get_cliente("clave") == clave
    
def test_set_cliente_invalido_con_diccionario(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un cliente inválido con un diccionario"""
    # Preparación
    cliente_invalido = {
        "nombre_cliente": "cliente",
        "clave_cliente": "clave"
    }
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="El diccionario no contiene la clave 'nombre_cliente' esperada."):
        sharepoint_dev.set_cliente(cliente_invalido)
        
def test_set_cliente_invalido_con_clave(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un cliente inválido con una clave única"""
    # Preparación
    cliente_invalido = "nombre_cliente"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="La clave no puede ser ``None`` o vacía."):
        sharepoint_dev.set_cliente(cliente_invalido)
        
def test_set_url(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se establece correctamente la URL """
    # Preparación
    url = "https://example.sharepoint.com/"
    
    # Llamada al método
    sharepoint_dev.set_url(url)
    
    # Verificación
    assert sharepoint_dev.get_url() == url
    
def test_set_url_invalida(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer una URL inválida"""
    # Preparación
    url_invalida = "https://example.com/"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'."):
        sharepoint_dev.set_url(url_invalida)

def test_set_contexto(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se establece correctamente el contexto """
    pass

def test_set_contexto_invalido_vacio(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al establecer un contexto vacío"""
    # Preparación
    contexto_vacio = None
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="El contexto no puede ser ``None``"):
        sharepoint_dev.set_contexto(contexto_vacio)
        
def test_get_url_base(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se obtiene correctamente la URL """
    # Preparación
    url = "https://example.sharepoint.com/sites/nombre"
    url_base = "https://example.sharepoint.com"
    sharepoint_dev.set_url(url)
    
    # Llamada al método y verificación
    assert sharepoint_dev.get_url_base() == url_base
        
def test_get_url_base_con_url(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se obtiene correctamente la URL base """
    # Preparación
    url = "https://example.sharepoint.com/sites/nombre"
    url_base = "https://example.sharepoint.com"
    
    # Llamada al método y verificación
    assert sharepoint_dev.get_url_base(url) == url_base

def test_get_url_base_invalida_sin_url_seteada(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al obtener la URL base sin una URL seteada"""
    # Llamada al método y verificación de la excepción
    with pytest.raises(AttributeError):
        sharepoint_dev.get_url_base()
        
def test_get_url_base_invalida_con_url(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al obtener la URL base con una URL inválida"""
    # Preparación
    url_invalida = "https://example.com/"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'."):
        sharepoint_dev.get_url_base(url_invalida)
        
def test_get_url_sitio(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se obtiene correctamente la URL del sitio """
    # Preparación
    url = "https://example.sharepoint.com/sites/nombre"
    url_sitio = "/sites/nombre"
    sharepoint_dev.set_url(url)
    
    # Llamada al método y verificación
    assert sharepoint_dev.get_url_sitio() == url_sitio
    
def test_get_url_sitio_con_url(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se obtiene correctamente la URL del sitio """
    # Preparación
    url = "https://example.sharepoint.com/sites/nombre"
    url_sitio = "/sites/nombre"
    
    # Llamada al método y verificación
    assert sharepoint_dev.get_url_sitio(url) == url_sitio
    
def test_get_url_sitio_invalida_sin_url_seteada(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al obtener la URL del sitio sin una URL seteada"""
    # Llamada al método y verificación de la excepción
    with pytest.raises(AttributeError):
        sharepoint_dev.get_url_sitio()
        
def test_get_url_sitio_invalida_con_url(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al obtener la URL del sitio con una URL inválida"""
    # Preparación
    url_invalida = "https://example.com/"
    
    # Llamada al método y verificación de la excepción
    with pytest.raises(ValueError, match="La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'."):
        sharepoint_dev.get_url_sitio(url_invalida)
        
def test_obtener_tipo_login(sharepoint_dev: Sharepoint):
    """ Prueba para verificar que se obtiene correctamente el tipo de login """
    # Preparación
    tipo_login = 'user_credentials'
    sharepoint_dev.set_usuario({'nombre': 'usuario', 'clave': 'clave'})
        
    # Llamada al método y verificación
    assert sharepoint_dev.obtener_tipo_login() == tipo_login
    
def test_obtener_tipo_login_invalido(sharepoint_dev: Sharepoint):
    """Prueba para verificar que se lanza una excepción al obtener el tipo de login sin un usuario seteado"""
    # Llamada al método y verificación de la excepción
    with pytest.raises(AttributeError, match="El tipo de autenticación no está definido"):
        sharepoint_dev.obtener_tipo_login()
        
# def test_crear_contexto(sharepoint_dev: Sharepoint):
#     """ Prueba para verificar que se crea correctamente el contexto """
#     # Preparación
#     url = "https://example.sharepoint.com/sites/nombre"
#     sharepoint_dev.set_url(url)
#     
#     # Llamada al método y verificación
#     assert sharepoint_dev.crear_contexto() is not None
#     assert sharepoint_dev.get_contexto() is not None

# def test_crear_contexto_mock(mocker, sharepoint_dev: Sharepoint):
#     """Prueba para verificar que se crea correctamente el contexto usando un mock"""
#     # Preparación
#     mock_contexto = mocker.MagicMock()  # Crear un mock para ClientContext
#     mocker.patch("office365.sharepoint.client_context.ClientContext", return_value=mock_contexto)
#     url = "https://example.sharepoint.com/sites/nombre"
#     sharepoint_dev.set_url(url)
#     
#     # Llamada al método
#     contexto = sharepoint_dev.crear_contexto(url, 'user_credentials')
#     
#     # Verificación
#     assert contexto == mock_contexto  # Verificar que el contexto devuelto es el mock
#     assert sharepoint_dev.get_contexto() == mock_contexto
#     mock_contexto.authenticate.assert_called_once()  # Verificar que el método authenticate fue llamado

pass