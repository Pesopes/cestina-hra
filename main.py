import pygame
import sys
from PIL import Image, ImageDraw, ImageFont

# Inicializace Pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doplňování I/Y")
font = pygame.font.Font(None, 50)
clock = pygame.time.Clock()

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
GREEN = (34, 139, 34)

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
        title_text = font.render("Vyberte délku hry a zadejte své jméno", True, BLUE)
        screen.blit(title_text, (WIDTH // 8, HEIGHT // 4))

        # Tlačítka pro výběr času
        button_1min = pygame.Rect(150, 400, 200, 100)
        button_2min = pygame.Rect(450, 400, 200, 100)
        draw_button(button_1min, "1 minuta", BLUE)
        draw_button(button_2min, "2 minuty", RED)

        # Textové pole pro zadání jména
        input_box = pygame.Rect(250, 300, 300, 50)
        pygame.draw.rect(screen, WHITE, input_box)
        name_surface = font.render(user_name, True, BLACK)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))

        pygame.display.flip()

        # Události
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1min.collidepoint(event.pos) and user_name:
                    return user_name, 60  # 1 minuta
                elif button_2min.collidepoint(event.pos) and user_name:
                    return user_name, 120  # 2 minuty
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
    pygame.draw.rect(screen, color, rect, border_radius=20)  # Zakulacené rohy
    text_surface = font.render(text, True, WHITE)
    screen.blit(
        text_surface,
        (rect.x + (rect.width - text_surface.get_width()) // 2,
         rect.y + (rect.height - text_surface.get_height()) // 2)
    )

# Funkce pro zobrazení timeru
def draw_timer(time_left, total_time):
    progress_width = 500
    progress_height = 50
    fill_width = (time_left / total_time) * progress_width

    # Draw the background of the timer
    pygame.draw.rect(screen, WHITE, (WIDTH // 4, 50, progress_width, progress_height))
    # Draw the filled portion of the timer
    pygame.draw.rect(screen, GREEN, (WIDTH // 4, 50, fill_width, progress_height))

    # Draw the time text
    time_text = font.render(f"Čas: {time_left}s", True, BLACK)
    screen.blit(time_text, (WIDTH // 4 + (progress_width - time_text.get_width()) // 2, 60))

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
    width, height = 800, 600
    diploma = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(diploma)

    # Fonty
    title_font = ImageFont.truetype("arial.ttf", 50)
    text_font = ImageFont.truetype("arial.ttf", 30)

    # Texty
    title_text = "Diplom"
    name_text = f"Jméno: {user_name}"
    score_text = f"Skóre: {score}/{total_phrases}"

    # Pozice textu
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    name_bbox = draw.textbbox((0, 0), name_text, font=text_font)
    score_bbox = draw.textbbox((0, 0), score_text, font=text_font)

    draw.text(((width - title_bbox[2]) // 2, height // 4), title_text, font=title_font, fill="black")
    draw.text(((width - name_bbox[2]) // 2, height // 2), name_text, font=text_font, fill="black")
    draw.text(((width - score_bbox[2]) // 2, height // 2 + 50), score_text, font=text_font, fill="black")

    diploma_path = "diplom.png"
    diploma.save(diploma_path)
    return diploma_path

def open_diploma(diploma_path):
    diploma_image = pygame.image.load(diploma_path)
    diploma_screen = pygame.display.set_mode((800, 600))
    diploma_screen.blit(diploma_image, (0, 0))
    pygame.display.flip()
    pygame.time.wait(5000)

# Hlavní smyčka hry
def main():
    phrases = load_phrases("fraze.txt")
    current_phrase_index = 0
    score = 0
    results = []

    # Získání jména a času z menu
    user_name, total_time = show_menu()
    time_left = total_time  # Počáteční čas

    # Nastavení časovače
    pygame.time.set_timer(pygame.USEREVENT, 1000)  # Nastavení časovače na 1 sekundu

    # Tlačítka
    button_i = pygame.Rect(150, 400, 200, 100)
    button_y = pygame.Rect(450, 400, 200, 100)

    running = True
    while running:
        screen.fill(GRAY)

        if current_phrase_index < len(phrases) and time_left > 0:
            phrase, correct_answer = phrases[current_phrase_index]
            question_text = font.render(f"Doplň: {phrase}", True, WHITE)
            screen.blit(question_text, ((WIDTH - question_text.get_width()) // 2, HEIGHT // 3))

            # Vykreslení tlačítek
            draw_button(button_i, "I", BLUE)
            draw_button(button_y, "Y", RED)

            # Zobrazení timeru
            draw_timer(time_left, total_time)

        elif time_left <= 0:
            # Konec hry kvůli uplynulému času
            end_text = font.render(f"Čas vypršel! Skóre: {score}/{len(phrases)}", True, WHITE)
            screen.blit(end_text, (WIDTH // 4, HEIGHT // 3))
            pygame.display.flip()
            save_results("vysledky.txt", user_name, results, score, len(phrases))
            diploma_path = create_diploma(user_name, score, len(phrases))
            pygame.time.wait(3000)  # Wait for 3 seconds
            open_diploma(diploma_path)
            # running = False

        else:
            # Konec hry po dokončení všech frází
            end_text = font.render(f"Hotovo! Skóre: {score}/{len(phrases)}", True, WHITE)
            screen.blit(end_text, (WIDTH // 4, HEIGHT // 3))
            pygame.display.flip()
            save_results("vysledky.txt", user_name, results, score, len(phrases))
            diploma_path = create_diploma(user_name, score, len(phrases))
            pygame.time.wait(3000)  # Wait for 3 seconds
            open_diploma(diploma_path)
            # running = False

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
                if event.key == pygame.K_i:
                    user_answer = "i"
                elif event.key == pygame.K_y:
                    user_answer = "y"
            if user_answer:
                correct_answer = phrases[current_phrase_index][1].lower()
                user_answer = user_answer.lower()
                if convert_letter(user_answer) == convert_letter(correct_answer):
                    score += 1
                results.append((phrases[current_phrase_index][0], correct_answer, user_answer))
                current_phrase_index += 1

        # Aktualizace obrazovky
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Spuštění hry
if __name__ == "__main__":
    main()
