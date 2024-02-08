import re
import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador Maquina de Turing")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

canvas_rect = pygame.Rect(100, 100, 600, 500)

font = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 36)

# Fita
TAPE_DISPLAY_HEIGHT = 100  
TAPE_CELL_WIDTH = 30 
TAPE_CELL_HEIGHT = 50  
TAPE_START_Y = 0  

TAPE_LENGTH = 25
tape = ['#'] * TAPE_LENGTH 
tape_pointer = 0

allowed_symbols = []
with open("symbols.txt", "r") as file:
    allowed_symbols = [line.strip() for line in file.readlines() if line.strip()]
symbols_count = len(allowed_symbols)

symbol_to_index = {symbol: index for index, symbol in enumerate(allowed_symbols)}
index_to_symbol = {index: symbol for symbol, index in symbol_to_index.items()}


# Menu contextual
right_click_menu = None
transition_creation_state = False
selected_state_for_transition = None
transition_prompt_position = (100, 60)
transition_parameters = {"x": "", "y": "", "m": ""}
first_state_for_transition = None
second_state_for_transition = None
collecting_transition_parameters = False
input_stage = "x"
user_input = "" 
input_box = pygame.Rect(150, 50, 500, 50)
show_input_box = False

# Botoes
simulate_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 80, 100, 60)
simulate_button_clicked = False
start_state_button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT - 80, 100, 60)

# Classe que armazena as transicoes
class Transition:
    def __init__(self, current_state, next_state, current_letter, replacement_letter, direction, is_final):
        self.current_state = current_state
        self.next_state = next_state
        self.current_letter = current_letter
        self.replacement_letter = replacement_letter
        self.direction = direction
        self.is_final = is_final
        
    def __str__(self):
        return f"{self.current_letter} : {self.replacement_letter}, {self.direction}"
    
    @classmethod
    def simplified(cls, is_final):
        return cls(-1, None, None, None, None, is_final)

# Variaveis globais de simulacao
is_simulating = False
current_state_index = None
simulation_step = 0
states = []
transitions = []
previous_state_index = None
last_transition = None
transition_table = [[Transition.simplified(is_final=False) for _ in range(symbols_count)] for _ in range(10)]
available_names = [f"S{i}" for i in range(10)]
transition_counts = {}

# Rodar passo a passo da MT
def execute_simulation_step():
    global tape, tape_pointer, states, transition_table, is_simulating, simulation_step, current_state_index, previous_state_index, last_transition

    if not is_simulating:
        return

    # Primeiro passo procura o estado inicial
    if simulation_step == 0:
        current_state_index = find_start_state_index()
        if current_state_index is None:
            print("Estado inicial nao encontrado. Simulacao nao pode ser executada.")
            is_simulating = False
            return

    current_symbol = tape[tape_pointer]
    symbol_index = symbol_to_index[current_symbol] if current_symbol in symbol_to_index else None
    
    if symbol_index is None:
        print("Simbolo invalido no ponteiro da fita.")
        is_simulating = False
        return

    transition = transition_table[current_state_index][symbol_index]
    
    if transition.current_state == -1:
        print("Nenhuma transicao valida encontrada. Parando simulacao.")
        is_simulating = False
        return
    
    # Realizar transicao
    tape[tape_pointer] = transition.replacement_letter
    direction = transition.direction
    next_state_index = transition.next_state
    previous_state_index = current_state_index
    current_state_index = next_state_index
    
    # Historico das transicoes
    print(f"Transition: {current_symbol} -> {transition.replacement_letter}, Move: {direction}, Next State: {next_state_index}")
    
    # Mover o ponteiro da fita
    if direction == 'L':
        tape_pointer -= 1
    elif direction == 'R':
        tape_pointer += 1
        
    last_transition = (find_state_position_by_index(previous_state_index), find_state_position_by_index(current_state_index))
    
    simulation_step += 1

def find_start_state_index():
    for index, state in enumerate(states):
        if state['is_start']:
            return index
    return None

def get_state_index(state_name):
    for index, state in enumerate(states):
        if state['name'] == state_name:
            return index
    return None

