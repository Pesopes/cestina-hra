import pygame
import sys

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

# Načtení dat z fraze.txt
def load_phrases(file):
    phrases = []
    try:
        with open(file, "r") as f:
            for line in f:
                phrase, correct_answer = line.strip().split(",")
                phrases.append((phrase, correct_answer))
    except FileNotFoundError:
        print(f"Soubor {file} nebyl nalezen.")
        sys.exit()
    return phrases

phrases = load_phrases("fraze.txt")
current_phrase_index = 0
score = 0
results = []

# Tlačítka
button_i = pygame.Rect(150, 400, 200, 100)  # Tlačítko pro "i"
button_y = pygame.Rect(450, 400, 200, 100)  # Tlačítko pro "y"

# Funkce pro vykreslení tlačítek
def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, WHITE)
    screen.blit(
        text_surface,
        (rect.x + (rect.width - text_surface.get_width()) // 2, 
         rect.y + (rect.height - text_surface.get_height()) // 2)
    )

# Funkce pro uložení výsledků
def save_results(file, results):
    with open(file, "w") as f:
        f.write(f"Skóre: {score}/{len(results)}\n")
        for phrase, correct_answer, user_answer in results:
            result = "správně" if correct_answer == user_answer else "špatně"
            f.write(f"{phrase} -> správně: {correct_answer}, odpověď: {user_answer} ({result})\n")

def convert_letter(letter):
    if letter == "y" or letter == "ý":
        return "y"
    if letter == "i" or letter == "í":
        return "i"

# Hlavní smyčka hry
running = True
while running:
    screen.fill(GRAY)
    
    # Zobrazení aktuální fráze
    if current_phrase_index < len(phrases):
        phrase, correct_answer = phrases[current_phrase_index]
        question_text = font.render(f"Doplň: {phrase}", True, WHITE)
        screen.blit(question_text, (50, HEIGHT // 3))
        
        # Vykreslení tlačítek
        draw_button(button_i, "I", BLUE)
        draw_button(button_y, "Y", RED)
    else:
        # Konec hry
        end_text = font.render(f"Hotovo! Skóre: {score}/{len(phrases)}", True, WHITE)
        screen.blit(end_text, (WIDTH // 4, HEIGHT // 3))
        pygame.display.flip()
        save_results("vysledky.txt", results)
        pygame.time.wait(3000)
        running = False
        continue

    # Události
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_i.collidepoint(event.pos):
                user_answer = "i"  # Hráč zvolil "i"
            elif button_y.collidepoint(event.pos):
                user_answer = "y"  # Hráč zvolil "y"
            else:
                continue
            
            # Vyhodnocení odpovědi (ignoruje délku)
            correct_answer = phrases[current_phrase_index][1].lower()
            user_answer = user_answer.lower()
            if convert_letter(user_answer)== convert_letter(correct_answer):
                score += 1
            results.append((phrases[current_phrase_index][0], correct_answer, user_answer))
            current_phrase_index += 1

    # Aktualizace obrazovky
    pygame.display.flip()
    clock.tick(30)

# Ukončení Pygame
pygame.quit()
sys.exit()
