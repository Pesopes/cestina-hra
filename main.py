import pygame
import sys
import random
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime

# Inicializace Pygame
pygame.init()

# Nastavení okna
#WIDTH, HEIGHT = 800, 600
WIDTH, HEIGHT = 1920,1080
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption("Doplňování I/Y")
font = pygame.font.Font(None, 80)
clock = pygame.time.Clock()

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
GREEN = (34, 139, 34)

# Cesty k souborům
LOG_FILE = "game_stats.json"
PHRASES_FILE = "fraze.txt"


# Načtení a inicializace herních statistik
def load_game_stats():
    if not os.path.exists(LOG_FILE):
        return {
            "total_games_played": 0,
            "total_time_played": 0,
            "total_phrases_attempted": 0,
            "total_correct_answers": 0,
            "phrase_mistake_count": {},
            "game_history": []
        }

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "total_games_played": 0,
            "total_time_played": 0,
            "total_phrases_attempted": 0,
            "total_correct_answers": 0,
            "phrase_mistake_count": {},
            "game_history": []
        }


# Uložení herních statistik
def save_game_stats(stats):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)


def update_game_stats(stats, game_data):
    stats["total_games_played"] += 1
    stats["total_time_played"] += game_data['total_time']
    stats["total_phrases_attempted"] += game_data['total_phrases']
    stats["total_correct_answers"] += game_data['score']
    stats["game_history"].append(game_data)

    # Aktualizace počtu chyb pro jednotlivé fráze
    for phrase, correct_answer, user_answer in game_data['results']:
        if not user_answer:
            stats["phrase_mistake_count"][phrase] = stats["phrase_mistake_count"].get(phrase, 0) + 1

    return stats


# Načtení dat z fraze.txt
def load_phrases(file):
    phrases = []
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                phrase, correct_answer = line.strip().split(",")
                phrases.append((phrase, correct_answer))
    except FileNotFoundError:
        print(f"Soubor {file} nebyl nalezen.")
        sys.exit()
    return phrases



