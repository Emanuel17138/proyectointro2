"""
Crazy Snack Rush - Diego Herrera y Emanuel Rojas
Temáticas: McDonald's, Soda El Cachetón y Bar La Nave.

Cómo ejecutar:
    pip install pygame (Python 3.13 e inferiores)
    python main.py

Controles:
    1, 2, 3        escoger escenario
    WASD / Flechas  mover al chef activo
    ESPACIO         interactuar
    TAB             cambiar entre Chef 1 y Chef 2
    Q               botar lo que lleva el chef
    P               pausar
    R               reiniciar escenario
    N               siguiente escenario cuando termina la partida
    ESC             volver al menú / salir

"""

import math
import os
import random
import sys
from typing import Dict, List, Optional, Tuple, Union

try:
    import pygame
except ImportError:
    print("Falta instalar pygame. Use: pip install pygame")
    raise



# Configuración general predeterminada

WIDTH = 1180
HEIGHT = 740
FPS = 60
TILE = 56
GRID_COLS = 14
GRID_ROWS = 10
GRID_X = 24
GRID_Y = 92
UI_X = GRID_X + GRID_COLS * TILE + 24

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DARK = (33, 33, 33)
GRAY = (130, 130, 130)
LIGHT_GRAY = (210, 210, 210)
YELLOW = (246, 211, 101)
GREEN = (82, 166, 93)
RED = (205, 67, 67)
BLUE = (66, 135, 245)
ORANGE = (238, 137, 43)
WALL = (92, 77, 63)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSET_PATHS = {
    "ui": {
        # Pantalla de inicio
        "inicio_fondo": "assets/ui/inicio_fondo.png",
        "inicio_titulo": "assets/ui/inicio_titulo.png",
        "boton_empezar": "assets/ui/boton_empezar.png",
        "boton_salir": "assets/ui/boton_salir.png",
        "boton_about": "assets/ui/boton_about.png",
        # Selección de mapas
        "mapas_fondo": "assets/ui/mapas_fondo.png",
        "mapas_titulo": "assets/ui/mapas_titulo.png",
        "mapa_mcdonalds": "assets/ui/mapa_mcdonalds.png",
        "mapa_cacheton": "assets/ui/mapa_cacheton.png",
        "mapa_nave": "assets/ui/mapa_nave.png",
        # About y elementos compartidos
        "about_fondo": "assets/ui/about_fondo.png",
        "about_titulo": "assets/ui/about_titulo.png",
        "about_panel": "assets/ui/about_panel.png",
        "boton_volver": "assets/ui/boton_volver.png",
        "selector": "assets/ui/selector.png",
    },
    "backgrounds": {
        "mcdonalds": "assets/backgrounds/mcdonalds.png",
        "cacheton": "assets/backgrounds/soda_el_cacheton.png",
        "nave": "assets/backgrounds/bar_la_nave.png",
    },
    "chefs": {
        "chef1_abajo": "assets/chefs/chef1_abajo.png",
        "chef1_arriba": "assets/chefs/chef1_arriba.png",
        "chef1_derecha": "assets/chefs/chef1_derecha.png",
        "chef1_izquierda": "assets/chefs/chef1_izquierda.png",
        "chef2_abajo": "assets/chefs/chef2_abajo.png",
        "chef2_arriba": "assets/chefs/chef2_arriba.png",
        "chef2_derecha": "assets/chefs/chef2_derecha.png",
        "chef2_izquierda": "assets/chefs/chef2_izquierda.png",
    },
    "stations": {
        "despensa": "assets/stations/despensa.png",
        "tabla": "assets/stations/tabla.png",
        "cocina": "assets/stations/cocina.png",
        "freidora": "assets/stations/freidora.png",
        "entrega": "assets/stations/entrega.png",
        "plato": "assets/stations/plato.png",
    },
    "ingredients": {
        "pan": "assets/ingredients/pan.png",
        "carne": "assets/ingredients/carne.png",
        "lechuga": "assets/ingredients/lechuga.png",
        "papas": "assets/ingredients/papas.png",
        "pollo": "assets/ingredients/pollo.png",
        "tomate": "assets/ingredients/tomate.png",
        "arroz": "assets/ingredients/arroz.png",
        "frijoles": "assets/ingredients/frijoles.png",
        "repollo": "assets/ingredients/repollo.png",
        "chicharron": "assets/ingredients/chicharron.png",
        "pico_gallo": "assets/ingredients/pico_gallo.png",
        "platano": "assets/ingredients/platano.png",
        "tortilla": "assets/ingredients/tortilla.png",
        "cebolla": "assets/ingredients/cebolla.png",
        "alitas": "assets/ingredients/alitas.png",
        "salchichon": "assets/ingredients/salchichon.png",
        "queso": "assets/ingredients/queso.png",
    },
}

# Funciones auxiliares, assets

def path_asset(relative_path: str) -> str:
    """Devuelve la ruta completa de una imagen."""
    return os.path.join(BASE_DIR, relative_path)


