import pygame
import sys
pygame.init()

# Bildschirmgröße und Farben
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 149, 237)
GREEN = (0, 0, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Clicker")

# Schriftart
font = pygame.font.SysFont(None, 48)

# Klick-Zähler
cookies = 0
cookies_per_click = 1

# Button-Position
clicker_pos = (WIDTH // 2, HEIGHT // 2)
clicker_radius = 100

# Upgrade-Button
upgrade_button = pygame.Rect(50, 500, 200, 60)
upgrade_cost = 50

# Zeichne Text
def draw_text(text, pos, color=WHITE, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surface, rect)

# Haupt-Spielschleife
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(DARK_GRAY)

    # Ereignisse prüfen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Auf Clicker klicken
            dx = mx - clicker_pos[0]
            dy = my - clicker_pos[1]
            if dx**2 + dy**2 <= clicker_radius**2:
                cookies += cookies_per_click

            # Upgrade kaufen
            if upgrade_button.collidepoint(mx, my):
                if cookies >= upgrade_cost:
                    cookies -= upgrade_cost
                    cookies_per_click += 1
                    upgrade_cost = int(upgrade_cost * 1.5)

    # Clicker zeichnen
    pygame.draw.circle(screen, BLUE, clicker_pos, clicker_radius)
    draw_text(f"+{cookies_per_click}", (clicker_pos[0], clicker_pos[1] + 10), center=True)

    # Zähler
    draw_text(f"Cookies: {cookies}", (30, 30))
    
    # Upgrade-Button
    pygame.draw.rect(screen, GREEN, upgrade_button)
    draw_text(f"Upgrade ({upgrade_cost})", (upgrade_button.x + 10, upgrade_button.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
