import pygame
import sys
import threading
import time
import sqlite3

pygame.init()


# Verbindung zur Datenbank herstellen
conn = sqlite3.connect('game_state.db')  # Datenbank-Datei (kann angepasst werden)
cursor = conn.cursor()

# Tabelle erstellen, falls sie noch nicht existiert
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_state (
    id INTEGER PRIMARY KEY,
    cookies INTEGER,
    cookies_per_click INTEGER,
    total_cookies INTEGER,
    autoclickers INTEGER,
    upgrade_cost INTEGER,
    autoclicker_cost INTEGER,
    rebirths INTEGER,
    has_rebirth_1 BOOLEAN,
    has_rebirth_5 BOOLEAN,
    has_rebirth_10 BOOLEAN,
    has_cookie_100 BOOLEAN,
    has_cookie_500 BOOLEAN,
    has_cookie_1000 BOOLEAN,
    has_cookie_5000 BOOLEAN,
    has_cps_5 BOOLEAN,
    has_cps_10 BOOLEAN,
    has_cps_20 BOOLEAN
)
''')

# Sicherstellen, dass ein Datensatz mit id=1 existiert
cursor.execute("SELECT COUNT(*) FROM game_state WHERE id = 1")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO game_state VALUES (
        1, 0, 1, 0, 0, 50, 100, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )
    ''')
    conn.commit()


# Bildschirmgröße und Farben
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 149, 237)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (120, 120, 120)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Clicker")

# Schriftart
font = pygame.font.SysFont(None, 36)

# Spielzustand aus DB laden
cursor.execute("SELECT * FROM game_state WHERE id = 1")
row = cursor.fetchone()

(
    _id, cookies, cookies_per_click, total_cookies, autoclickers,
    upgrade_cost, autoclicker_cost, rebirths,
    has_rebirth_1, has_rebirth_5, has_rebirth_10,
    has_cookie_100, has_cookie_500, has_cookie_1000, has_cookie_5000,
    has_cps_5, has_cps_10, has_cps_20
) = row

