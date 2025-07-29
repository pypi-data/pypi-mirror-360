import sys

if sys.platform == 'win32':
    from msvcrt import getch
else:
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

def secure_input(prompt='Password: ', mask='*'):
    #Vérification du type et de la taille des paramètres
    if not isinstance(prompt, str):
        raise TypeError(f'Unsupported prompt type: accept only str and not {type(prompt).__name__}')
    if not isinstance(mask, str):
        raise TypeError(f'Unsupported mask type: accept only str and not {type(prompt).__name__}')
    if len(mask) > 1:
        raise ValueError(f'Unsupported mask size: accept only 0 or 1 characters and not {len(mask)}')

    passwd = []
    #Affichage du prompt
    sys.stdout.write(prompt)
    sys.stdout.flush()
    while True:
        key = ord(getch())
        if key == 13:
            sys.stdout.write('\n')
            return ''.join(passwd)
        elif key in (8, 127):
            if len(passwd) > 0:
                #Pour supprimer un caractère
                sys.stdout.write('\b \b')
                sys.stdout.flush()
                passwd = passwd[:-1]
        elif 0 <= key <= 31:
            pass
        else:
            sys.stdout.write(mask)
            sys.stdout.flush()
            passwd.append(chr(key))