def apply_transition():
    global transition_parameters, first_state_for_transition, second_state_for_transition
    start_index = get_state_index(first_state_for_transition['name'])
    end_index = get_state_index(second_state_for_transition['name'])
    if start_index is not None and end_index is not None:
        current_letter = transition_parameters['x']
        replacement_letter = transition_parameters['y']
        direction = transition_parameters['m']
        is_final = first_state_for_transition['is_accept']
        update_transition(start_index, end_index, current_letter, replacement_letter, direction, is_final)
        
def update_transition(start_state_index, end_state_index, current_letter, replacement_letter, direction, is_final):
    global transition_table
    
    symbol_index = symbol_to_index[current_letter]
    
    if 0 <= start_state_index < 10 and 0 <= symbol_index < symbols_count:
        transition_table[start_state_index][symbol_index] = Transition(start_state_index, end_state_index, current_letter, replacement_letter, direction, is_final)

def draw_tape(screen, font):
    start_x = (WIDTH - TAPE_CELL_WIDTH * TAPE_LENGTH) // 2
    for i in range(TAPE_LENGTH):
        cell_rect = pygame.Rect(start_x + i * TAPE_CELL_WIDTH, TAPE_START_Y, TAPE_CELL_WIDTH, TAPE_CELL_HEIGHT)
        pygame.draw.rect(screen, BLACK, cell_rect, 1)
        if i == tape_pointer:
            pygame.draw.rect(screen, RED, cell_rect, 2)
            triangle_height = 10
            triangle_base_half = 5
            pygame.draw.polygon(screen, RED, [
                (cell_rect.centerx, TAPE_START_Y + TAPE_CELL_HEIGHT + triangle_height),
                (cell_rect.centerx - triangle_base_half, TAPE_START_Y + TAPE_CELL_HEIGHT),
                (cell_rect.centerx + triangle_base_half, TAPE_START_Y + TAPE_CELL_HEIGHT)
            ])
        
        symbol_text = font.render(tape[i], True, BLACK)
        screen.blit(symbol_text, (cell_rect.x + (TAPE_CELL_WIDTH - symbol_text.get_width()) // 2, cell_rect.y + (TAPE_CELL_HEIGHT - symbol_text.get_height()) // 2))

def handle_tape_click(pos):
    start_x = (WIDTH - TAPE_CELL_WIDTH * TAPE_LENGTH) // 2
    if pos[1] >= TAPE_START_Y and pos[1] <= TAPE_START_Y + TAPE_CELL_HEIGHT:
        click_x = pos[0] - start_x
        if 0 <= click_x < TAPE_CELL_WIDTH * TAPE_LENGTH:
            cell_index = click_x // TAPE_CELL_WIDTH
            return cell_index
    return None

def prompt_for_symbol():
    global show_input_box, user_input, input_stage
    show_input_box = True
    input_stage = "symbol"
    user_input = ""

def draw_canvas(screen, canvas_rect):
    pygame.draw.rect(screen, WHITE, canvas_rect)
    pygame.draw.rect(screen, BLACK, canvas_rect, 2)

def add_new_state(pos):
    if not available_names:
        print("Numero maximo de estados atingido.")
        return
    state_name = available_names.pop(0)
    state_index = int(re.search(r'\d+', state_name).group())
    states.append({"index": state_index, "position": pos, "name": state_name, "is_start": False, "is_accept": False})
 
def delete_state(pos):
    global states, transition_table, available_names
    deleted_state_name = None

    # Encontrar o estado pela posicao, pegar o nome e liberar
    for i, state in enumerate(states):
        state_pos = state["position"]
        if (state_pos[0] - 20 < pos[0] < state_pos[0] + 20) and (state_pos[1] - 20 < pos[1] < state_pos[1] + 20):
            deleted_state_name = state["name"]
            available_names.append(state["name"])
            available_names.sort()
            del states[i]
            break

    # Deletar o estado
    if deleted_state_name is not None:
        deleted_state_index = get_state_index(deleted_state_name)
        
        # Deletar todas as transicoes relacionadas a esse estado
        if deleted_state_index is not None:
            for i in range(len(transition_table)):
                for j in range(len(transition_table[i])):
                    if(transition_table[i][j].current_state == deleted_state_index or transition_table[i][j].next_state == deleted_state_index):
                        transition_table[i][j] = Transition.simplified(is_final=False)
            
def draw_context_menu(screen, menu):
    if menu:
        mouse_pos = pygame.mouse.get_pos()
        menu["option_rects"] = []
        for i, option in enumerate(menu["options"]):
            text_surf = font.render(option, True, BLACK)
            option_width, option_height = text_surf.get_size()
            option_width += 20
            option_height += 10
            option_rect = pygame.Rect(menu["pos"][0], menu["pos"][1] + i * (option_height + 5), option_width, option_height)
            menu["option_rects"].append(option_rect)

            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, GRAY, option_rect)
            else:
                pygame.draw.rect(screen, WHITE, option_rect)
            pygame.draw.rect(screen, BLACK, option_rect, 1)
            screen.blit(text_surf, (option_rect.x + 10, option_rect.y + 5))

def draw_states(screen, states):
    global current_state_index, previous_state_index
    
    for state in states:
        state_pos = state["position"]
        state_index = state["index"]
        
        # Verificar se e um estado atual ou anterior para mostrar em vermelho
        if state_index == current_state_index:
            circle_color = RED
        elif state_index == previous_state_index:
            circle_color = RED
        else:
            circle_color = BLACK
            
        pygame.draw.circle(screen, circle_color, state_pos, 20, 2)
        
        # Indicador de estado final
        if state["is_accept"]:
            pygame.draw.circle(screen, BLACK, state_pos, 25, 2)
        
        # Indicador de estado inicial
        if state["is_start"]:
            pygame.draw.polygon(screen, BLACK, [(state_pos[0] - 30, state_pos[1]), (state_pos[0] - 50, state_pos[1] - 15), (state_pos[0] - 50, state_pos[1] + 15)])
        
        text_surf = font.render(state["name"], True, BLACK)
        text_rect = text_surf.get_rect(center=state_pos)
        screen.blit(text_surf, text_rect)

def check_right_click(event):
    global right_click_menu, transition_creation_state, selected_state_for_transition, second_state_for_transition
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        pos = pygame.mouse.get_pos()
        clicked_state = find_clicked_state(pos)
        
        # Opcoes variam dependendo do estado
        if not transition_creation_state and canvas_rect.collidepoint(pos):
            if clicked_state:
                right_click_menu = {"pos": pos, "options": ["Marcar como inicial", "Marcar como final", "Transicao", "Deletar"]}
                selected_state_for_transition = clicked_state
            else:
                right_click_menu = {"pos": pos, "options": ["Novo estado"] if len(states) < 10 else []}
        elif transition_creation_state and canvas_rect.collidepoint(pos):
            if clicked_state:
                right_click_menu = {"pos": pos, "options": ["Transicao para...", "Cancelar"]}
                second_state_for_transition = clicked_state
            else:
                right_click_menu = {"pos": pos, "options": ["Cancelar"]}

def find_clicked_state(pos):
    for state in states:
        state_pos = state["position"]
        if (state_pos[0] - 20 < pos[0] < state_pos[0] + 20) and (state_pos[1] - 20 < pos[1] < state_pos[1] + 20):
            return state
    return None

def handle_menu_selection(pos):
    global right_click_menu, transition_creation_state, collecting_transition_parameters, selected_state_for_transition, first_state_for_transition, second_state_for_transition
    
    if right_click_menu and "option_rects" in right_click_menu:
        option_selected = None
        for i, rect in enumerate(right_click_menu["option_rects"]):
            if rect.collidepoint(pos):
                option_selected = right_click_menu["options"][i]

                if option_selected == "Novo estado":
                    add_new_state(right_click_menu["pos"])
                elif option_selected == "Marcar como inicial":
                    for state in states:
                        state["is_start"] = False
                    selected_state_for_transition["is_start"] = True
                elif option_selected == "Marcar como final":
                    selected_state_for_transition["is_accept"] = not selected_state_for_transition["is_accept"]
                elif option_selected == "Deletar":
                    if selected_state_for_transition:
                        delete_state(selected_state_for_transition["position"])
                elif option_selected == "Transicao":
                    transition_creation_state = True
                    first_state_for_transition = selected_state_for_transition
                elif option_selected == "Cancelar":
                    transition_creation_state = False
                    selected_state_for_transition = None
                    first_state_for_transition = None
                    second_state_for_transition = None
                elif option_selected == "Transicao para...":
                    transition_creation_state = False
                    collecting_transition_parameters = True
                
                break
        right_click_menu = None

def draw_input_box(screen, font):
    global user_input
    
    if not show_input_box:
        return

    pygame.draw.rect(screen, WHITE, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)
    
    prompt_text = f"Pressione a tecla para {input_stage.upper()}: {user_input}"
    
    if input_stage == "symbol":
        prompt_text = "Pressione a tecla do simbolo desejado"
    
    text_surf = font.render(prompt_text, True, BLACK)
    screen.blit(text_surf, (input_box.x + 10, input_box.y + 10))
    
    if not input_stage == "symbol":
        retry_button = pygame.Rect(input_box.right - 150, input_box.y + 10, 60, 30)
        next_button = pygame.Rect(input_box.right - 80, input_box.y + 10, 60, 30)
        pygame.draw.rect(screen, GRAY, retry_button)
        pygame.draw.rect(screen, GRAY, next_button)
        screen.blit(font.render("Limp.", True, BLACK), (retry_button.x + 10, retry_button.y + 5))
        screen.blit(font.render("Prox.", True, BLACK), (next_button.x + 10, next_button.y + 5))

def update_input_state(event, font):
    global user_input, input_stage, collecting_transition_parameters, show_input_box, selected_state_for_transition, first_state_for_transition, second_state_for_transition, allowed_symbols
    if not show_input_box:
        return
    
    if input_stage == "symbol" and event.type == pygame.KEYDOWN:
        user_input = event.unicode
        if user_input in allowed_symbols:
            if tape_pointer is not None:
                tape[tape_pointer] = user_input
                show_input_box = False
                input_stage = "x"
        else:
            print("Symbolo nao permitido. Insira um simbolo valido.")
            user_input = ""
    
    if event.type == pygame.KEYDOWN:
        if input_stage in ["x", "y"]:
            user_input = event.unicode
            if user_input not in allowed_symbols:
                print(f"Symbolo '{user_input}' nao permitido. Por favor insira um simbolo valido.")
                user_input = ""
        elif input_stage == "m":
            if event.unicode.lower() in ["l", "r"]:
                user_input = event.unicode.upper()

        draw_input_box(screen, font)
    
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos
        retry_button = pygame.Rect(input_box.right - 150, input_box.y + 10, 60, 30)
        next_button = pygame.Rect(input_box.right - 80, input_box.y + 10, 60, 30)
        if retry_button.collidepoint(mouse_pos):
            user_input = ""
        elif next_button.collidepoint(mouse_pos):
            if input_stage == "x":
                transition_parameters["x"] = user_input
                input_stage = "y"
            elif input_stage == "y":
                transition_parameters["y"] = user_input
                input_stage = "m"   
            if input_stage == "m" and user_input.upper() in ["L", "R"]:
                transition_parameters["m"] = user_input
                if first_state_for_transition and second_state_for_transition:
                    apply_transition()
                    first_state_for_transition = None
                    second_state_for_transition = None
                input_stage = "x"
                user_input = ""
                collecting_transition_parameters = False
                show_input_box = False

            user_input = "" 

def draw_transition_prompt(screen, position):
    if transition_creation_state:
        text_surf = font.render("Transicao para...", True, BLACK)
        screen.blit(text_surf, position)

def find_state_position_by_index(state_index):
    for state in states:
        if state['index'] == state_index:
            return state['position']
    return None

def calculate_edge_points(start_pos, end_pos, radius=20):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
    offset_x = dx * radius / distance
    offset_y = dy * radius / distance

    new_start = (start_pos[0] + offset_x, start_pos[1] + offset_y)
    new_end = (end_pos[0] - offset_x, end_pos[1] - offset_y)

    return new_start, new_end

def draw_arrow(screen, start_pos, end_pos, text, loopback=False, color=BLACK):
    global font
    arrow_color = BLACK
    arrow_thickness = 1
    arrowhead_size = 10

    pygame.draw.line(screen, arrow_color, start_pos, end_pos, arrow_thickness)

    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    angle = math.atan2(dy, dx)

    arrowhead_point1 = (end_pos[0] - arrowhead_size * math.cos(angle - math.pi / 6),
                        end_pos[1] - arrowhead_size * math.sin(angle - math.pi / 6))
    arrowhead_point2 = (end_pos[0] - arrowhead_size * math.cos(angle + math.pi / 6),
                        end_pos[1] - arrowhead_size * math.sin(angle + math.pi / 6))

    pygame.draw.polygon(screen, arrow_color, [end_pos, arrowhead_point1, arrowhead_point2])

    if loopback:
        text_pos = (start_pos[0], start_pos[1] - 30)
    else:
        text_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)

    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, text_pos)