# Clicker-Position
clicker_pos = (WIDTH // 2, HEIGHT // 2)
clicker_radius = 100

# Upgrade-Button
upgrade_button = pygame.Rect(50, 460, 200, 60)

# Autoklicker-Button
autoclicker_button = pygame.Rect(50, 530, 200, 60)
cookies_per_autoclicker = 1
last_autoclick_time = 0

# Rebirth-System
rebirth_button = pygame.Rect(50, 400, 200, 50)
rebirth_cost_base = 5000
rebirth_discount_factor = 0.95

# Autoklicker-Button
autoclicker_button = pygame.Rect(50, 570, 200, 60)
autoclickers = 0
autoclicker_cost = 100
cookies_per_autoclicker = 1
last_autoclick_time = 0

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
if has_rebirth_1:
    achievements.append("🔁 1. Rebirth!")
if has_rebirth_5:
    achievements.append("🔁 5 Rebirths!")
if has_rebirth_10:
    achievements.append("🔁 10 Rebirths!")
if has_cookie_100:
    achievements.append("🍪 100 Cookies!")
if has_cookie_500:
    achievements.append("🍪 500 Cookies!")
if has_cookie_1000:
    achievements.append("🍪 1000 Cookies!")
if has_cookie_5000:
    achievements.append("🍪 5000 Cookies!")
if has_cps_5:
    achievements.append("⚡ 5 CPS!")
if has_cps_10:
    achievements.append("⚡ 10 CPS!")
if has_cps_20:
    achievements.append("⚡ 20 CPS!")



# Autoklicker-Überwachung
click_times = []
AUTOKLICK_LIMIT = 50
autoklicker_detected = False
autoklicker_time = 0
countdown_seconds = 10
last_beep_time = 0


def draw_text(text, pos, color=WHITE, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surface, rect)


def play_beep():
    frequency = 440
    duration = 100
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except ImportError:
        pass


clock = pygame.time.Clock()
running = True

while running:
    screen.fill(DARK_GRAY)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not autoklicker_detected:
            mx, my = pygame.mouse.get_pos()
            dx = mx - clicker_pos[0]
            dy = my - clicker_pos[1]
            if dx ** 2 + dy ** 2 <= clicker_radius ** 2:
                clicker_radius = 120
                cookies += cookies_per_click
                total_cookies += cookies_per_click
                last_click_time = current_time
                clicks_per_second += 1
                click_times.append(current_time)
                # Nur Klicks aus der letzten Sekunde behalten
                click_times = [t for t in click_times if current_time - t <= 1000]
                if len(click_times) >= AUTOKLICK_LIMIT:
                    autoklicker_detected = True
                    autoklicker_time = current_time

            # Upgrade
            if upgrade_button.collidepoint(mx, my):
                if cookies >= upgrade_cost:
                    cookies -= upgrade_cost
                    cookies_per_click += 1

                    upgrade_cost = int(upgrade_cost * 1.5 * (rebirth_discount_factor ** rebirths))

            # Autoklicker

            if autoclicker_button.collidepoint(mx, my):
                if cookies >= autoclicker_cost:
                    cookies -= autoclicker_cost
                    autoclickers += 1

                    autoclicker_cost = int(autoclicker_cost * 1.7 * (rebirth_discount_factor ** rebirths))

            # Rebirth
            if rebirth_button.collidepoint(mx, my):
                current_rebirth_cost = int(rebirth_cost_base * (1.8 ** rebirths))
                if total_cookies >= current_rebirth_cost:
                    rebirths += 1
                    cookies = 0
                    total_cookies = 0
                    cookies_per_click = 1 + rebirths
                    autoclickers = 0
                    upgrade_cost = int(50 * (rebirth_discount_factor ** rebirths))
                    autoclicker_cost = int(100 * (rebirth_discount_factor ** rebirths))

                    if rebirths >= 1 and not has_rebirth_1:
                        achievements.append("🔁 1. Rebirth!")
                        has_rebirth_1 = True
                    if rebirths >= 5 and not has_rebirth_5:
                        achievements.append("🔁 5 Rebirths!")
                        has_rebirth_5 = True
                    if rebirths >= 10 and not has_rebirth_10:
                        achievements.append("🔁 10 Rebirths!")
                        has_rebirth_10 = True

            # Achievements anzeigen
            if achievements_button.collidepoint(mx, my):
                show_achievements = not show_achievements

    # Autoklicker generieren Cookies
    if not autoklicker_detected and current_time - last_autoclick_time >= 1000:
        cookies += autoclickers * cookies_per_autoclicker
        total_cookies += autoclickers * cookies_per_autoclicker
        last_autoclick_time = current_time


    if current_time - last_click_time >= clicker_expansion_time:
        clicker_radius = 100

    if not autoklicker_detected and current_time - cps_start_time >= 1000:
        cps_start_time = current_time
        clicks_per_second = 0

    # Achievements prüfen
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

    if autoklicker_detected:
        time_passed = (current_time - autoklicker_time) // 1000
        seconds_left = countdown_seconds - time_passed
        if current_time - last_beep_time >= 1000:
            threading.Thread(target=play_beep, daemon=True).start()
            last_beep_time = current_time
        if seconds_left <= 3:
            if seconds_left > 0:
                if (current_time // 250) % 2 == 0:
                    screen.fill(WHITE)
                else:
                    screen.fill(DARK_GRAY)
            else:
                screen.fill(WHITE)
                pygame.display.flip()
                pygame.time.delay(500)
                pygame.quit()
                sys.exit()

        draw_text("AUTOKLICKER ERKANNT!", (WIDTH // 2, HEIGHT // 2 - 60), RED, center=True)
        draw_text(f"Selbstzerstörung in {seconds_left} Sekunden...", (WIDTH // 2, HEIGHT // 2 - 20), YELLOW, center=True)

    else:

        pygame.draw.circle(screen, BLUE, clicker_pos, clicker_radius)
        draw_text(f"+{cookies_per_click}", (clicker_pos[0], clicker_pos[1] + 10), center=True)
        draw_text(f"Cookies: {cookies}", (30, 30))
        draw_text(f"CPS: {clicks_per_second}", (30, 70))
        draw_text(f"Total Cookies: {total_cookies}", (30, 110))
        draw_text(f"Rebirths: {rebirths}", (30, 150))

        # Upgrade-Button
        if cookies >= upgrade_cost:
            pygame.draw.rect(screen, GREEN, upgrade_button)
        else:
            pygame.draw.rect(screen, GRAY, upgrade_button)
        draw_text(f"Upgrade ({upgrade_cost})", (upgrade_button.x + 10, upgrade_button.y + 10))


        # Autoklicker-Button
        if cookies >= autoclicker_cost:
            pygame.draw.rect(screen, YELLOW, autoclicker_button)
        else:
            pygame.draw.rect(screen, GRAY, autoclicker_button)
        draw_text(f"Autoklicker ({autoclicker_cost})", (autoclicker_button.x + 10, autoclicker_button.y + 10), DARK_GRAY)
        draw_text(f"Anzahl: {autoclickers}", (autoclicker_button.x + 10, autoclicker_button.y + 40), DARK_GRAY)

        # Rebirth-Button
        current_rebirth_cost = int(rebirth_cost_base * (1.8 ** rebirths))
        if total_cookies >= current_rebirth_cost:
            pygame.draw.rect(screen, RED, rebirth_button)
        else:
            pygame.draw.rect(screen, GRAY, rebirth_button)
        draw_text(f"Rebirth ({current_rebirth_cost})", (rebirth_button.x + 10, rebirth_button.y + 10))
        draw_text(f"Anzahl: {rebirths}", (rebirth_button.x + 10, rebirth_button.y + 30))


        pygame.draw.rect(screen, WHITE, achievements_button)
        draw_text("🏆 Achievements anzeigen", (achievements_button.x + 10, achievements_button.y + 10), DARK_GRAY)

        if show_achievements:
            y_offset = 200
            draw_text("🏆 Achievements:", (30, y_offset))
            for achievement in achievements:
                y_offset += 30
                draw_text(achievement, (30, y_offset), GREEN)

    pygame.display.flip()
    clock.tick(60)

# Spielstand speichern beim Beenden
cursor.execute('''
UPDATE game_state SET
    cookies = ?, cookies_per_click = ?, total_cookies = ?, autoclickers = ?,
    upgrade_cost = ?, autoclicker_cost = ?, rebirths = ?,
    has_rebirth_1 = ?, has_rebirth_5 = ?, has_rebirth_10 = ?,
    has_cookie_100 = ?, has_cookie_500 = ?, has_cookie_1000 = ?, has_cookie_5000 = ?,
    has_cps_5 = ?, has_cps_10 = ?, has_cps_20 = ?
WHERE id = 1
''', (
    cookies, cookies_per_click, total_cookies, autoclickers,
    upgrade_cost, autoclicker_cost, rebirths,
    has_rebirth_1, has_rebirth_5, has_rebirth_10,
    has_cookie_100, has_cookie_500, has_cookie_1000, has_cookie_5000,
    has_cps_5, has_cps_10, has_cps_20
))
conn.commit()
conn.close()

pygame.quit()
sys.exit()