def load_image(relative_path: str, size: Tuple[int, int]) -> pygame.Surface:
    """Carga una imagen obligatoria. Si falta o no se puede leer, el juego se detiene."""
    full_path = path_asset(relative_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(
            f"Falta una imagen obligatoria: {relative_path}. "
            f"Coloque el archivo en: {full_path}"
        )

    try:
        image = pygame.image.load(full_path).convert_alpha()
    except pygame.error as error:
        raise RuntimeError(
            f"No se pudo cargar la imagen obligatoria: {relative_path}. "
            f"Revise que el archivo exista y sea una imagen válida."
        ) from error

    return pygame.transform.smoothscale(image, size)


def load_selector_image(relative_path: str) -> pygame.Surface:
    """Carga el marco de selección obligatorio."""
    return load_image(relative_path, (256, 96))


def require_asset(assets: Dict[str, pygame.Surface], key: str, group: str) -> pygame.Surface:
    """Devuelve un asset cargado o detiene el juego con un error claro."""
    if key not in assets:
        raise KeyError(f"Falta el asset '{key}' en el grupo '{group}'.")
    return assets[key]


def require_global_asset(group: str, key: str) -> pygame.Surface:
    """Devuelve un asset global cargado o detiene el juego con un error claro."""
    if group not in cocina_assets_actuales:
        raise KeyError(f"No existe el grupo de assets '{group}'.")
    return require_asset(cocina_assets_actuales[group], key, group)


def validar_archivos_assets() -> None:
    """Revisa todos los archivos configurados en ASSET_PATHS antes de iniciar el juego."""
    faltantes: List[str] = []
    for grupo, rutas in ASSET_PATHS.items():
        for nombre, ruta_relativa in rutas.items():
            if not os.path.exists(path_asset(ruta_relativa)):
                faltantes.append(f"- {grupo}/{nombre}: {ruta_relativa}")

    if faltantes:
        detalle = "\n".join(faltantes)
        raise FileNotFoundError(
            "Faltan imágenes obligatorias. El juego no crea imágenes de reemplazo.\n"
            f"{detalle}"
        )


def draw_text(surface: pygame.Surface, text: str, x: int, y: int, size: int = 22,
              color: Tuple[int, int, int] = BLACK, bold: bool = False,
              centered: bool = False) -> pygame.Rect:
    """Dibuja un texto y devuelve el espacio que ocupa."""
    font = pygame.font.SysFont("arial", size, bold=bold)
    rendered = font.render(str(text), True, color)
    rect = rendered.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def draw_wrapped_text(surface: pygame.Surface, text: str, x: int, y: int, max_width: int,
                      size: int = 18, color: Tuple[int, int, int] = BLACK) -> int:
    """Dibuja un texto en varias líneas."""
    font = pygame.font.SysFont("arial", size)
    words = str(text).split(" ")
    line = ""
    current_y = y
    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] > max_width and line:
            rendered = font.render(line.strip(), True, color)
            surface.blit(rendered, (x, current_y))
            current_y += size + 4
            line = word + " "
        else:
            line = test_line
    if line:
        rendered = font.render(line.strip(), True, color)
        surface.blit(rendered, (x, current_y))
        current_y += size + 4
    return current_y


def grid_to_pixel(pos: Tuple[int, int]) -> Tuple[int, int]:
    """Convierte una casilla del mapa a píxeles."""
    col, row = pos
    return GRID_X + col * TILE, GRID_Y + row * TILE


def formato_tiempo(segundos: float) -> str:
    """Convierte segundos al formato minutos y segundos."""
    segundos = max(0, int(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


# Carga centralizada de imágenes (solo commits)
cocina_assets_actuales: Dict[str, Dict[str, pygame.Surface]] = {}


def cargar_assets_juego() -> Dict[str, Dict[str, pygame.Surface]]:
    """Carga todos los assets necesarios. Si falta uno, el juego se detiene."""
    global cocina_assets_actuales
    assets: Dict[str, Dict[str, pygame.Surface]] = {
        "ui": {},
        "backgrounds": {},
        "chefs": {},
        "stations": {},
        "ingredients": {},
    }
    validar_archivos_assets()

    ui_sizes = {
        "inicio_fondo": (WIDTH, HEIGHT),
        "inicio_titulo": (760, 160),
        "boton_empezar": (520, 84),
        "boton_salir": (520, 84),
        "boton_about": (520, 84),
        "mapas_fondo": (WIDTH, HEIGHT),
        "mapas_titulo": (720, 120),
        "mapa_mcdonalds": (790, 96),
        "mapa_cacheton": (790, 96),
        "mapa_nave": (790, 96),
        "about_fondo": (WIDTH, HEIGHT),
        "about_titulo": (640, 120),
        "about_panel": (900, 430),
        "boton_volver": (250, 58),
    }
    for key, size in ui_sizes.items():
        assets["ui"][key] = load_image(ASSET_PATHS["ui"][key], size)
    assets["ui"]["selector"] = load_selector_image(ASSET_PATHS["ui"]["selector"])

    for name, rel_path in ASSET_PATHS["backgrounds"].items():
        assets["backgrounds"][name] = load_image(rel_path, (WIDTH, HEIGHT))

    chef_size = (TILE - 14, TILE - 14)
    for key, rel_path in ASSET_PATHS["chefs"].items():
        assets["chefs"][key] = load_image(rel_path, chef_size)

    for key, rel_path in ASSET_PATHS["stations"].items():
        assets["stations"][key] = load_image(rel_path, (TILE, TILE))

    for key, rel_path in ASSET_PATHS["ingredients"].items():
        assets["ingredients"][key] = load_image(rel_path, (30, 30))

    cocina_assets_actuales = assets
    return assets


class Game:
    """Pantalla inicial usando assets obligatorios."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Crazy Snack Rush - assets obligatorios")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = cargar_assets_juego()

    def ejecutar(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self.screen.blit(self.assets["ui"]["inicio_fondo"], (0, 0))
            self.screen.blit(self.assets["ui"]["inicio_titulo"], ((WIDTH - 760) // 2, 90))
            self.screen.blit(self.assets["ui"]["boton_empezar"], ((WIDTH - 520) // 2, 335))
            draw_text(self.screen, "Carga obligatoria de imágenes activa", WIDTH // 2, 470, 26, WHITE, True, centered=True)
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().ejecutar()
