import sys
if sys.platform == 'win32':
    from msvcrt import getch

else: # macOS and Linux
    import tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def getpass(prompt='Password: ', mask='*'):
    if not isinstance(prompt, str):
        raise TypeError('prompt argument must be a str, not %s' % (type(prompt).__name__))
    if not isinstance(mask, str):
        raise TypeError('mask argument must be a zero- or one-character str, not %s' % (type(prompt).__name__))
    if len(mask) > 1:
        raise ValueError('mask argument must be a zero- or one-character str')

    enteredPassword = []
    sys.stdout.write(prompt)
    sys.stdout.flush()
    while True:
        key = ord(getch())
        if key == 13: # Enter key pressed.
            sys.stdout.write('\n')
            return ''.join(enteredPassword)
        elif key in (8, 127): # Backspace/Del key erases previous output.
            if len(enteredPassword) > 0:
                sys.stdout.write('\b \b')
                sys.stdout.flush()
                enteredPassword = enteredPassword[:-1]
        elif 0 <= key <= 31:
            #For non printable character
            pass
        else:
            char = chr(key)
            sys.stdout.write(mask)
            sys.stdout.flush()
            enteredPassword.append(char)
