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

# Estaciones

class Estacion:
    """Clase base para todas las estaciones."""

    def __init__(self, nombre: str, tipo: str, posicion: Tuple[int, int]) -> None:
        """Crea una estación en una casilla."""
        self.nombre = nombre
        self.tipo = tipo
        self.posicion = posicion
        self.ingredientes_aceptados: List[str] = []

    def interactuar(self, cocina: "Cocina", chef: "Chef") -> str:
        """Responde cuando un chef usa la estación."""
        return "No se puede usar esta estación."

    def actualizar(self, dt: float) -> None:
        """Actualiza la estación con el paso del tiempo."""
        pass

    def dibujar(self, surface: pygame.Surface, assets: Dict[str, pygame.Surface]) -> None:
        """Dibuja la estación sin poner texto encima."""
        x, y = grid_to_pixel(self.posicion)
        surface.blit(require_asset(assets, self.tipo, "stations"), (x, y))


class Despensa(Estacion):
    """Entrega ingredientes infinitos, uno a la vez."""

    def __init__(self, ingrediente_base: Ingrediente, posicion: Tuple[int, int]) -> None:
        """Crea una despensa para un ingrediente."""
        super().__init__(f"Desp. {ingrediente_base.nombre}", "despensa", posicion)
        self.ingrediente_base = ingrediente_base

    def interactuar(self, cocina: "Cocina", chef: "Chef") -> str:
        """Entrega un ingrediente si el chef tiene la mano vacía."""
        if chef.sosteniendo is not None:
            return "Ya tiene algo en la mano."
        chef.sosteniendo = self.ingrediente_base.copiar()
        return f"Tomó {chef.sosteniendo.nombre}."

    def dibujar(self, surface: pygame.Surface, assets: Dict[str, pygame.Surface]) -> None:
        """Dibuja la despensa y el ingrediente que entrega."""
        super().dibujar(surface, assets)
        x, y = grid_to_pixel(self.posicion)
        icon = require_global_asset("ingredients", self.ingrediente_base.asset_key)
        surface.blit(icon, (x + 13, y + 7))


class EstacionTrabajo(Estacion):
    """Tabla, cocina o freidora. Procesa ingredientes con tiempo."""

    def __init__(self, nombre: str, tipo: str, posicion: Tuple[int, int], aceptados: List[str],
                 permite_quemarse: bool = False, tiempo_para_quemarse: float = 7.0) -> None:
        """Crea una estación que prepara ingredientes."""
        super().__init__(nombre, tipo, posicion)
        self.ingredientes_aceptados = aceptados
        self.ingrediente: Optional[Ingrediente] = None
        self.progreso = 0.0
        self.procesando = False
        self.terminado = False
        self.permite_quemarse = permite_quemarse
        self.tiempo_para_quemarse = tiempo_para_quemarse
        self.tiempo_despues_de_listo = 0.0

    def interactuar(self, cocina: "Cocina", chef: "Chef") -> str:
        """Coloca o recoge un ingrediente de la estación."""
        if self.ingrediente is None:
            if chef.sosteniendo is None:
                return "La estación está vacía."
            if isinstance(chef.sosteniendo, Plato):
                return "Aquí solo se preparan ingredientes, no platos."
            if chef.sosteniendo.esta_listo_para_plato():
                return f"{chef.sosteniendo.nombre} ya está listo. Póngalo en un plato."
            if chef.sosteniendo.categoria not in self.ingredientes_aceptados:
                return f"{chef.sosteniendo.nombre} no sirve para {self.nombre}."
            if chef.sosteniendo.estacion_requerida != self.tipo:
                return f"{chef.sosteniendo.nombre} no ocupa esta estación."
            self.ingrediente = chef.sosteniendo
            chef.sosteniendo = None
            self.progreso = 0.0
            self.procesando = True
            self.terminado = False
            self.tiempo_despues_de_listo = 0.0
            return f"Preparando {self.ingrediente.nombre}."

        if chef.sosteniendo is None:
            if not self.terminado:
                return "Todavía se está preparando."
            chef.sosteniendo = self.ingrediente
            nombre = chef.sosteniendo.nombre
            self.ingrediente = None
            self.progreso = 0.0
            self.procesando = False
            self.terminado = False
            self.tiempo_despues_de_listo = 0.0
            return f"Recogió {nombre}."

        return "Tiene que tener la mano vacía para recoger."

    def actualizar(self, dt: float) -> None:
        """Avanza la preparación y quema si tarda demasiado."""
        if self.ingrediente is None:
            return

        if self.procesando and not self.terminado:
            self.progreso += dt
            if self.progreso >= self.ingrediente.tiempo_preparacion:
                self.ingrediente.preparar()
                self.procesando = False
                self.terminado = True
                self.tiempo_despues_de_listo = 0.0
                return

        if self.terminado and self.permite_quemarse and not self.ingrediente.esta_arruinado():
            self.tiempo_despues_de_listo += dt
            if self.tiempo_despues_de_listo >= self.tiempo_para_quemarse:
                if hasattr(self.ingrediente, "quemar"):
                    self.ingrediente.quemar()
                self.terminado = True

    def dibujar(self, surface: pygame.Surface, assets: Dict[str, pygame.Surface]) -> None:
        """Dibuja la estación, el ingrediente y su avance."""
        super().dibujar(surface, assets)
        x, y = grid_to_pixel(self.posicion)
        if self.ingrediente:
            icon = require_global_asset("ingredients", self.ingrediente.asset_key)
            surface.blit(icon, (x + 13, y + 7))

            if not self.terminado:
                ratio = min(1.0, self.progreso / max(0.01, self.ingrediente.tiempo_preparacion))
                pygame.draw.rect(surface, BLACK, (x + 5, y + 5, TILE - 10, 7), 1)
                pygame.draw.rect(surface, GREEN, (x + 6, y + 6, int((TILE - 12) * ratio), 5))
            else:
                color = RED if self.ingrediente.estado == "quemado" else GREEN
                pygame.draw.circle(surface, color, (x + TILE - 8, y + 8), 6)


