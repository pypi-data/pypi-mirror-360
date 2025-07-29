import __main__
import impmagic

def set_token(token):
    with open(__main__.settings.token_file, 'w') as f:
        f.write(token)


@impmagic.loader(
    {'module': 'os'},
)
def get_token(token_file):
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read()
    else:
        return False