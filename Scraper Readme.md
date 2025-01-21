# Descripción del Scraper de Metacritic

Este programa es un scraper desarrollado en Python que utiliza Selenium y BeautifulSoup para extraer información de juegos y reseñas de usuarios desde el sitio web de Metacritic.

## Funcionalidades principales
1. **Extracción de información de juegos:**
   - Títulos de juegos.
   - Fechas de lanzamiento.
   - Clasificaciones (ratings).
   - Descripciones.
   - Puntajes de Metacritic (Metascore).
   - Enlaces a la página de detalles del juego.
   - Los datos se guardan en un archivo CSV llamado `metacritic_detailed_games_all_time.csv`.

2. **Extracción de reseñas de usuarios:**
   - Hasta 1000 reseñas por juego.
   - Nombre de usuario.
   - Puntuación dada por el usuario.
   - Fecha de publicación de la reseña.
   - Contenido de la reseña.
   - Enlaces al juego correspondiente.
   - Los datos se guardan en un archivo CSV llamado `metacritic_reviews_all_time.csv`.

## Paso a paso del scraper
1. **Configuración del WebDriver:**
   - El programa configura un WebDriver de Selenium para interactuar con el navegador.
   - Incluye opciones para maximizar la ventana del navegador, deshabilitar la GPU y evitar problemas en entornos restringidos.

2. **Extracción de la información de juegos:**
   - Navega por varias páginas de Metacritic especificadas por el rango en `range(1, 51)`.
   - Extrae información de cada juego listado en las páginas y la almacena en un diccionario.
   - Guarda la información recopilada en un archivo CSV.

3. **Extracción de reseñas de usuarios:**
   - Para cada juego listado, el programa navega a la página de detalles del juego.
   - Cambia a la pestaña "User Reviews" y desplaza progresivamente la página para cargar todas las reseñas.
   - Extrae información de cada reseña y la almacena en un diccionario.
   - Guarda la información recopilada en un archivo CSV.

## Explicación del código
### Configuración del WebDriver
```python
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
driver_path = r"C:\\Users\\Maximo Guzman\\Desktop\\Metacritic - Scraper\\chromedriver.exe"
driver = webdriver.Chrome(service=webdriver.chrome.service.Service(driver_path), options=options)
```
- Se configura el WebDriver para controlar el navegador Chrome.
- Se especifica la ruta del ejecutable de ChromeDriver.
- Se agregan opciones para mejorar la compatibilidad y rendimiento.

### Extracción de información de juegos
```python
for page in range(1, 51):
    url = base_url.format(page)
    print(f"Procesando: {url}")
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "c-productListings"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    main_div = soup.find("div", {"section": section_id, "class": "c-productListings"})
```
- El programa navega a cada página del rango especificado.
- Utiliza WebDriverWait para asegurarse de que el contenido de los juegos esté completamente cargado.
- Extrae el HTML de la página usando BeautifulSoup y busca el div que contiene la información de los juegos.

### Extracción de reseñas de usuarios
```python
user_reviews_tab = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "User Reviews"))
)
user_reviews_tab.click()
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CLASS_NAME, "c-siteReview_main"))
)
```
- El programa hace clic en la pestaña "User Reviews" para acceder a las reseñas.
- Espera hasta que el contenido de las reseñas esté completamente cargado.

### Desplazamiento progresivo
```python
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
```
- El programa desplaza progresivamente hacia abajo para cargar todas las reseñas dinámicas.
- Si no se detecta un cambio en la altura de la página, el desplazamiento se detiene.

### Guardado de datos
```python
if reviews_data:
    pd.DataFrame(reviews_data).to_csv("metacritic_reviews_all_time.csv", index=False)
    print("Datos de reseñas guardados en 'metacritic_reviews_all_time.csv'.")
```
- Los datos extraídos se guardan en archivos CSV para su análisis posterior.

## Requisitos
- Python 3.7 o superior.
- Selenium.
- BeautifulSoup4.
- ChromeDriver compatible con la versión de Chrome instalada.

## Ejecución
Ejecutar el script desde la terminal:
```bash
python scraper_metacritic.py
```