def draw_transitions(screen):
    global transition_counts, font, last_transition
    transition_counts.clear()
    drawn_arrows = set()

    for i, row in enumerate(transition_table):
        transitions_text = {}

        for j, transition in enumerate(row):
            if transition.current_state != -1:
                start_pos = find_state_position_by_index(transition.current_state)
                end_pos = find_state_position_by_index(transition.next_state)

                if start_pos and end_pos:
                    key = (transition.current_state, transition.next_state)
                    transition_key = (start_pos, end_pos)
                    count = transition_counts.get(key, 0)
                    transition_counts[key] = count + 1

                    if transition_key not in transitions_text:
                        transitions_text[transition_key] = []
                    transition_text = f"{transition.current_letter} : {transition.replacement_letter}, {transition.direction}"
                    transitions_text[transition_key].append(transition_text)

        for (start_pos, end_pos), texts in transitions_text.items():
            loopback = start_pos == end_pos
            if not loopback:
                new_start, new_end = calculate_edge_points(start_pos, end_pos)
                if (start_pos, end_pos) == last_transition:
                    draw_arrow(screen, new_start, new_end, "\n".join(texts), color=RED)
                else:
                    draw_arrow(screen, new_start, new_end, "\n".join(texts))
                drawn_arrows.add((start_pos, end_pos))
            else:
                text_pos_y = start_pos[1] - 40
                for text in texts:
                    text_surf = font.render(text, True, BLACK)

                    text_pos_x = start_pos[0] - text_surf.get_width() / 2
                    screen.blit(text_surf, (text_pos_x, text_pos_y))
                    text_pos_y -= 20

