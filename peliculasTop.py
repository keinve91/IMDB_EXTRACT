from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar servicio de Edge (ajustá la ruta si cambia)
servicio_edge = Service(executable_path=r"C:\edgedriver_win64\msedgedriver.exe")

def expandir_todo(navegador):
    """Hace clic en todos los botones 'ver más' hasta que no quede ninguno."""
    wait = WebDriverWait(navegador, 10)

    while True:
        try:
            navegador.execute_script("window.scrollBy(0, 200);")
            boton = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.ipc-see-more__button")
            ))
            navegador.execute_script("arguments[0].click();", boton)
            time.sleep(2)

        except TimeoutException:
            print("No hay botones disponibles.")
            break
        except NoSuchElementException:
            print("⚠️ Botón no encontrado, terminando.")
            break

def listarpelis(navegador):
    """Devuelve una lista con los links de todas las películas cargadas hasta ahora."""
    html = navegador.page_source
    sopa = BeautifulSoup(html, "html.parser")
    
    peliculas = []

    # Obtener el límite desde el div que indica "1-150 de 161"
    div_total = sopa.select_one("div.sc-2d056ab8-3.fhbjmI")
    limite = 0
    if div_total:
        texto = div_total.get_text(strip=True)
        if "de " in texto:
            try:
                limite = int(texto.split("de ")[1])
            except ValueError:
                limite = 0

    # Seleccionar todos los <li> dentro de la lista principal hasta el límite
    for li in sopa.select("ul.ipc-metadata-list li")[:limite]:
        enlace = li.select_one("a.ipc-title-link-wrapper")
        if enlace:
            link = "https://www.imdb.com" + enlace.get("href")
            peliculas.append(link)
    
    return peliculas

def verificar_pelicula(navegador, numero):
    """Devuelve la URL de la película #numero si está cargada, o None si no."""
    html = navegador.page_source
    sopa = BeautifulSoup(html, "html.parser")
    
    enlaces = sopa.select("a.ipc-title-link-wrapper")
    for enlace in enlaces:
        href = enlace.get("href")
        if f"ref_=sr_t_{numero}" in href:
            return "https://www.imdb.com" + href
    return None

def main():
    navegador = webdriver.Edge(service=servicio_edge)
    try:
        peliculastop = os.getenv("TOPPELICULAS")
        navegador.get(peliculastop)
        expandir_todo(navegador)
        #numero_buscar = 139
        #url_peli = verificar_pelicula(navegador, numero_buscar)
        #if url_peli:
        #    print(f"✅ La película #{numero_buscar} está cargada: {url_peli}")
        #else:
        #    print(f"❌ La película #{numero_buscar} NO está cargada.")
        peliculas=listarpelis(navegador)
        print(peliculas)
    except Exception as error:
        print(f"❌ Error general: {error}")
    finally:
        navegador.quit()
        print("✅ Navegador cerrado.")



if __name__ == "__main__":
    main()
