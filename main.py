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
# Clases Ingredientes

class Ingrediente:
    """Clase base. Representa cualquier ingrediente que puede sostener un chef."""

    def __init__(self, nombre: str, categoria: str, estado: str = "crudo",
                 estacion_requerida: Optional[str] = None, tiempo_preparacion: float = 0,
                 asset_key: Optional[str] = None) -> None:
        """Guarda los datos básicos de un ingrediente."""
        self.nombre = nombre
        self.categoria = categoria
        self.estado = estado
        self.estacion_requerida = estacion_requerida
        self.tiempo_preparacion = tiempo_preparacion
        self.asset_key = asset_key or nombre

    def preparar(self) -> None:
        """Polimorfismo: cada subclase cambia su estado de forma distinta."""
        self.estado = "preparado"

    def esta_listo_para_plato(self) -> bool:
        """Revisa si el ingrediente puede ponerse en un plato."""
        return self.estado in ["listo", "picado", "cocinado", "frito"]

    def esta_arruinado(self) -> bool:
        """Revisa si el ingrediente está quemado."""
        return self.estado == "quemado"

    def clave_receta(self) -> str:
        """Crea el texto usado para comparar recetas."""
        return f"{self.nombre}:{self.estado}"

    def copiar(self) -> "Ingrediente":
        """Crea otra copia igual del ingrediente."""
        return Ingrediente(self.nombre, self.categoria, self.estado,
                           self.estacion_requerida, self.tiempo_preparacion,
                           self.asset_key)

    def __str__(self) -> str:
        """Devuelve el nombre y estado como texto."""
        return f"{self.nombre} ({self.estado})"


class VegetalFruta(Ingrediente):
    """Ingrediente que se prepara en la tabla."""

    def __init__(self, nombre: str, asset_key: Optional[str] = None) -> None:
        """Crea un vegetal o una fruta cruda."""
        super().__init__(nombre, "vegetal_fruta", "crudo", "tabla", 3.0, asset_key)

    def preparar(self) -> None:
        """Deja el ingrediente picado."""
        self.estado = "picado"

    def copiar(self) -> "VegetalFruta":
        """Crea otra copia igual del ingrediente."""
        nuevo = VegetalFruta(self.nombre, self.asset_key)
        nuevo.estado = self.estado
        return nuevo


class PanesYBases(Ingrediente):
    """Ingrediente que ya sale listo de la despensa."""

    def __init__(self, nombre: str, asset_key: Optional[str] = None) -> None:
        """Crea un pan o una base lista."""
        super().__init__(nombre, "pan_base", "listo", None, 0, asset_key)

    def preparar(self) -> None:
        """Mantiene el ingrediente listo."""
        self.estado = "listo"

    def copiar(self) -> "PanesYBases":
        """Crea otra copia igual del ingrediente."""
        nuevo = PanesYBases(self.nombre, self.asset_key)
        nuevo.estado = self.estado
        return nuevo


class Proteina(Ingrediente):
    """Ingrediente que se cocina y puede quemarse."""

    def __init__(self, nombre: str, asset_key: Optional[str] = None) -> None:
        """Crea una proteína cruda."""
        super().__init__(nombre, "proteina", "crudo", "cocina", 5.0, asset_key)

    def preparar(self) -> None:
        """Cocina la proteína."""
        self.estado = "cocinado"

    def quemar(self) -> None:
        """Marca la proteína como quemada."""
        self.estado = "quemado"

    def copiar(self) -> "Proteina":
        """Crea otra copia igual de la proteína."""
        nuevo = Proteina(self.nombre, self.asset_key)
        nuevo.estado = self.estado
        return nuevo


class PapaFreir(Ingrediente):
    """Ingrediente que se prepara en la freidora."""

    def __init__(self, nombre: str = "papas", asset_key: Optional[str] = None) -> None:
        """Crea una papa o alimento para freír."""
        super().__init__(nombre, "papa_freir", "crudo", "freidora", 4.0, asset_key or nombre)

    def preparar(self) -> None:
        """Fríe el ingrediente."""
        self.estado = "frito"

    def quemar(self) -> None:
        """Marca el ingrediente como quemado."""
        self.estado = "quemado"

    def copiar(self) -> "PapaFreir":
        """Crea otra copia igual del ingrediente."""
        nuevo = PapaFreir(self.nombre, self.asset_key)
        nuevo.estado = self.estado
        return nuevo

