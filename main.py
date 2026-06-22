import sys
import pygame

WIDTH = 1180
HEIGHT = 740
FPS = 60
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)


def draw_text(surface: pygame.Surface, text: str, x: int, y: int, size: int = 30) -> None:
    font = pygame.font.SysFont("arial", size, bold=True)
    rendered = font.render(text, True, BLACK)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)


class Game:
    """Ventana principal"""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Crazy Snack Rush")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def manejar_eventos(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def dibujar(self) -> None:
        self.screen.fill(WHITE)
        draw_text(self.screen, "Crazy Snack Rush", WIDTH // 2, HEIGHT // 2 - 25, 48)
        pygame.display.flip()

    def ejecutar(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.manejar_eventos()
            self.dibujar()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().ejecutar()