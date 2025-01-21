from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

# Configuración inicial del driver
def setup_driver():
    """
    Configura el WebDriver de Selenium con opciones específicas para mejorar el rendimiento y evitar problemas.

    Opciones configuradas:
    - "--disable-gpu": Deshabilita el uso de GPU para mejorar la compatibilidad.
    - "--no-sandbox": Evita problemas de sandboxing en entornos restringidos.
    - "--start-maximized": Inicia la ventana del navegador maximizada para evitar problemas de resolución.

    Returns:
        WebDriver: Instancia configurada de Selenium WebDriver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")  # Expandir la pantalla completamente
    driver_path = r"C:\\Users\\Maximo Guzman\\Desktop\\Metacritic - Scraper\\chromedriver.exe"  # Ruta del ejecutable de ChromeDriver
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(driver_path), options=options)
    return driver

# Función principal para realizar el scraping de Metacritic
def scrape_metacritic():
    start_time = time.time()  # Registrar el tiempo de inicio de la ejecución

    driver = setup_driver()  # Configurar el WebDriver
    base_url = "https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2025&page={}"

    all_data = []  # Lista para almacenar la información de todos los juegos

    # Iterar a través de las páginas del sitio web (1 a 50 en este caso)
    for page in range(1, 51):
        url = base_url.format(page)  # Construir la URL para la página actual
        print(f"Procesando: {url}")
        driver.get(url)  # Navegar a la URL

        # Esperar hasta que el contenido de los juegos se cargue completamente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-productListings"))
        )

        # Obtener el HTML completo de la página actual
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Encontrar el div principal que contiene la información de los juegos
        section_id = f"detailed|{page}"
        main_div = soup.find("div", {"section": section_id, "class": "c-productListings"})

        # Verificar si el div existe, si no, continuar con la siguiente página
        if not main_div:
            print(f"No se encontró el div especificado en la página {page}.")
            continue

        # Extraer información de cada juego en la página actual
        game_cards = main_div.find_all("div", class_="c-finderProductCard")
        for card in game_cards:
            try:
                # Extraer título del juego
                title = card.find("div", class_="c-finderProductCard_title")
                title = title.get_text(strip=True) if title else "N/A"

                # Extraer fecha de lanzamiento
                release_date = card.find("span", class_="u-text-uppercase")
                release_date = release_date.get_text(strip=True) if release_date else "N/A"

                # Extraer clasificación (rating)
                rating = card.find("span", class_="u-text-capitalize")
                rating = rating.find_next_sibling(string=True).strip() if rating else "N/A"

                # Extraer descripción del juego
                description = card.find("div", class_="c-finderProductCard_description")
                description = description.get_text(strip=True) if description else "N/A"

                # Extraer Metascore
                metascore = card.find("div", class_="c-siteReviewScore")
                metascore = metascore.get_text(strip=True) if metascore else "N/A"

                # Extraer el enlace al detalle del juego
                link = card.find("a", href=True)
                link = f"https://www.metacritic.com{link['href']}" if link else "N/A"

                # Almacenar toda la información del juego en un diccionario
                all_data.append({
                    "Title": title,
                    "Release Date": release_date,
                    "Rating": rating,
                    "Description": description,
                    "Metascore": metascore,
                    "Link": link
                })
            except AttributeError as e:
                print(f"Error al procesar una tarjeta de juego: {e}")

    # Guardar los datos extraídos de los juegos en un archivo CSV
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("metacritic_detailed_games_all_time.csv", index=False)
        print("Datos guardados en 'metacritic_detailed_games_all_time.csv'.")
    else:
        print("No se encontraron datos para guardar.")

    # Llamar a la función para extraer las reseñas de los juegos
    scrape_reviews(all_data, driver)

    # Cerrar el navegador
    driver.quit()

    # Calcular y mostrar el tiempo total de ejecución
    print(f"Tiempo total de ejecución: {time.time() - start_time:.2f} segundos.")

# Función para extraer reseñas de los juegos
def scrape_reviews(games_data, driver):
    reviews_data = []  # Lista para almacenar las reseñas extraídas

    # Iterar sobre cada juego para extraer sus reseñas
    for game in games_data:
        link = game.get("Link")  # Obtener el enlace al detalle del juego
        if link == "N/A":
            continue

        print(f"Extrayendo reseñas de: {link}")
        driver.get(link)  # Navegar al enlace del juego

        # Intentar hacer clic en la pestaña "User Reviews"
        try:
            user_reviews_tab = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "User Reviews"))
            )
            user_reviews_tab.click()
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "c-siteReview_main"))
            )
        except Exception as e:
            print(f"No se pudo acceder a las reseñas para {game['Title']}: {e}")
            continue

        # Extraer reseñas de usuarios con desplazamiento progresivo
        try:
            scroll_pause_time = 2  # Tiempo de espera entre desplazamientos
            last_height = driver.execute_script("return document.body.scrollHeight")

            # Desplazarse hacia abajo hasta que no haya más contenido para cargar
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Analizar el contenido HTML de la página después del desplazamiento
            soup = BeautifulSoup(driver.page_source, "html.parser")
            reviews = soup.find_all("div", class_="c-siteReview_main")

            # Verificar si se encontraron reseñas
            if not reviews:
                print(f"No se encontraron reseñas para el juego '{game['Title']}'.")
                continue

            # Extraer información de cada reseña
            for review in reviews[:1000]:
                try:
                    user = review.find("a", class_="c-siteReviewHeader_username")
                    user = user.get_text(strip=True) if user else "Anonymous"

                    score = review.find("div", class_="c-siteReviewScore")
                    score = score.get_text(strip=True) if score else "N/A"

                    date = review.find("div", class_="c-siteReviewHeader_reviewDate")
                    date = date.get_text(strip=True) if date else "N/A"

                    content = review.find("div", class_="c-siteReview_quote")
                    content = content.get_text(strip=True) if content else "N/A"

                    # Agregar la reseña a la lista de datos
                    reviews_data.append({
                        "Game": game["Title"],
                        "User": user,
                        "Score": score,
                        "Date": date,
                        "Content": content,
                        "Link": link
                    })
                except AttributeError as e:
                    print(f"Error al procesar una reseña: {e}")

        except Exception as e:
            print(f"Error al cargar reseñas para {game['Title']}: {e}")

    # Guardar las reseñas extraídas en un archivo CSV
    if reviews_data:
        pd.DataFrame(reviews_data).to_csv("metacritic_reviews_all_time.csv", index=False)
        print("Datos de reseñas guardados en 'metacritic_reviews_all_time.csv'.")

    if not reviews_data:
        print("No se encontraron datos para guardar.")

# Punto de entrada principal del programa
if __name__ == "__main__":
    scrape_metacritic()