# Platos

class Plato:
    """Contenedor de ingredientes. El jugador debe llenar un plato y luego entregarlo."""

    def __init__(self, capacidad: int = 6) -> None:
        """Crea un plato vacío con un límite de ingredientes."""
        self.capacidad = capacidad
        self.ingredientes: List[Ingrediente] = []

    def agregar(self, ingrediente: Ingrediente) -> bool:
        """Agrega un ingrediente si todavía hay espacio."""
        if len(self.ingredientes) >= self.capacidad:
            return False
        self.ingredientes.append(ingrediente)
        return True

    def esta_vacio(self) -> bool:
        """Revisa si el plato no tiene ingredientes."""
        return len(self.ingredientes) == 0

    def claves(self) -> List[str]:
        """Devuelve las claves ordenadas de sus ingredientes."""
        return sorted(ingrediente.clave_receta() for ingrediente in self.ingredientes)

    def descripcion(self) -> str:
        """Devuelve una lista simple de lo que contiene."""
        if not self.ingredientes:
            return "plato vacío"
        return ", ".join(f"{i.nombre} {i.estado}" for i in self.ingredientes)

    def __str__(self) -> str:
        """Devuelve el plato como texto."""
        return "Plato: " + self.descripcion()


class Receta:
    """Receta activa que tiene ingredientes, puntos y tiempo máximo."""

    def __init__(self, nombre: str, ingredientes_requeridos: List[str]) -> None:
        """Crea una orden con tiempo y puntos."""
        self.nombre = nombre
        self.ingredientes_requeridos = list(ingredientes_requeridos)
        self.puntos_originales = len(ingredientes_requeridos) * 100
        self.puntos_receta = self.puntos_originales
        self.max_time_receta = 18 + len(ingredientes_requeridos) * 12
        self.tiempo_restante = float(self.max_time_receta)

    def actualizar_tiempo(self, dt: float) -> bool:
        """
        Reduce el tiempo. Cuando llega a cero, baja la puntuación a la mitad.
        Retorna True si la receta debe eliminarse porque llegó a cero puntos.
        """
        self.tiempo_restante -= dt
        if self.tiempo_restante <= 0:
            self.puntos_receta //= 2
            self.tiempo_restante = float(self.max_time_receta)
        return self.puntos_receta <= 0

    def comparar_plato(self, plato: Plato) -> bool:
        """Revisa si un plato cumple esta receta."""
        return plato.claves() == sorted(self.ingredientes_requeridos)

    def texto_ingredientes(self) -> str:
        """Devuelve los ingredientes de la receta como texto."""
        partes = []
        for clave in self.ingredientes_requeridos:
            nombre, estado = clave.split(":")
            partes.append(f"{nombre} {estado}")
        return ", ".join(partes)

    def copiar(self) -> "Receta":
        """Crea una receta nueva con los mismos datos."""
        return Receta(self.nombre, list(self.ingredientes_requeridos))


ItemSostenido = Union[Ingrediente, Plato]


class Game:
    """Demostración de ingredientes, platos y recetas."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Crazy Snack Rush - recetas")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.plato = Plato()
        carne = Proteina("carne", "carne")
        carne.preparar()
        self.plato.agregar(PanesYBases("pan", "pan"))
        self.plato.agregar(carne)
        self.receta = Receta("Hamburguesa simple", ["pan:listo", "carne:cocinado"])

    def ejecutar(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self.screen.fill((245, 240, 225))
            draw_text(self.screen, "Sistema de ingredientes y recetas", 80, 90, 34, BLACK, True)
            draw_text(self.screen, "Receta: " + self.receta.nombre, 80, 160, 26, BLACK, True)
            draw_text(self.screen, "Requiere: " + self.receta.texto_ingredientes(), 80, 210, 22, DARK)
            draw_text(self.screen, "Plato armado: " + self.plato.descripcion(), 80, 270, 22, DARK)
            resultado = "Correcto" if self.receta.comparar_plato(self.plato) else "Incorrecto"
            draw_text(self.screen, "Resultado: " + resultado, 80, 330, 28, GREEN if resultado == "Correcto" else RED, True)
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().ejecutar()
