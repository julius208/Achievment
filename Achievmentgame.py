import pygame
import sys
import threading
import time

pygame.init()

# Bildschirmgröße und Farben
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 149, 237)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Clicker")

# Schriftart
font = pygame.font.SysFont(None, 36)

# Klick-Zähler
cookies = 0
cookies_per_click = 1
total_cookies = 0

# Clicker-Position
clicker_pos = (WIDTH // 2, HEIGHT // 2)
clicker_radius = 100

# Upgrade-Button
upgrade_button = pygame.Rect(50, 500, 200, 60)
upgrade_cost = 50

# Button für Achievements
achievements_button = pygame.Rect(600, 50, 180, 50)
show_achievements = False

# Zeitmanagement Clicker-Radius
clicker_expansion_time = 120
last_click_time = 0

# CPS Zähler
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

# Autoklicker-Überwachung
click_times = []
AUTOKLICK_LIMIT = 50  # 50 CPS Grenze
autoklicker_detected = False
autoklicker_time = 0
countdown_seconds = 10
last_beep_time = 0  # Zeitstempel für Piepton (optional)

# Text zeichnen
def draw_text(text, pos, color=WHITE, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surface, rect)

# Piep-Ton (optional)
def play_beep():
    frequency = 440  # Hz
    duration = 100  # ms
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except ImportError:
        pass  # Plattformabhängig, kein Ton

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(DARK_GRAY)

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not autoklicker_detected:
            mx, my = pygame.mouse.get_pos()

            dx = mx - clicker_pos[0]
            dy = my - clicker_pos[1]
            if dx**2 + dy**2 <= clicker_radius**2:
                # Klick registrieren
                clicker_radius = 120
                cookies += cookies_per_click
                total_cookies += cookies_per_click
                last_click_time = current_time

                # CPS zählen
                clicks_per_second += 1

                # Autoklicker-Check (50 Klicks in letzter Sekunde)
                click_times.append(current_time)
                click_times = [t for t in click_times if current_time - t <= 1000]  # nur letzte Sekunde

                if len(click_times) >= AUTOKLICK_LIMIT:
                    autoklicker_detected = True
                    autoklicker_time = current_time

            # Upgrade kaufen
            if upgrade_button.collidepoint(mx, my):
                if cookies >= upgrade_cost:
                    cookies -= upgrade_cost
                    cookies_per_click += 1
                    upgrade_cost = int(upgrade_cost * 1.5)

            # Achievements ein-/ausklappen
            if achievements_button.collidepoint(mx, my):
                show_achievements = not show_achievements

    # Clicker Radius zurücksetzen
    if current_time - last_click_time >= clicker_expansion_time:
        clicker_radius = 100

    # CPS reset alle 1 Sekunde, außer Autoklicker erkannt
    if not autoklicker_detected and current_time - cps_start_time >= 1000:
        cps_start_time = current_time
        clicks_per_second = 0

    # Achievement prüfen
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

    if clicks_per_second >= 5 and not has_cps_5:
        achievements.append("⚡ 5 CPS!")
        has_cps_5 = True

    if clicks_per_second >= 10 and not has_cps_10:
        achievements.append("⚡ 10 CPS!")
        has_cps_10 = True

    if clicks_per_second >= 20 and not has_cps_20:
        achievements.append("⚡ 20 CPS!")
        has_cps_20 = True

    # Wenn Autoklicker erkannt, Countdown starten und nach 10 Sekunden "abstürzen"
    if autoklicker_detected:
        time_passed = (current_time - autoklicker_time) // 1000
        seconds_left = countdown_seconds - time_passed

        # Alle Sekunde piepen (optional)
        if current_time - last_beep_time >= 1000:
            threading.Thread(target=play_beep, daemon=True).start()
            last_beep_time = current_time

        # Bildschirm blitzweiß machen kurz vor Ablauf
        if seconds_left <= 3:
            if seconds_left > 0:
                # Blinken
                if (current_time // 250) % 2 == 0:
                    screen.fill(WHITE)
                else:
                    screen.fill(DARK_GRAY)
            else:
                # Zeit abgelaufen - "Absturz"
                screen.fill(WHITE)
                pygame.display.flip()
                pygame.time.delay(500)
                pygame.quit()
                sys.exit()

        # Warn-Text anzeigen
        draw_text("AUTOKLICKER ERKANNT!", (WIDTH//2, HEIGHT//2 - 60), RED, center=True)
        draw_text(f"Selbstzerstörung in {seconds_left} Sekunden...", (WIDTH//2, HEIGHT//2 - 20), YELLOW, center=True)

    else:
        # Normales Spiel zeichnen
        pygame.draw.circle(screen, BLUE, clicker_pos, clicker_radius)
        draw_text(f"+{cookies_per_click}", (clicker_pos[0], clicker_pos[1] + 10), center=True)

        draw_text(f"Cookies: {cookies}", (30, 30))
        draw_text(f"CPS: {clicks_per_second}", (30, 70))
        draw_text(f"Total Cookies: {total_cookies}", (30, 110))

        pygame.draw.rect(screen, GREEN, upgrade_button)
        draw_text(f"Upgrade ({upgrade_cost})", (upgrade_button.x + 10, upgrade_button.y + 10))

        pygame.draw.rect(screen, WHITE, achievements_button)
        draw_text("🏆 Achievements anzeigen", (achievements_button.x + 10, achievements_button.y + 10), DARK_GRAY)

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
