import __main__
import impmagic


@impmagic.loader(
    {'module': 'socket'},
    {'module': 'app.display', 'submodule': ['logs']},
)
def connect_server():
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connexion.connect((__main__.settings.host, __main__.settings.port))
    except socket.error:
        return 0
    logs("Connexion établie avec le serveur.", "success")
    return connexion


@impmagic.loader(
    {'module': 'base64','submodule': ['b64encode']},
    {'module': 'Crypto.Cipher','submodule': ['AES']},
    {'module': 'Crypto.Hash','submodule': ['SHA256']},
    {'module': 'Crypto','submodule': ['Random']}
)
def encrypt(source, encode=True):
    key = __main__.settings.totp.now()
    key = SHA256.new(key.encode()).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return b64encode(data) if encode else data


@impmagic.loader(
    {'module': 'base64','submodule': ['b64decode']},
    {'module': 'Crypto.Cipher','submodule': ['AES']},
    {'module': 'Crypto.Hash','submodule': ['SHA256']}
)
def decrypt(source, decode=True):
    key = __main__.settings.totp.now()
    if decode:
        source = b64decode(source)
    key = SHA256.new(key.encode()).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")
    return data[:-padding].decode("Utf8")
