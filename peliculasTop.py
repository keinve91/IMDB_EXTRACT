from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import os
from dotenv import load_dotenv


load_dotenv()
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
    html = navegador.page_source
    sopa = BeautifulSoup(html, "html.parser")
    peliculas = []
    div_total = sopa.select_one("div.sc-2d056ab8-3.fhbjmI")
    limite = 0
    if div_total:
        texto = div_total.get_text(strip=True)
        if "de " in texto:
            try:
                limite = int(texto.split("de ")[1])
            except ValueError:
                limite = 0

    for li in sopa.select("ul.ipc-metadata-list li")[:limite]:
        enlace = li.select_one("a.ipc-title-link-wrapper")
        if enlace:
            link = "https://www.imdb.com" + enlace.get("href")
            peliculas.append(link)    
    return peliculas
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time

def extraer_peliculas(navegador, link):
    navegador.get(link)
    time.sleep(2)
    html = navegador.page_source
    sopa = BeautifulSoup(html, "html.parser")
    datos = {}
        titulo = sopa.find("h1", {"data-testid": "hero__pageTitle"})
    datos["pelicula"] = titulo.get_text(strip=True) if titulo else None
        datos["link"] = link
        poster = sopa.find("a", {"aria-label": lambda v: v and "póster" in v.lower()})
    if poster and poster.get("href"):
        datos["imagen_poster"] = "https://www.imdb.com" + poster["href"]
    else:
        datos["imagen_poster"] = None
        año = sopa.find("a", href=lambda v: v and "releaseinfo" in v)
    datos["año"] = año.get_text(strip=True) if año else None
        categorias_block = sopa.find("div", {"data-testid": "interests"})
    if categorias_block:
        chips = categorias_block.select(".ipc-chip__text")
        datos["categorias"] = [c.get_text(strip=True) for c in chips]
    else:
        datos["categorias"] = []
        plot = sopa.find("p", {"data-testid": "plot"})
    if plot:
        span_xl = plot.find("span", {"data-testid": "plot-xl"})
        span_l = plot.find("span", {"data-testid": "plot-l"})
        span_short = plot.find("span", {"data-testid": "plot-xs_to_m"})
        if span_xl:
            datos["sinopsis"] = span_xl.get_text(strip=True)
        elif span_l:
            datos["sinopsis"] = span_l.get_text(strip=True)
        elif span_short:
            datos["sinopsis"] = span_short.get_text(strip=True)
        else:
            datos["sinopsis"] = None
    else:
        datos["sinopsis"] = None
        rating = sopa.find("span", {"class": "sc-4dc495c1-1"})
    datos["rating"] = rating.get_text(strip=True) if rating else None
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["imdb"]
    coleccion = db["peliculas"]
    
    resultado = coleccion.insert_one(datos)
    print("Insertado en MongoDB con ID:", resultado.inserted_id)

    return datos
def verificar_pelicula(navegador, numero):
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
        print(f"🔎 Se encontraron {len(peliculas)} películas")
        for i, link in enumerate(peliculas, start=1):
            print(f"\n▶ Procesando película #{i}")
            pelicula_info = extraer_peliculas(navegador, link)
            print(pelicula_info)
    except Exception as error:
        print(f"❌ Error general: {error}")
    finally:
        navegador.quit()
        print("✅ Navegador cerrado.")


if __name__ == "__main__":
    main()
