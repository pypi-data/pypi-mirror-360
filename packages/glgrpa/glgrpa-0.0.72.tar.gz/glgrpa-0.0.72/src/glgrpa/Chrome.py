# src/Chrome/Chrome.py

# Librerías para el manejo de la consola
from .Terminal import Terminal

# Librerías para el manejo de ventanas
from .Windows import Windows

# Librerías para el manejo de elementos web
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Librerías para el manejo de datos
import pandas as pd
from io import StringIO
import os


class Chrome(Windows, Terminal):
    # Variables de clase para el singleton del driver
    _chrome_options: Options | None = None
    _driver: WebDriver | None = None
        
    def __init__(self, dev:bool=False, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False, driver:WebDriver|None=None):
        super().__init__(dev=dev)
        self.dev = dev
        self.tiempo_demora = 3 if self.dev else 5
        self.reintentos = 3

        self._nuevo_driver = False  # <-- Añadido para saber si se crea un nuevo driver

        if driver is not None:
            Chrome._driver = driver

        if not Chrome._chrome_options:
            self._chrome_options = self.__configuracion_driver(
                mostrar_mensajes_por_consola=mostrar_mensajes_por_consola,
                modo_oculto=modo_oculto,
                modo_minimizado=modo_minimizado
            )
        if not Chrome._driver:
            self._driver = self.obtener_driver()
            self._nuevo_driver = True  # <-- Se creó un nuevo driver
        else:
            self._driver = Chrome._driver

        if self._nuevo_driver:
            self.mostrar("Iniciando navegador Chrome")        
        
    def __configuracion_driver(self, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False) -> Options:
        """ Configuración del driver """
        chrome_options = Options()
        
        if not mostrar_mensajes_por_consola:
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--log-level=3')
        if modo_oculto:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Necesario para Windows
        if modo_minimizado:
            chrome_options.add_argument('--start-minimized')
        else:
            chrome_options.add_argument('--start-maximized')
            
        prefs = {
            "download.default_directory": self.carpeta_descargas_personalizada, # Carpeta de descargas
            "download.prompt_for_download": False, # No preguntar por la descarga
            "download.directory_upgrade": True, # Actualizar automaticamente la carpeta de descargas
            "safebrowsing.enabled": True # Habilitar navegacion segura
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        return chrome_options
        
    def obtener_driver(self) -> WebDriver:
        """ Obtiene el driver de Chrome """
        return self._driver if self._driver else self.__iniciar_driver()
    
    def __iniciar_driver(self) -> WebDriver:
        """ Inicia el driver de Chrome """
        if self._chrome_options is None:
            raise ValueError("Las opciones del driver no están configuradas. Por favor, inicializa el objeto Chrome correctamente.")
        
        self._driver = webdriver.Chrome(service=Service(log_path=os.devnull), options=self._chrome_options)
        self._driver.implicitly_wait(self.tiempo_demora)
        self._driver.set_page_load_timeout(30)  # <-- Cambiado a 30 segundos
        self._driver.set_script_timeout(30)     # <-- Cambiado a 30 segundos
        
        return self._driver
    
    def abrir_navegador(self) -> None:
        """ Abre el navegador """
        self._driver = self.obtener_driver()
        self.mostrar("Navegador abierto")
        
    def cerrar_navegador(self) -> None:
        """ Cierra el navegador """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de cerrarlo.")
        self._driver.quit()
        
        self.demora()
        
        Chrome._driver = None
        Chrome._chrome_options = None
        
        self.fin_ejecucion()
        
    def navegar(self, url:str) -> None:
        """ Navega a la URL """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de navegar.")
        
        try:
            WebDriverWait(self._driver, self.tiempo_demora).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self._driver.get(url)
            self.mostrar(f"Navegando a {url}")
            self.demora()
        except TimeoutException as e:
            self.mostrar(f"No se pudo cargar la página {url} en el tiempo previsto", True)
            self.cerrar_navegador()
            raise e
        except Exception as e:
            self.mostrar(f"Ocurrió un error al navegar a {url}: {e}", True)
            self.cerrar_navegador()
            if "net::ERR_NAME_NOT_RESOLVED" in e.__str__():
                self.mostrar("Parece que hay un problema con la conexión a Internet o el dominio no existe.", True)
                raise ValueError("Dominio no encontrado o conexión a Internet inestable.")
        
    def ScrollToUp(self):
        """ Hace scroll hasta el principio de la página """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de hacer scroll.")
        
        self._driver.execute_script("window.scrollTo(0, 0);")   
        self.demora() 
        
    def esperar_elemento_clickeable(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True, elemento_padre:WebElement|None=None) -> WebElement | None:
        """ Espera a que el elemento sea clickeable, opcionalmente dentro de un elemento padre """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de esperar un elemento clickeable.")
        
        try:
            if elemento_padre:
                elemento = WebDriverWait(elemento_padre, self.tiempo_demora).until(
                    EC.element_to_be_clickable((str(metodo_busqueda), texto_busqueda))
                )
                elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, tiene_que_estar)
            else:
                elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                    EC.element_to_be_clickable((str(metodo_busqueda), texto_busqueda))
                )
                elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda, tiene_que_estar)
        except Exception as e:
            return None
        
        return elemento
    
    def click_elemento(self, metodo_busqueda:By|str, texto_busqueda:str) -> bool:
        """ Clickea el elemento """
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda)
        if not elemento: return False
        
        try:
            self.__desplazar_elemento_a_vista(elemento)
            elemento.click()
            return True
        except ElementClickInterceptedException:
            self.mostrar(f"El elemento {texto_busqueda} está siendo interceptado.")
            return False
        
    def click_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str) -> bool:
        """ Clickea el elemento hijo """
        elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, False)
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda, elemento_padre=elemento_padre)
        if not elemento: return False
        
        try:
            self.__desplazar_elemento_a_vista(elemento)
            elemento.click()
            return True
        except ElementClickInterceptedException:
            self.mostrar(f"El elemento {texto_busqueda} está siendo interceptado.")
            return False
        
    def click_button(self, texto_descripcion:str, metodo_busqueda:By|str, texto_busqueda:str) -> None:
        """ Clickea el botón primero por su texto_descripcion y sino encuentra por el texto_busqueda """
        xpath = f"//button[(text()='{texto_descripcion}' or @value='{texto_descripcion}')]"
        if not self.click_elemento(By.XPATH, xpath):
            if not self.click_elemento(metodo_busqueda, texto_busqueda):
                self.mostrar(f"No se encontró el botón {texto_descripcion} o {texto_busqueda}", True)
                self.cerrar_navegador()
            
    def __desplazar_elemento_a_vista(self, elemento: WebElement) -> None:
        """ Se desplaza la vista hasta el elemento """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de desplazar un elemento a la vista.")
        
        self._driver.execute_script("""arguments[0].scrollIntoView({block: 'center', inline: 'center'});""", elemento)
        self.demora()
        
    def encontrar_elemento(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento y espera a que esté presente """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.visibility_of_element_located((str(metodo_busqueda), texto_busqueda))
            )
            elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_element_located((str(metodo_busqueda), texto_busqueda))
            )
            self.__desplazar_elemento_a_vista(elemento)
        except TimeoutException as e:
            if tiene_que_estar: self.mostrar(f"No se encontró el elemento {texto_busqueda} en el tiempo previsto", True)
            elemento = None
        except Exception as e:
            # if tiene_que_estar: self.mostrar(f"No se encontró el elemento {texto_busqueda} por el metodo {metodo_busqueda}", True)
            elemento = None
        finally:
            return elemento
    
    def encontrar_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento hijo"""
        try:
            elemento = elemento_padre.find_element(str(metodo_busqueda), texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.mostrar(f"No se encontró el elemento {texto_busqueda} con el metodo {metodo_busqueda}", True)
            return None
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"Ocurrió un error al buscar {texto_busqueda}", True)
            return None
        return elemento
    
    def encontrar_elemento_y_elementos(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra al elemento padre desde el metodo y el texto introducido y retorna los elementos hijos cuando estén presentes """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        elemento_padre = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        try:
            if elemento_padre:
                elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*"))
                )
                elementos = elemento_padre.find_elements(By.XPATH, ".//*")
            else:
                elementos = []
            
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos en {texto_busqueda}", True)
            return None
        return elementos 
    
    def encontrar_elementos_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos hijos """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_all_elements_located((str(metodo_busqueda), texto_busqueda))
            )
            elementos = elemento_padre.find_elements(str(metodo_busqueda), texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos   
    
    def encontrar_elementos(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos y espera a que estén presentes """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_all_elements_located((str(metodo_busqueda), texto_busqueda))
            )
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos    
        
    def ingresar_texto(self, metodo_busqueda:By|str, texto_busqueda:str, texto_a_ingresar:str) -> None:
        """ Ingresa texto en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.clear()
            elemento.send_keys(texto_a_ingresar)
            self.demora()
            
    def ingresar_comando(self, comando:str) -> None:
        """ Ingresa un comando en la consola """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de ingresar un comando.")
        
        self._driver.execute_script(comando)
        
    def presionar_enter(self, metodo_busqueda:By|str, texto_busqueda: str) -> None:
        """ Presiona la tecla Enter en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(Keys.ENTER)
            
    def presionar_tecla(self, metodo_busqueda:By|str, texto_busqueda: str, tecla: str) -> None:
        """ Presiona una tecla en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(tecla)     
   
    def seleccionar_opcion_en_desplegable(self, metodo_busqueda:By|str, texto_busqueda: str, nombre_opcion: str, valor_opcion: str|None=None, reintentos: int=0) -> bool:
        """ Selecciona una opción en un desplegable """
        if reintentos >= self.reintentos:
            self.mostrar(f"No se encontró la opción {nombre_opcion} después de varios intentos", True)
            return False

        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if not elemento: 
            self.demora()
            return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        if not isinstance(elemento, WebElement): 
            return False

        desplegable = Select(elemento)

        if valor_opcion: 
            try:
                desplegable.select_by_value(valor_opcion)
                if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                    return True
            except NoSuchElementException as e:
                # self.mostrar(f"No se encontró la opción por su valor {valor_opcion}", True)
                self.demora()
            return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)

        try:
            desplegable.select_by_visible_text(nombre_opcion)
            if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                return True
        except NoSuchElementException as e:
            # self.mostrar(f"No se encontró la opción {nombre_opcion}", True)
            return False

        self.demora()
        return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        
    def __verificar_opcion_seleccionada(self, metodo_busqueda:By|str, texto_busqueda: str, nombre_opcion: str) -> bool:
        """ Verifica que la opción seleccionada sea la correcta """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if not isinstance(elemento, WebElement): return False
        desplegable = Select(elemento)
        return desplegable.first_selected_option.text == nombre_opcion
            
    def valor_en_elemento(self, metodo_busqueda:By|str, texto_busqueda: str) -> str|None:
        """ Obtiene el valor de un elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            return elemento.get_attribute("value")
        return ""
    
    def obtener_texto_elemento(self, metodo_busqueda:By|str, texto_busqueda: str) -> str:
        """ Obtiene el texto de un elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            return elemento.text.strip()
        return ''
   
    def cambiar_ventana(self):
        """ Cambia a la última ventana del navegador """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de cambiar de ventana.")
        
        ventanas = self.esperar_nueva_pestaña(self._driver.window_handles)
        self._driver.switch_to.window(ventanas[-1])
        self.mostrar(f"Cambiando a la ventana {self._driver.title}")
        self.demora()
        
    def esperar_nueva_pestaña(self, ventanas: list[str]) -> list[str]:
        """ Espera a que se abra una nueva pestaña """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de esperar una nueva pestaña.")
        
        WebDriverWait(self._driver, self.tiempo_demora).until(
            EC.new_window_is_opened(ventanas)
        )
        return self._driver.window_handles
    
    def cambiar_directorio_descargas(self):
        """ Cambia el directorio de descargas """
        pass

    def obtener_tabla_en_data_frame(self, metedo_busqueda:By|str, texto_busqueda: str) -> pd.DataFrame| None:
        """ Obtiene una tabla en un DataFrame """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return None
        outer_html = tabla.get_attribute('outerHTML') or ""
        return pd.read_html(StringIO(outer_html))[0] if outer_html else None
    
    def obtener_filas_tabla(self, metedo_busqueda:By|str, texto_busqueda: str) -> list[WebElement]| None:
        """ Obtiene las filas de una tabla """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return []
        self.demora()
        self.__desplazar_elemento_a_vista(tabla)
        return self.encontrar_elementos_desde_elemento(tabla, By.TAG_NAME, "tr")
    
    def obtener_columnas_fila(self, fila: WebElement) -> list[WebElement]| None:
        """ Obtiene las columnas de una fila """
        return self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "th")
    
    def click_boton_en_celda(self, fila: WebElement) -> None:
        """ Clickea un botón en una celda """
        celdas = self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "td")
        if not celdas or len(celdas) == 0: return
        
        for celda in celdas:
            if not self.click_elemento_desde_elemento(celda, By.CLASS_NAME, "fa-print"):
                self.mostrar("No se encontró el botón de descarga", True)
                self.demora()
                
            return
    
    def _obtener_PID_activo(self):
        """Obtiene el PID del proceso de Chrome controlado por Selenium."""
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de obtener el PID.")
        chrome_pid = self._driver.service.process.pid if hasattr(self._driver, "service") else None
        if not chrome_pid:
            raise Exception("No se pudo obtener el PID del proceso de Chrome.")
        return chrome_pid

    def _buscar_proceso_chrome(self, chrome_pid):
        """Busca el proceso hijo que es la ventana real de Chrome."""
        import psutil
        chrome_process = psutil.Process(chrome_pid)
        child_pids = [p.pid for p in chrome_process.children(recursive=True) if "chrome" in p.name().lower()]
        if not child_pids:
            raise Exception("No se encontró el proceso de la ventana de Chrome.")
        return child_pids[0]

    def _set_focus(self, child_pid):
        """Establece el foco en la ventana de Chrome correspondiente al PID dado."""
        from pywinauto import Application
        app = Application(backend="uia").connect(process=child_pid, timeout=5)
        window = app.top_window()
        window.set_focus()
        return window

    def activar_ventana(self):
        """ Trae al frente la ventana de Chrome asociada a esta instancia """
        try:
            chrome_pid = self._obtener_PID_activo()
            child_pid = self._buscar_proceso_chrome(chrome_pid)
            self._set_focus(child_pid)
        except Exception as e:
            self.mostrar(f"No se pudo activar la ventana de Chrome: {e}", True)
            
    def enviar_tecla_ventana(self, *teclas: str):
        """
        Envía una o varias teclas directamente a la ventana de Chrome.
        Ejemplo: enviar_tecla_ventana("F5"), enviar_tecla_ventana("ctrl", "s")
        """
        try:
            from pywinauto import keyboard

            self.activar_ventana()
            # Mapear nombres de teclas especiales a la sintaxis de pywinauto
            special_keys = {
                "F1": "{F1}", "F2": "{F2}", "F3": "{F3}", "F4": "{F4}", "F5": "{F5}", "F6": "{F6}",
                "F7": "{F7}", "F8": "{F8}", "F9": "{F9}", "F10": "{F10}", "F11": "{F11}", "F12": "{F12}",
                "ESC": "{ESC}", "TAB": "{TAB}", "ENTER": "{ENTER}", "DEL": "{DEL}", "DELETE": "{DEL}",
                "INS": "{INSERT}", "INSERT": "{INSERT}", "HOME": "{HOME}", "END": "{END}",
                "PGUP": "{PGUP}", "PGDN": "{PGDN}", "LEFT": "{LEFT}", "RIGHT": "{RIGHT}", "UP": "{UP}", "DOWN": "{DOWN}",
                "CTRL": "^", "CONTROL": "^", "ALT": "%", "SHIFT": "+", "WIN": "{LWIN}"
            }

            def translate_key(key: str):
                k = key.upper()
                return special_keys.get(k, key)

            if len(teclas) == 1:
                # Si es una sola tecla, traducir si es especial
                secuencia = translate_key(teclas[0])
            else:
                # Traducir cada tecla y unir con combinadores
                secuencia = ""
                for t in teclas:
                    tk = translate_key(t)
                    # Si es un modificador (^, +, %) no agregar espacio
                    if tk in ("^", "+", "%"):
                        secuencia += tk
                    else:
                        secuencia += tk
            keyboard.send_keys(secuencia, pause=0.05)
            self.demora()
            
        except Exception as e:
            self.mostrar(f"No se pudo enviar la(s) tecla(s) '{'+'.join(teclas)}' a la ventana de Chrome: {e}", True)
            
    def pegar_portapapeles_en_ventana_activa(self):
        """ Pega el contenido del portapapeles en la ventana activa de Chrome """
        try:
            from pywinauto import keyboard

            self.activar_ventana()
            keyboard.send_keys("^v")  # Ctrl + V para pegar
            self.demora()
            self.mostrar("Contenido del portapapeles pegado en la ventana activa de Chrome")
        except Exception as e:
            self.mostrar(f"No se pudo pegar el contenido del portapapeles: {e}", True)
            
    def buscar_elemento_en_iframes(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> tuple[WebElement | None, str | None]:
        """ Busca un elemento dentro de iframes y devuelve el primer elemento encontrado y su texto """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento en iframes.")
        
        iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar)
        if iframes:
            for iframe in iframes:
                try:
                    self._driver.switch_to.frame(iframe)
                    elementos = self.encontrar_elementos(metodo_busqueda, texto_busqueda, tiene_que_estar)
                    if elementos:
                        texto = elementos[0].text  # Accede al texto antes de salir del iframe
                        self._driver.switch_to.default_content()
                        return elementos[0], texto
                    self._driver.switch_to.default_content()
                except Exception:
                    self._driver.switch_to.default_content()
                    continue
        return None, None