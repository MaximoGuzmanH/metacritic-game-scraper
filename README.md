# metacritic-game-scraper
Scraper en Python para extraer datos de juegos y reseñas de Metacritic utilizando Selenium y BeautifulSoup. Recopila títulos, fechas de lanzamiento, calificaciones, descripciones, Metascores y hasta 1000 reseñas de usuarios por juego. Los datos se almacenan en archivos CSV para análisis posterior.

Scraper de Juegos en Metacritic
Un scraper basado en Python que utiliza Selenium y BeautifulSoup para extraer detalles de juegos y reseñas de usuarios desde Metacritic.

Este programa permite:
Extraer títulos de juegos, fechas de lanzamiento, clasificaciones, descripciones y puntajes de Metascore.
Obtener hasta 1000 reseñas de usuarios por juego, incluyendo nombre de usuario, puntajes, fechas y contenido de las reseñas.

Características:
Desplazamiento progresivo para cargar todas las reseñas de usuarios.
Manejo de contenido dinámico y navegación hacia la pestaña "User Reviews".
Guarda los datos en archivos CSV separados para análisis posterior.

Requisitos:
Python 3.7 o superior
Selenium WebDriver
BeautifulSoup4
ChromeDriver