# Menu pro výběr času a zadání jména
def show_menu():
    menu_running = True
    user_name = ""
    while menu_running:
        screen.fill(LIGHT_BLUE)

        # Center the title text
        title_text = font.render("Vyberte délku hry a zadejte své jméno", True, BLUE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Tlačítka pro výběr času
        button_1min = pygame.Rect(WIDTH // 2 - 500, 400, 400, 200)
        button_2min = pygame.Rect(WIDTH // 2 + 50, 400, 400, 200)
        draw_button(button_1min, "1 minuta", BLUE)
        draw_button(button_2min, "2 minuty", RED)

        # Textové pole pro zadání jména - centered
        input_box_width = 300
        input_box = pygame.Rect(WIDTH // 2 - input_box_width // 2, 300, input_box_width, 50)
        pygame.draw.rect(screen, WHITE, input_box)
        name_surface = font.render(user_name, True, BLACK)
        name_rect = name_surface.get_rect(center=input_box.center)
        screen.blit(name_surface, name_rect)

        pygame.display.flip()

        # Události
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1min.collidepoint(event.pos) and user_name:
                    return user_name, 60  # 1 minuta
                elif button_2min.collidepoint(event.pos) and user_name:
                    return user_name, 120 # 2 minuty
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_name:
                        return user_name, 60  # Defaultní čas 1 minuta při stisknutí Enter
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    user_name += event.unicode
        clock.tick(30)


# Funkce pro vykreslení tlačítek
def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=20)
    text_surface = font.render(text, True, WHITE)
    # Center text in button
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


# Funkce pro zobrazení timeru
def draw_timer(time_left, total_time):
    progress_width = 800  # Wider progress bar
    progress_height = 60  # Taller progress bar

    # Center the timer bar perfectly
    progress_rect = pygame.Rect((WIDTH - progress_width) // 2, 50,
                                progress_width, progress_height)

    # Draw background (white bar)
    pygame.draw.rect(screen, WHITE, progress_rect)

    # Calculate and draw the filled portion (green bar)
    fill_width = int((time_left / total_time) * progress_width)
    fill_rect = pygame.Rect((WIDTH - fill_width) // 2, 50,  # Center the fill from left edge
                            fill_width, progress_height)
    pygame.draw.rect(screen, GREEN, fill_rect)

    # Draw border around the timer
    pygame.draw.rect(screen, BLACK, progress_rect, 2)  # 2 pixels wide border

    # Center the time text
    time_text = font.render(f"Čas: {time_left}s", True, BLACK)
    text_rect = time_text.get_rect(center=(WIDTH // 2, 50 + progress_height // 2))  # Perfectly center the text
    screen.blit(time_text, text_rect)

# Funkce pro uložení výsledků
def save_results(file, user_name, results, score, total_phrases):
    with open(file, "w", encoding="utf-8") as f:
        f.write(f"Jméno: {user_name}\n")
        f.write(f"Skóre: {score}/{total_phrases}\n")
        for phrase, correct_answer, user_answer in results:
            result = "správně" if correct_answer == user_answer else "špatně"
            f.write(f"{phrase} -> správně: {correct_answer}, odpověď: {user_answer} ({result})\n")


# Funkce pro převod písmen
def convert_letter(letter):
    if letter in ["y", "ý"]:
        return "y"
    if letter in ["i", "í"]:
        return "i"
    return letter


def create_diploma(user_name, score, total_phrases):
    # Create a white background
    width, height = 1920, 1080
    diploma = Image.new("RGB", (width, height), "white")

    # If confetti.png is transparent, overlay it on the white background
    try:
        confetti = Image.open("confetti.png")
        # Ensure the confetti image is the same size as the diploma
        confetti = confetti.resize((width, height), Image.LANCZOS)

        # Paste confetti with alpha compositing
        diploma = Image.alpha_composite(diploma.convert("RGBA"), confetti.convert("RGBA"))
    except Exception:
        # If confetti can't be loaded, keep the white background
        pass

    # Prepare for drawing
    draw = ImageDraw.Draw(diploma)

    # Font paths
    font_paths = [
        # Windows
        "C:\\Windows\\Fonts\\arial.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        # Common Linux locations
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]

    # Find first available font
    def load_font(paths, size):
        for path in paths:
            try:
                return ImageFont.truetype(path, size)
            except IOError:
                continue
        return ImageFont.load_default()

    # Load fonts
    title_font = load_font(font_paths, 120)
    name_font = load_font(font_paths, 80)
    score_font = load_font(font_paths, 60)

    # Texts
    title_text = "Diplom"
    name_text = f"Jméno: {user_name}"
    score_text = f"Skóre: {score}/{total_phrases}"

    # Calculate text positions
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    score_bbox = draw.textbbox((0, 0), score_text, font=score_font)

    # Draw text with shadow
    shadow_offset = 4
    shadow_color = "lightgray"
    text_color = "black"

    # Shadow texts
    draw.text(
        ((width - title_bbox[2]) // 2 + shadow_offset, height // 9 + shadow_offset),
        title_text, font=title_font, fill=shadow_color
    )
    draw.text(
        ((width - name_bbox[2]) // 2 + shadow_offset, height // 2 + shadow_offset),
        name_text, font=name_font, fill=shadow_color
    )
    draw.text(
        ((width - score_bbox[2]) // 2 + shadow_offset, height // 2 + 100 + shadow_offset),
        score_text, font=score_font, fill=shadow_color
    )

    # Main texts
    draw.text(
        ((width - title_bbox[2]) // 2, height // 9),
        title_text, font=title_font, fill=text_color
    )
    draw.text(
        ((width - name_bbox[2]) // 2, height // 2),
        name_text, font=name_font, fill=text_color
    )
    draw.text(
        ((width - score_bbox[2]) // 2, height // 2 + 100),
        score_text, font=score_font, fill=text_color
    )

    # Save the diploma
    diploma_path = "diplom.png"
    diploma.save(diploma_path)
    return diploma_path


diploma_screen = None
diploma_image = None
def open_diploma(diploma_path):
    global diploma_screen
    global diploma_image
    diploma_image = pygame.image.load(diploma_path)
#    pygame.display.quit()

    diploma_screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
    # pygame.display.init()

    diploma_screen.blit(diploma_image, (0, 0))

    pygame.display.flip()

previous_answer = None
# Hlavní smyčka hry
def main():
    global previous_answer

    # Načtení herních statistik
    game_stats = load_game_stats()

    # Načtení frází
    all_phrases = load_phrases(PHRASES_FILE)

    # Získání jména a času z menu
    user_name, total_time = show_menu()
    time_left = total_time  # Počáteční čas

    # Nastavení časovače
    pygame.time.set_timer(pygame.USEREVENT, 1000)  # Nastavení časovače na 1 sekundu

    # Inicializace proměnných pro hru
    score = 0
    total_phrases = 0
    results = []
    current_phrase_index = 0
    used_phrases = set()  # Sledování použitých frází

    # Tlačítka
    button_i = pygame.Rect(WIDTH/2-500, 400, 400, 200)
    button_y = pygame.Rect(WIDTH/2+50, 400, 400, 200)


    diploma_active = False
    running = True
    while running:
        screen.fill(GRAY)
        if diploma_active:
            diploma_screen.blit(diploma_image, (0, 0))
        elif time_left > 0:
            # Náhodný výběr fráze
            # Pokud jsou všechny fráze použity, resetovat použité fráze
            if current_phrase_index >= len(all_phrases):
                current_phrase_index = 0
                used_phrases.clear()

            # Vybrat frázi, která ještě nebyla použita v tomto kole
            while current_phrase_index < len(all_phrases):
                phrase, correct_answer = all_phrases[current_phrase_index]
                if phrase not in used_phrases:
                    break
                current_phrase_index += 1

                # Pokud jsme prošli všechny fráze, resetovat
                if current_phrase_index >= len(all_phrases):
                    current_phrase_index = 0
                    used_phrases.clear()

            question_text = font.render(f"Doplň: {phrase}", True, WHITE)
            question_rect = question_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(question_text, question_rect)

            # Vykreslení tlačítek
            draw_button(button_i, "I", BLUE)
            draw_button(button_y, "Y", RED)

            # Zobrazení timeru
            draw_timer(time_left, total_time)

            if previous_answer is not None:
                title_text = font.render("Špatně", True, RED)
                if previous_answer:
                    title_text = font.render("Správně", True, GREEN)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
                screen.blit(title_text, title_rect)
        else:
            # Konec hry kvůli uplynulému času
            end_text = font.render(f"Čas vypršel! Skóre: {score}/{total_phrases}", True, WHITE)
            end_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(end_text, end_rect)
            pygame.display.flip()

            # Uložení výsledků hry
            save_results("vysledky.txt", user_name, results, score, total_phrases)

            # Vytvoření diplomu
            diploma_path = create_diploma(user_name, score, total_phrases)
            pygame.time.wait(3000)  # Wait for 3 seconds

            # Aktualizace herních statistik
            game_result = {
                'user_name': user_name,
                'total_time': total_time,
                'total_phrases': total_phrases,
                'score': score,
                'datetime': datetime.now().isoformat(),
                'results': [(phrase, correct_answer, correct) for phrase, correct_answer, correct in results]
            }
            game_stats = update_game_stats(game_stats, game_result)
            save_game_stats(game_stats)

            diploma_active = True
            open_diploma(diploma_path)

        # Události
        user_answer = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_i.collidepoint(event.pos):
                    user_answer = "i"
                elif button_y.collidepoint(event.pos):
                    user_answer = "y"
            if event.type == pygame.USEREVENT:  # Časovač události
                if time_left > 0:
                    time_left -= 1
            if event.type == pygame.KEYDOWN:
                if time_left <= 0 and diploma_active and not event.key == pygame.K_i and not event.key == pygame.K_y:
                    diploma_active = False
                    main()
                elif event.key == pygame.K_i:
                    user_answer = "i"
                elif event.key == pygame.K_y:
                    user_answer = "y"

        if user_answer is not None:
            correct_answer = all_phrases[current_phrase_index][1].lower()
            user_answer = user_answer.lower()

            # Vyhodnocení odpovědi
            was_correct = convert_letter(user_answer) == convert_letter(correct_answer)
            total_phrases += 1
            if was_correct:
                score += 1
            previous_answer = was_correct


            # Přidat frázi mezi použité
            used_phrases.add(phrase)

            # Uložit výsledek
            results.append((phrase, correct_answer, was_correct))
            current_phrase_index += 1

        user_answer = None

        # Aktualizace obrazovky
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()



# Spuštění hry
if __name__ == "__main__":
    main()