def draw_footer(screen, font):
    bottom_menu_rect = pygame.Rect(0, HEIGHT - 100, WIDTH, 100)
    pygame.draw.rect(screen, BLACK, bottom_menu_rect)

    pygame.draw.rect(screen, WHITE, simulate_button_rect, 2)
    simulate_text = font.render("Simular", True, WHITE)
    screen.blit(simulate_text, (simulate_button_rect.x + (simulate_button_rect.width - simulate_text.get_width()) // 2, simulate_button_rect.y + (simulate_button_rect.height - simulate_text.get_height()) // 2))
    
    pygame.draw.rect(screen, WHITE, start_state_button_rect, 2)
    start_state_text = font.render("Inicio", True, WHITE)
    screen.blit(start_state_text, (start_state_button_rect.x + (start_state_button_rect.width - start_state_text.get_width()) // 2, start_state_button_rect.y + (start_state_button_rect.height - start_state_text.get_height()) // 2))


running = True
while running:
    screen.fill(WHITE)
    draw_tape(screen, font)
    draw_canvas(screen, canvas_rect)
    draw_states(screen, states)
    draw_transition_prompt(screen, transition_prompt_position)
    draw_footer(screen, font_large)
    draw_transitions(screen)


    if collecting_transition_parameters:
        show_input_box = True
        
    if simulate_button_clicked and is_simulating:
        execute_simulation_step()
        simulate_button_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif show_input_box:
            update_input_state(event, font)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if simulate_button_rect.collidepoint(event.pos):
                simulate_button_clicked = True
                start_state_index = find_start_state_index()          
                
                if start_state_index is not None:
                    is_simulating = True

                else:
                    print("Estado inicial nao encontrado. Simulacao nao pode ser executada.")
            
            if start_state_button_rect.collidepoint(event.pos):
                is_simulating = False
                simulation_step = 0
                current_state_index = None
                previous_state_index = None
                last_transition = None
                tape = ['#'] * TAPE_LENGTH
                tape_pointer = 0
                
            if event.button == 3:
                check_right_click(event)
            elif event.button == 1:
                cell_index = handle_tape_click(pygame.mouse.get_pos())
                if cell_index is not None:
                    tape_pointer = cell_index
                    prompt_for_symbol()
                elif right_click_menu:
                    handle_menu_selection(pygame.mouse.get_pos())

    if show_input_box:
        draw_input_box(screen, font)
    
    if right_click_menu:
        draw_context_menu(screen, right_click_menu)

    pygame.display.flip()

pygame.quit()
sys.exit()