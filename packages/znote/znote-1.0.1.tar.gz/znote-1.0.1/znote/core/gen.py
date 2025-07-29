import impmagic


@impmagic.loader(
    {'module': 'string'},
    {'module': 'secrets'}
)
def gen_password(size):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    pwd = ''
    for i in range(size):
      pwd += ''.join(secrets.choice(alphabet))

    return pwd.encode()


@impmagic.loader(
    {'module': 'uuid','submodule': ['uuid4']}
)
def UUID():
    return str(uuid4()).replace("-","")