class EstacionPlato(Estacion):
    """Mesa con plato. Aquí se ponen ingredientes preparados antes de entregarlos."""

    def __init__(self, posicion: Tuple[int, int], capacidad: int = 6) -> None:
        """Crea una mesa con un plato vacío."""
        super().__init__("Plato", "plato", posicion)
        self.plato = Plato(capacidad)

    def interactuar(self, cocina: "Cocina", chef: "Chef") -> str:
        """Permite poner ingredientes o recoger el plato."""
        if chef.sosteniendo is None:
            if self.plato.esta_vacio():
                return "Plato vacío. Ponga ingredientes preparados aquí."
            chef.sosteniendo = self.plato
            self.plato = Plato(self.plato.capacidad)
            return "Tomó el plato armado. Llévelo a Entrega."

        if isinstance(chef.sosteniendo, Ingrediente):
            ingrediente = chef.sosteniendo
            if ingrediente.esta_arruinado():
                chef.sosteniendo = None
                return "Ingrediente quemado descartado."
            if not ingrediente.esta_listo_para_plato():
                return "Ese ingrediente todavía no está preparado."
            if not self.plato.agregar(ingrediente):
                return "El plato está lleno."
            chef.sosteniendo = None
            return f"Puso {ingrediente.nombre} en el plato."

        if isinstance(chef.sosteniendo, Plato):
            if not self.plato.esta_vacio():
                return "Ya hay un plato con ingredientes aquí."
            self.plato = chef.sosteniendo
            chef.sosteniendo = None
            return "Dejó el plato en la mesa."

        return "No se pudo usar el plato."

    def dibujar(self, surface: pygame.Surface, assets: Dict[str, pygame.Surface]) -> None:
        """Dibuja la mesa y el plato."""
        super().dibujar(surface, assets)
        x, y = grid_to_pixel(self.posicion)
        dibujar_plato(surface, self.plato, x + 6, y + 6, 44)


