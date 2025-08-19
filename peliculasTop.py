from selenium import webdriver 
from selenium.webdriver.edge.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
import sys             
import os                                  
from dotenv import load_dotenv                           
load_dotenv()
try:
    servicio_edge = Service(executable_path=r"C:\edgedriver\msedgedriver.exe")
    print(f"Ruta del driver de Edge configurada: {servicio_edge.path}")
except Exception as error:
    print(f"Error al configurar el servicio del driver de Edge: {error}")
    sys.exit(1)

def main():

    navegador = None
    try:
        navegador = webdriver.Edge(service=servicio_edge)
        peliculastop = os.getenv("TOPPELICULAS")
        navegador.get(peliculastop)
        WebDriverWait(navegador, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "smv__verticalSections"))
        )
    except Exception as error:
        print(f"❌ Error al iniciar el navegador: {error}")
    finally:
        if navegador:
            navegador.quit()
            print("✅ Navegador cerrado.")
if __name__ == "__main__":
    main()

