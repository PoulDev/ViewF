import string
import random
import pygame
import threading
from math import sqrt, pow, cos, sin, tan, factorial, pi

from geo_math import distance, process_equation, apply_modifiers 


precision = 0.01
total_points = 10000
width, height = 750, 500
zoom = 8
move = [0, 0]
font_size = 23
preprocess_vars = True

running = True
equations = []
variables = {}
pause = False

globals_vars = {'sqrt': sqrt, 'pow': pow, 'cos': cos, 'sin': sin, 'tan': tan, 'factorial': factorial, 'pi': pi, 'random': random}

for equation in equations:
    for i, char in enumerate(equation):
        if char in string.ascii_letters and char not in ('x', 'y') and i > 1 and equation[i-1] == '$':
            variables[char] = '1'
            print(f'New variable {char} = 1')

def editor():
    global total_points, preprocess_vars, pause
    while True:
        try:
            cmd = input('> ')
            if cmd.startswith('set'):
                cmd = cmd[4:]
                space = cmd.index(' ')
                variable, value = cmd[:space], cmd[space+1:]
                variables[variable] = value
                print(f'"{variable}" set to {value}')
    
            elif cmd.replace(' ', '').startswith('y=') or cmd.replace(' ', '').startswith('x='):
                equation_colors.append(random_color())
                equations.append(cmd)
            
            elif cmd.startswith('rm'):
                index = int(cmd.split(' ')[-1])
                equations.pop(index)
                equation_colors.pop(index)

            elif cmd in ('preprocess', 'preprocess_vars', 'preprocessvars', 'preprocess-vars'):
                preprocess_vars = not(preprocess_vars)
                print(f'Variables Pre-Processing is now set to {preprocess_vars}')

            elif cmd == 'pause':
                pause = True
                print('Rendering paused, type "resume" to resume it')
            elif cmd == 'resume':
                pause = False
                print('Rendering resumed')

            elif cmd.startswith('points'):
                total_points = int(cmd.split(' ')[-1])

            elif cmd.startswith('color'):
                equation, r, g, b = [int(x) for x in cmd.split(' ')[1:]]
                try:
                    equation_colors[equation] = (r, g, b)
                except:
                    print(f'Failed to set color for equation n.{equation}')
                else:
                    print(f'Equation n.{equation} color is now {r} {g} {b}')

        except Exception as e:
            print(f'ERROR => {type(e)}: {e}')
            continue
        except KeyboardInterrupt:
            break

editor_thread = threading.Thread(target=editor)
editor_thread.daemon = True
editor_thread.start()

equation_colors = []
avaible_colors = list(range(20, 256, 20))

def random_color():
    color = [0,0,0]
    while color == [0,0,0]:
        color = [random.choice(avaible_colors) for _ in range(3)]
        if tuple(color) in equation_colors: continue
    return tuple(color)


def get_function_points(equation, avaible_points, globals_vars, variables):
    global preprocess_vars

    processed_variables = variables
    if preprocess_vars:
        processed_variables = {k: str(eval(v)) for k, v in variables.items()}

    step = avaible_points // 2
    for x in range(step - total_points, step):
        x *= precision
        if equation.startswith('y'):
            y = process_equation({'x': x}, equation, globals_vars, processed_variables)
        elif equation.startswith('x'):
            y = x
            x = process_equation({'y': y}, equation, globals_vars, processed_variables)
        else:
            print(f'[FATAL] Incognita not found in {equation}')
            continue

        if y is None:
            yield None, None
            continue

        yield x, y

pygame.init()

screen = pygame.display.set_mode([width, height])


font = pygame.font.SysFont('FiraCode Nerd Font', font_size)
fontx = 10
fonty = 5

clock = pygame.time.Clock()

highlighted_point = None
mouse_point = None

mouse_move = (0, 0)
mouse_down = False
move_save = move.copy()

while running:
    screen.fill((0, 0, 0))

    size = 2
    points = 0

    globals_vars.update(variables)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL and event.y == 1:
            zoom += 2
            highlighted_point = None
        elif event.type == pygame.MOUSEWHEEL and event.y == -1:
            zoom -= 2
            highlighted_point = None
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                mouse_point = event.pos
            elif event.button == pygame.BUTTON_MIDDLE:
                mouse_down = False
                move_save = move.copy()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_MIDDLE:
                mouse_move = event.pos
                mouse_down = True
                highlighted_point = None

        elif event.type == pygame.MOUSEMOTION:
            if mouse_down:
                move = [
                    move_save[0] + (event.pos[0] - mouse_move[0]),
                    move_save[1] + (event.pos[1] - mouse_move[1])
                ]

        if zoom < 8:
            zoom = 8

    nearest_to_mouse = None

    for index, equation in enumerate(equations):
        last_point = None
        color = equation_colors[index]
        for x, y in get_function_points(equation, total_points, globals_vars, variables.copy()):
            if x is None and y is None:
                last_point = None
                continue

            x, y = apply_modifiers(width, height, zoom, tuple(move), x, y)

            if x < -500 or x > width+500: continue
            if y < -500 or y > height+500: continue

            if mouse_point and (d := distance(x, mouse_point[0], y, mouse_point[1])) < 10:
                if not nearest_to_mouse:
                    nearest_to_mouse = (d, x, y)
                elif d < nearest_to_mouse[0]:
                    nearest_to_mouse = (d, x, y)

            if last_point and distance(x, last_point[0], y, last_point[1]) < 1000:
                pygame.draw.line(screen, color, last_point, (x, y), size)
                #pygame.draw.circle(screen, (255, 255, 255), (x, y), size)

            points += 1
            last_point = x, y

        if mouse_point and nearest_to_mouse:
            mouse_point = None
            highlighted_point = list(nearest_to_mouse[1:])

    for i, equation in enumerate(equations):
        txt = f'{i}. {equation}'
        screen.blit(font.render(txt, False, equation_colors[i]), (
            fontx,
            i * font_size + fonty
            ))

    for i, variable in enumerate(variables):
        screen.blit(font.render(f'{variable} = {variables[variable]}', False, (255, 255, 255)), (
            fontx,
            height - (i+1) * font_size - fonty
            ))

    if highlighted_point:
        x, y = highlighted_point
        pygame.draw.circle(screen, (255, 255, 255), (x, y), size*2)

        pygame.draw.line(screen, (255, 255, 255), (x, y), (width/2+move[0], y), size)
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, height/2+move[1]), size)
        screen.blit(font.render(f'{round(x, 2)}', False, (255, 255, 255)), (x, height/2))
        screen.blit(font.render(f'{round(y, 2)}', False, (255, 255, 255)), (width/2, y))

    # Y Axis
    pygame.draw.line(screen, (255, 255, 255), (width/2+move[0], 0), (width/2+move[0], height), 1)
    # X Axis
    pygame.draw.line(screen, (255, 255, 255), (0, height/2+move[1]), (width, height/2+move[1]), 1)

    clock.tick()

    for index, text in enumerate([f'Zoom: {zoom}', f'Points: {points}', f'FPS: {clock.get_fps():.2f}']):
        screen.blit(
                font.render(text, False, (255, 255, 255)),
                (width - fontx - font.size(text)[0], index * font_size + fonty)
            )

    pygame.display.flip()

    while pause: pass

pygame.quit()