class EstacionEntrega(Estacion):
    """Recibe platos completos y los compara con las recetas activas."""

    def __init__(self, posicion: Tuple[int, int]) -> None:
        """Crea la estación donde se entregan los platos."""
        super().__init__("Entrega", "entrega", posicion)

    def interactuar(self, cocina: "Cocina", chef: "Chef") -> str:
        """Compara el plato con las órdenes y suma puntos."""
        if chef.sosteniendo is None:
            return "Debe traer un plato armado."
        if isinstance(chef.sosteniendo, Ingrediente):
            return "Ahora la entrega solo acepta platos, no ingredientes sueltos."

        plato = chef.sosteniendo
        if plato.esta_vacio():
            return "No entregue un plato vacío."

        for receta in list(cocina.ordenes):
            if receta.comparar_plato(plato):
                cocina.puntos = max(0, cocina.puntos + receta.puntos_receta)
                cocina.ordenes.remove(receta)
                chef.sosteniendo = None
                cocina.agregar_mensaje("+" + str(receta.puntos_receta), GREEN)
                return f"Entregó {receta.nombre}. +{receta.puntos_receta} puntos."

        chef.sosteniendo = None
        cocina.puntos = max(0, cocina.puntos - 50)
        cocina.agregar_mensaje("-50", RED)
        return "Plato incorrecto. -50 puntos."


# Variable global para que las estaciones dibujen iconos

cocina_assets_actuales: Dict[str, Dict[str, pygame.Surface]] = {}


