import impmagic
import sys

color_config = {'cyan': 'cyan', 'green': 'green', 'dark_gray': 'dark_gray', 'light_gray': 'light_gray', 'yellow': 'yellow', 'red': 'red', 'light_red': 'light_red', 'orange_1': 'orange_1', 'magenta': 'magenta'}
#SETTINGS TRUECOLOR
#color_config = {'cyan': '26,128,162', 'green': 'green', 'dark_gray': 'dark_gray', 'light_gray': 'light_gray', 'yellow': 'light_goldenrod_2b', 'red': 'red', 'light_red': 'light_red', 'orange_1': 'red', 'magenta': 'magenta'}


@impmagic.loader(
    {'module': 'zpp_color', 'submodule': ['fg', 'attr']}
)
def print_nxs(message, color=None, nojump=False):
    if color==None:
        color = color_config['cyan']
    
    if nojump:
        print(f"{fg(color)}{message}{attr(0)}", end="")
    else:
        print(f"{fg(color)}{message}{attr(0)}")


@impmagic.loader(
    {'module': '__main__'},
    {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
    {'module': 'datetime', 'submodule': ['datetime']}
)
def logs(message, lvl='info', component="core", nodate=False):
    if __main__.settings.verbose:
        if lvl=='logs':
            color = color_config['light_gray']
        elif lvl=='info':
            color = color_config['cyan']
        elif lvl=='warning':
            color = color_config['yellow']
        elif lvl=='error':
            color = color_config['red']
        elif lvl=='critical':
            color = color_config['light_red']
        elif lvl=='success':
            color = color_config['green']
        
        print_date = ""
        if not nodate:
            date = datetime.now().strftime("%Y/%m/%d - %H:%M:%S.%f")
            print_date = f"{fg(color_config['dark_gray'])}[{attr(0)}{fg(color_config['magenta'])}{date}{attr(0)}{fg(color_config['dark_gray'])}] - {attr(0)}"

        print_component = f"{fg(color_config['dark_gray'])}[{attr(0)}{fg(color_config['yellow'])}{component.upper()}{attr(0)}{fg(color_config['dark_gray'])}] - {attr(0)}"

        print(f"{print_date}{print_component}{fg(color)}{message}{attr(0)}")


@impmagic.loader(
    {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
    {'module': 'datetime', 'submodule': ['datetime']}
)
def notify(message, lvl='info'):
    if lvl=='logs':
        color = color_config['light_gray']
    elif lvl=='info':
        color = color_config['cyan']
    elif lvl=='warning':
        color = color_config['yellow']
    elif lvl=='error':
        color = color_config['red']
    elif lvl=='critical':
        color = color_config['light_red']
    elif lvl=='success':
        color = color_config['green']

    print(f"{fg(color)}{message}{attr(0)}")


def SaveCursor():
    sys.stdout.write("\033[s")
    sys.stdout.flush()

def RestoreCursor():
    sys.stdout.write("\033[u")
    sys.stdout.flush()

def SaveScreen():
    SaveCursor()
    sys.stdout.write("\033[?47h")
    sys.stdout.flush()

def RestoreScreen():
    sys.stdout.write("\033[?47l")
    sys.stdout.flush()
    RestoreCursor()

def CleanScreen():
    sys.stdout.write("\033[2J")  # Effacer l'écran
    sys.stdout.flush()