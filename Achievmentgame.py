import pygame
import sys

pygame.init()

# Bildschirmgröße und Farben
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 149, 237)
GREEN = (0, 200, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Clicker")

# Schriftart
font = pygame.font.SysFont(None, 36)

# Klick-Zähler
cookies = 0
cookies_per_click = 1
total_cookies = 0  # Gesamtzahl der Cookies (für Achievements)

# Clicker-Position
clicker_pos = (WIDTH // 2, HEIGHT // 2)
clicker_radius = 100

# Upgrade-Button
upgrade_button = pygame.Rect(50, 500, 200, 60)
upgrade_cost = 50

# Button für Achievements
achievements_button = pygame.Rect(600, 50, 180, 50)
show_achievements = False  # Standard: Achievements ausgeblendet

# Zeitmanagement für Clicker-Radius
clicker_expansion_time = 120  # Millisekunden
last_click_time = 0  # Zeitpunkt des letzten Klicks

# Klicks pro Sekunde Zähler
clicks_per_second = 0
cps_start_time = pygame.time.get_ticks()

# Achievement-System
achievements = []
has_cookie_100 = False
has_cookie_500 = False
has_cookie_1000 = False
has_cookie_5000 = False

has_cps_5 = False
has_cps_10 = False
has_cps_20 = False

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
                clicker_radius = 120  # Clicker wird größer
                cookies += cookies_per_click
                total_cookies += cookies_per_click  # Gesamtzahl erhöhen
                last_click_time = pygame.time.get_ticks()  # Zeit speichern

                # Klicks pro Sekunde zählen
                clicks_per_second += 1

            # Upgrade kaufen
            if upgrade_button.collidepoint(mx, my):
                if cookies >= upgrade_cost:
                    cookies -= upgrade_cost
                    cookies_per_click += 1
                    upgrade_cost = int(upgrade_cost * 1.5)

            # Achievements ein-/ausklappen
            if achievements_button.collidepoint(mx, my):
                show_achievements = not show_achievements  # Status umschalten

    # Prüfen, ob die eingestellte Zeit vergangen ist
    if pygame.time.get_ticks() - last_click_time >= clicker_expansion_time:
        clicker_radius = 100  # Clicker zurücksetzen

    # CPS-Zähler aktualisieren (alle Sekunde zurücksetzen)
    if pygame.time.get_ticks() - cps_start_time >= 1000:
        cps_start_time = pygame.time.get_ticks()
        clicks_per_second = 0  # Zurücksetzen

    # Achievements für Cookies prüfen
    if total_cookies >= 100 and not has_cookie_100:
        achievements.append("🍪 100 Cookies!")
        has_cookie_100 = True

    if total_cookies >= 500 and not has_cookie_500:
        achievements.append("🍪 500 Cookies!")
        has_cookie_500 = True

    if total_cookies >= 1000 and not has_cookie_1000:
        achievements.append("🍪 1000 Cookies!")
        has_cookie_1000 = True

    if total_cookies >= 5000 and not has_cookie_5000:
        achievements.append("🍪 5000 Cookies!")
        has_cookie_5000 = True

    # Achievements für CPS prüfen
    if clicks_per_second >= 5 and not has_cps_5:
        achievements.append("⚡ 5 CPS!")
        has_cps_5 = True

    if clicks_per_second >= 10 and not has_cps_10:
        achievements.append("⚡ 10 CPS!")
        has_cps_10 = True

    if clicks_per_second >= 20 and not has_cps_20:
        achievements.append("⚡ 20 CPS!")
        has_cps_20 = True

    # Clicker zeichnen
    pygame.draw.circle(screen, BLUE, clicker_pos, clicker_radius)
    draw_text(f"+{cookies_per_click}", (clicker_pos[0], clicker_pos[1] + 10), center=True)

    # Zähler
    draw_text(f"Cookies: {cookies}", (30, 30))
    draw_text(f"CPS: {clicks_per_second}", (30, 70))  # Klicks pro Sekunde anzeigen
    draw_text(f"Total Cookies: {total_cookies}", (30, 110))  # Gesamtanzahl anzeigen

    # Upgrade-Button
    pygame.draw.rect(screen, GREEN, upgrade_button)
    draw_text(f"Upgrade ({upgrade_cost})", (upgrade_button.x + 10, upgrade_button.y + 10))

    # Button für Achievements ein-/ausklappen
    pygame.draw.rect(screen, WHITE, achievements_button)
    draw_text("🏆 Achievements anzeigen", (achievements_button.x + 10, achievements_button.y + 10), DARK_GRAY)

    # Erreichte Achievements anzeigen
    if show_achievements:
        y_offset = 150
        draw_text("🏆 Achievements:", (30, y_offset))
        for achievement in achievements:
            y_offset += 30
            draw_text(achievement, (30, y_offset), GREEN)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
