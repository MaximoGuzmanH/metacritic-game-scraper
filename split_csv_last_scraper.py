from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import pandas as pd

# Configuración inicial del driver
def setup_driver():
    """
    Configura el WebDriver de Selenium con opciones específicas para mejorar el rendimiento y evitar problemas.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    driver_path = r"C:\\Users\\Maximo Guzman\\Desktop\\Metacritic - Scraper\\chromedriver.exe"
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(driver_path), options=options)
    return driver

# Función para dividir y guardar la data en archivos CSV de máximo 20MB
def save_to_csv(filename, data):
    """
    Guarda los datos en archivos CSV de máximo 20 MB cada uno.
    """
    max_size = 20 * 1024 * 1024  # 20MB en bytes
    file_count = 1
    chunk_size = 10000  # Cantidad de filas por bloque (ajustable)
    
    df = pd.DataFrame(data)

    while True:
        file_path = f"{filename}_{file_count}.csv"
        df_chunk = df.iloc[(file_count - 1) * chunk_size : file_count * chunk_size]

        if df_chunk.empty:
            break

        df_chunk.to_csv(file_path, index=False, encoding="utf-8")

        # Si el archivo supera los 20MB, reducimos el chunk size para los siguientes archivos
        if os.path.getsize(file_path) > max_size:
            chunk_size = int(chunk_size * 0.8)

        file_count += 1

    print(f"Datos guardados en {file_count - 1} archivo(s) '{filename}_*.csv'.")

# Función principal para realizar el scraping de Metacritic
def scrape_metacritic():
    start_time = time.time()
    driver = setup_driver()
    base_url = "https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2025&page={}"

    all_data = []  # Lista para almacenar la información de los juegos

    # Iterar a través de 50 páginas del sitio web
    for page in range(1, 51):
        url = base_url.format(page)
        print(f"Procesando: {url}")
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-productListings"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        section_id = f"detailed|{page}"
        main_div = soup.find("div", {"section": section_id, "class": "c-productListings"})

        if not main_div:
            print(f"No se encontró el div especificado en la página {page}.")
            continue

        game_cards = main_div.find_all("div", class_="c-finderProductCard")
        for card in game_cards:
            try:
                title = card.find("div", class_="c-finderProductCard_title")
                title = title.get_text(strip=True) if title else "N/A"

                release_date = card.find("span", class_="u-text-uppercase")
                release_date = release_date.get_text(strip=True) if release_date else "N/A"

                rating = card.find("span", class_="u-text-capitalize")
                rating = rating.find_next_sibling(string=True).strip() if rating else "N/A"

                description = card.find("div", class_="c-finderProductCard_description")
                description = description.get_text(strip=True) if description else "N/A"

                metascore = card.find("div", class_="c-siteReviewScore")
                metascore = metascore.get_text(strip=True) if metascore else "N/A"

                link = card.find("a", href=True)
                link = f"https://www.metacritic.com{link['href']}" if link else "N/A"

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

    # Guardar la lista de juegos en archivos CSV
    if all_data:
        save_to_csv("metacritic_detailed_games_all_time", all_data)
    else:
        print("No se encontraron datos para guardar.")

    # Scraping de reseñas
    scrape_reviews(all_data, driver)

    driver.quit()
    print(f"Tiempo total de ejecución: {time.time() - start_time:.2f} segundos.")

# Función para extraer reseñas de los juegos
def scrape_reviews(games_data, driver):
    reviews_data = []

    for game in games_data:
        link = game.get("Link")
        if link == "N/A":
            continue

        print(f"Extrayendo reseñas de: {link}")
        driver.get(link)

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

        try:
            scroll_pause_time = 2
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")
            reviews = soup.find_all("div", class_="c-siteReview_main")

            if not reviews:
                print(f"No se encontraron reseñas para el juego '{game['Title']}'.")
                continue

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

    # Guardar las reseñas en archivos CSV
    if reviews_data:
        save_to_csv("metacritic_reviews_all_time", reviews_data)
    else:
        print("No se encontraron datos para guardar.")

if __name__ == "__main__":
    scrape_metacritic()