def dibujar_plato(surface: pygame.Surface, plato: Plato, x: int, y: int, size: int) -> None:
    """Dibuja un plato y sus ingredientes."""
    pygame.draw.ellipse(surface, (250, 250, 245), (x, y, size, size))
    pygame.draw.ellipse(surface, (120, 120, 120), (x, y, size, size), 2)
    pygame.draw.ellipse(surface, (220, 220, 215), (x + 7, y + 7, size - 14, size - 14), 1)

    for idx, ingrediente in enumerate(plato.ingredientes[:6]):
        icon = require_global_asset("ingredients", ingrediente.asset_key)
        px = x + 5 + (idx % 3) * 12
        py = y + 9 + (idx // 3) * 13
        mini = pygame.transform.smoothscale(icon, (15, 15))
        surface.blit(mini, (px, py))

# Jugador

class Chef:
    """Chef controlable. Solo puede sostener un ingrediente o un plato a la vez."""

    VEL = 200

    def __init__(self, nombre: str, posicion: Tuple[int, int], asset_key: str) -> None:
        """Crea un chef en una casilla del mapa."""
        self.nombre = nombre
        self.asset_key = asset_key
        self.sosteniendo: Optional[ItemSostenido] = None
        self.direccion = (0, 1)
        self.ancho = TILE - 14
        self.alto = TILE - 14
        col, row = posicion
        self.x = float(col * TILE + (TILE - self.ancho) / 2)
        self.y = float(row * TILE + (TILE - self.alto) / 2)

    def rect(self) -> pygame.Rect:
        """Devuelve el rectángulo usado para choques."""
        return pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)

    def centro(self) -> Tuple[float, float]:
        """Devuelve el centro del chef."""
        return self.x + self.ancho / 2, self.y + self.alto / 2

    def celda_actual(self) -> Tuple[int, int]:
        """Devuelve la casilla donde está el chef."""
        centro_x, centro_y = self.centro()
        return int(centro_x // TILE), int(centro_y // TILE)

    def posicion_frente(self) -> Tuple[int, int]:
        """Devuelve la casilla que está frente al chef."""
        col, row = self.celda_actual()
        return col + self.direccion[0], row + self.direccion[1]

    def interactuar(self, cocina: "Cocina") -> str:
        """Usa la estación que está frente al chef."""
        estacion = cocina.obtener_estacion_en(self.posicion_frente())
        if estacion is None:
            return "No hay estación enfrente."
        return estacion.interactuar(cocina, self)

    def descartar(self) -> str:
        """Bota lo que el chef tiene en la mano."""
        if self.sosteniendo is None:
            return "No lleva nada."
        self.sosteniendo = None
        return "Descartó lo que llevaba."

    def texto_mano(self) -> str:
        """Devuelve un texto con lo que lleva el chef."""
        if self.sosteniendo is None:
            return "vacía"
        if isinstance(self.sosteniendo, Plato):
            return self.sosteniendo.descripcion()
        return str(self.sosteniendo)

    def dibujar(self, surface: pygame.Surface, assets: Dict[str, pygame.Surface], activo: bool) -> None:
        """Dibuja al chef con el sprite de su dirección."""
        x = GRID_X + int(self.x)
        y = GRID_Y + int(self.y)
        if activo:
            pygame.draw.ellipse(surface, YELLOW, (x - 4, y + self.alto - 8, self.ancho + 8, 12))
        nombres_direccion = {
            (0, 1): "abajo",
            (0, -1): "arriba",
            (1, 0): "derecha",
            (-1, 0): "izquierda",
        }
        direccion = nombres_direccion.get(self.direccion, "abajo")
        surface.blit(assets[f"{self.asset_key}_{direccion}"], (x, y))
        if activo:
            pygame.draw.rect(surface, YELLOW, (x, y, self.ancho, self.alto), 3, border_radius=6)
        if self.sosteniendo:
            if isinstance(self.sosteniendo, Plato):
                dibujar_plato(surface, self.sosteniendo, x + self.ancho - 24, y - 8, 30)
            else:
                icon = require_global_asset("ingredients", self.sosteniendo.asset_key)
                mini = pygame.transform.smoothscale(icon, (28, 28))
                surface.blit(mini, (x + self.ancho - 22, y - 9))


 
# Cocina

class Cocina:
    """Administra chefs, estaciones, recetas, tiempo, layout y puntos."""

    def __init__(self, definicion: Dict) -> None:
        """Crea una partida usando los datos de un restaurante."""
        self.nombre = definicion["nombre"]
        self.tema = definicion["tema"]
        self.background_key = definicion["fondo"]
        self.tiempo_total = int(definicion["tiempo"])
        self.tiempo_restante = float(self.tiempo_total)
        self.recetas_base = [Receta(nombre, ingredientes) for nombre, ingredientes in definicion["recetas"]]
        self.max_ordenes = definicion.get("max_ordenes", 3)
        self.spawn_interval = float(definicion.get("intervalo", 8.0))
        self.spawn_timer = 0.0
        self.chefs: List[Chef] = []
        self.estaciones: List[Estacion] = []
        self.ordenes: List[Receta] = []
        self.paredes = set()
        self.puntos = 0
        self.mensaje = "Tome ingredientes, prepárelos, póngalos en un plato y entréguelo."
        self.juego_terminado = False
        self.mensajes_flotantes: List[Dict] = []
        self._construir_desde_layout(definicion["layout"], definicion["despensas"])
        self.ordenes.append(self.generar_receta())

    def _construir_desde_layout(self, layout: List[str], despensas: Dict[str, Ingrediente]) -> None:
        """Crea paredes, estaciones y chefs leyendo el mapa."""
        posiciones_chef: List[Tuple[int, int]] = []
        for row, line in enumerate(layout):
            if len(line) != GRID_COLS:
                raise ValueError(f"El layout de {self.nombre} tiene una fila con largo incorrecto: {line}")
            for col, ch in enumerate(line):
                pos = (col, row)
                if ch == "#":
                    self.paredes.add(pos)
                elif ch == "S":
                    self.estaciones.append(EstacionTrabajo("Cocina", "cocina", pos, ["proteina"], True, 7.0))
                elif ch == "T":
                    self.estaciones.append(EstacionTrabajo("Tabla", "tabla", pos, ["vegetal_fruta"], False))
                elif ch == "F":
                    self.estaciones.append(EstacionTrabajo("Freidora", "freidora", pos, ["papa_freir"], True, 7.0))
                elif ch == "E":
                    self.estaciones.append(EstacionEntrega(pos))
                elif ch == "P":
                    self.estaciones.append(EstacionPlato(pos))
                elif ch in ("1", "2"):
                    posiciones_chef.append(pos)
                elif ch in despensas:
                    self.estaciones.append(Despensa(despensas[ch], pos))
                elif ch == ".":
                    pass
                else:
                    raise ValueError(f"Símbolo desconocido en layout: {ch}")

        if len(posiciones_chef) < 2:
            posiciones_chef = [(2, 8), (4, 8)]
        self.chefs = [
            Chef("Chef 1", posiciones_chef[0], "chef1"),
            Chef("Chef 2", posiciones_chef[1], "chef2"),
        ]

    def generar_receta(self) -> Receta:
        """Escoge una receta al azar y crea una copia."""
        return random.choice(self.recetas_base).copiar()

    def actualizar(self, dt: float) -> None:
        """Actualiza el tiempo, estaciones, órdenes y mensajes."""
        if self.juego_terminado:
            return

        self.tiempo_restante -= dt
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            self.juego_terminado = True
            self.mensaje = "Tiempo terminado."
            return

        for estacion in self.estaciones:
            estacion.actualizar(dt)

        for receta in list(self.ordenes):
            debe_eliminarse = receta.actualizar_tiempo(dt)
            if debe_eliminarse:
                self.ordenes.remove(receta)
                self.puntos = max(0, self.puntos - receta.puntos_originales)
                self.mensaje = f"Orden perdida: {receta.nombre}. -{receta.puntos_originales}."
                self.agregar_mensaje("-" + str(receta.puntos_originales), RED)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if len(self.ordenes) < self.max_ordenes:
                self.ordenes.append(self.generar_receta())

        while len(self.ordenes) == 0:
            self.ordenes.append(self.generar_receta())

        for mensaje in self.mensajes_flotantes:
            mensaje["t"] -= dt
            mensaje["y"] -= 28 * dt
        self.mensajes_flotantes = [m for m in self.mensajes_flotantes if m["t"] > 0]

    def mover(self, chef: Chef, vx: float, vy: float) -> None:
        """Movimiento continuo con colisiones, igual al proyecto de referencia."""
        chef.x += vx
        if self._colisiona(chef.rect(), chef):
            chef.x -= vx

        chef.y += vy
        if self._colisiona(chef.rect(), chef):
            chef.y -= vy

        max_x = GRID_COLS * TILE - chef.ancho
        max_y = GRID_ROWS * TILE - chef.alto
        chef.x = max(0.0, min(chef.x, max_x))
        chef.y = max(0.0, min(chef.y, max_y))

    def _colisiona(self, rect: pygame.Rect, chef_actual: Chef) -> bool:
        """Revisa si el chef toca una pared, estación u otro chef."""
        posiciones_bloqueadas = set(self.paredes)
        posiciones_bloqueadas.update(estacion.posicion for estacion in self.estaciones)
        for col, row in posiciones_bloqueadas:
            if rect.colliderect(pygame.Rect(col * TILE, row * TILE, TILE, TILE)):
                return True

        for chef in self.chefs:
            if chef is not chef_actual and rect.colliderect(chef.rect()):
                return True
        return False

    def obtener_estacion_en(self, posicion: Tuple[int, int]) -> Optional[Estacion]:
        """Busca una estación en una casilla."""
        for estacion in self.estaciones:
            if estacion.posicion == posicion:
                return estacion
        return None

    def agregar_mensaje(self, texto: str, color: Tuple[int, int, int]) -> None:
        """Agrega un texto flotante a la pantalla."""
        self.mensajes_flotantes.append({"texto": texto, "color": color, "x": GRID_X + GRID_COLS * TILE // 2, "y": GRID_Y + 55, "t": 1.4})

# Ingredientes
def ing_pan() -> PanesYBases:
    """Crea un pan."""
    return PanesYBases("pan", "pan")


def ing_carne() -> Proteina:
    """Crea una carne."""
    return Proteina("carne", "carne")


def ing_lechuga() -> VegetalFruta:
    """Crea una lechuga."""
    return VegetalFruta("lechuga", "lechuga")


def ing_papas() -> PapaFreir:
    """Crea unas papas."""
    return PapaFreir("papas", "papas")


def ing_pollo() -> Proteina:
    """Crea un pollo."""
    return Proteina("pollo", "pollo")


def ing_tomate() -> VegetalFruta:
    """Crea un tomate."""
    return VegetalFruta("tomate", "tomate")


def ing_arroz() -> PanesYBases:
    """Crea arroz listo."""
    return PanesYBases("arroz", "arroz")


def ing_frijoles() -> PanesYBases:
    """Crea frijoles listos."""
    return PanesYBases("frijoles", "frijoles")


def ing_repollo() -> VegetalFruta:
    """Crea un repollo."""
    return VegetalFruta("repollo", "repollo")


def ing_chicharron() -> Proteina:
    """Crea chicharrón."""
    return Proteina("chicharron", "chicharron")


def ing_pico_gallo() -> VegetalFruta:
    """Crea pico de gallo."""
    return VegetalFruta("pico_gallo", "pico_gallo")


def ing_platano() -> PapaFreir:
    """Crea un plátano para freír."""
    return PapaFreir("platano", "platano")


def ing_tortilla() -> PanesYBases:
    """Crea una tortilla lista."""
    return PanesYBases("tortilla", "tortilla")


def ing_cebolla() -> VegetalFruta:
    """Crea una cebolla."""
    return VegetalFruta("cebolla", "cebolla")


def ing_alitas() -> Proteina:
    """Crea unas alitas."""
    return Proteina("alitas", "alitas")


def ing_salchichon() -> Proteina:
    """Crea salchichón."""
    return Proteina("salchichon", "salchichon")


def ing_queso() -> PanesYBases:
    """Crea queso listo."""
ESCENARIOS: List[Dict] = [
    {
        "nombre": "McDonald's",
        "tema": "Comida rápida: hamburguesas, papas y combos.",
        "fondo": "mcdonalds",
        "tiempo": 130,
        "layout": [
            "##############",
            "#a.b.c.d.....#",
            "#............#",
            "#..T.....S...#",
            "#............#",
            "#..P.....F..E#",
            "#............#",
            "#....1..2....#",
            "#............#",
            "##############",
        ],
        "despensas": {
            "a": ing_pan(),
            "b": ing_carne(),
            "c": ing_lechuga(),
            "d": ing_papas(),
        },
        "recetas": [
            ("Papas fritas", ["papas:frito"]),
            ("Hamburguesa simple", ["pan:listo", "carne:cocinado"]),
            ("Hamburguesa deluxe", ["pan:listo", "carne:cocinado", "lechuga:picado"]),
            ("Combo Mc", ["pan:listo", "carne:cocinado", "papas:frito"]),
        ],
        "max_ordenes": 3,
        "intervalo": 8.0,
    },
    {
        "nombre": "Soda El Cachetón",
        "tema": "Comida tica: gallo pinto, casado, chifrijo y patacones.",
        "fondo": "cacheton",
        "tiempo": 150,
        "layout": [
            "##############",
            "#a..b.....c..#",
            "#..####......#",
            "#..T..P..S...#",
            "#............#",
            "#d.....F...E.#",
            "#..####......#",
            "#e..1....2.f.#",
            "#............#",
            "##############",
        ],
        "despensas": {
            "a": ing_arroz(),
            "b": ing_frijoles(),
            "c": ing_pollo(),
            "d": ing_repollo(),
            "e": ing_chicharron(),
            "f": ing_pico_gallo(),
        },
        "recetas": [
            ("Gallo pinto", ["arroz:listo", "frijoles:listo"]),
            ("Casado Cachetón", ["arroz:listo", "pollo:cocinado", "repollo:picado"]),
            ("Chifrijo", ["frijoles:listo", "chicharron:cocinado", "pico_gallo:picado"]),
            ("Plato tico", ["arroz:listo", "frijoles:listo", "pollo:cocinado", "repollo:picado"]),
        ],
        "max_ordenes": 4,
        "intervalo": 7.0,
    },
    {
        "nombre": "Bar La Nave",
        "tema": "Bocas de bar: nachos, alitas, picadas y hamburguesas.",
        "fondo": "nave",
        "tiempo": 170,
        "layout": [
            "##############",
            "#a....#...gb.#",
            "#..T..#..S...#",
            "#.....#......#",
            "#..1..P..2...#",
            "#.....#..F...#",
            "#c....#....dE#",
            "#..e.....f...#",
            "#............#",
            "##############",
        ],
        "despensas": {
            "a": ing_tortilla(),
            "b": ing_carne(),
            "c": ing_tomate(),
            "d": ing_cebolla(),
            "e": ing_alitas(),
            "f": ing_papas(),
            "g": ing_pan(),
        },
        "recetas": [
            ("Nachos La Nave", ["tortilla:listo", "carne:cocinado", "tomate:picado"]),
            ("Hamburguesa nocturna", ["pan:listo", "carne:cocinado", "cebolla:picado"]),
            ("Alitas con papas", ["alitas:cocinado", "papas:frito"]),
            ("Picada Nave", ["carne:cocinado", "papas:frito", "cebolla:picado"]),
        ],
        "max_ordenes": 4,
        "intervalo": 6.0,
    },
]

# Juego Principal


# Carga centralizada de imágenes obligatorias para las versiones intermedias.
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
    """Partida directa con tres escenarios seleccionables por teclado."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Crazy Snack Rush - tres escenarios")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = cargar_assets_juego()
        self.indice_escenario = 0
        self.cocina = Cocina(ESCENARIOS[self.indice_escenario])
        self.chef_activo = 0

    def iniciar(self, indice: int) -> None:
        self.indice_escenario = indice
        self.cocina = Cocina(ESCENARIOS[indice])
        self.chef_activo = 0

    def manejar_eventos(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    self.chef_activo = 1 - self.chef_activo
                elif event.key == pygame.K_SPACE:
                    chef = self.cocina.chefs[self.chef_activo]
                    self.cocina.mensaje = chef.interactuar(self.cocina)
                elif event.key == pygame.K_q:
                    self.cocina.mensaje = self.cocina.chefs[self.chef_activo].descartar()
                elif event.key == pygame.K_r:
                    self.iniciar(self.indice_escenario)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    nuevo = int(event.unicode) - 1
                    if 0 <= nuevo < len(ESCENARIOS):
                        self.iniciar(nuevo)

    def mover(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        chef = self.cocina.chefs[self.chef_activo]
        vx = 0
        vy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1
        if vx or vy:
            mag = math.hypot(vx, vy)
            ux, uy = vx / mag, vy / mag
            if abs(vx) > abs(vy):
                chef.direccion = (1 if vx > 0 else -1, 0)
            else:
                chef.direccion = (0, 1 if vy > 0 else -1)
            self.cocina.mover(chef, ux * Chef.VEL * dt, uy * Chef.VEL * dt)

    def dibujar(self) -> None:
        self.screen.blit(self.assets["backgrounds"][self.cocina.background_key], (0, 0))
        for col, row in self.cocina.paredes:
            x, y = grid_to_pixel((col, row))
            pygame.draw.rect(self.screen, WALL, (x, y, TILE, TILE), border_radius=6)
            pygame.draw.rect(self.screen, BLACK, (x, y, TILE, TILE), 2, border_radius=6)
        for estacion in self.cocina.estaciones:
            estacion.dibujar(self.screen, self.assets["stations"])
        for index, chef in enumerate(self.cocina.chefs):
            chef.dibujar(self.screen, self.assets["chefs"], index == self.chef_activo)

        draw_text(self.screen, self.cocina.nombre, UI_X, 75, 26, BLACK, True)
        draw_text(self.screen, "1 McDonald's | 2 Cachetón | 3 La Nave", UI_X, 112, 16, DARK, True)
        draw_text(self.screen, "Tiempo: " + formato_tiempo(self.cocina.tiempo_restante), UI_X, 150, 22, RED, True)
        draw_text(self.screen, "Puntos: " + str(self.cocina.puntos), UI_X, 185, 22, BLUE, True)
        draw_text(self.screen, "Órdenes:", UI_X, 235, 22, BLACK, True)
        y = 270
        for receta in self.cocina.ordenes[:4]:
            draw_text(self.screen, receta.nombre, UI_X, y, 18, BLACK, True)
            draw_text(self.screen, receta.texto_ingredientes(), UI_X, y + 24, 15, DARK)
            y += 70
        draw_wrapped_text(self.screen, self.cocina.mensaje, UI_X, 610, WIDTH - UI_X - 40, 18, BLACK)
        pygame.display.flip()

    def ejecutar(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self.manejar_eventos()
            if not self.cocina.juego_terminado:
                self.mover(dt)
                self.cocina.actualizar(dt)
            self.dibujar()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().ejecutar()
