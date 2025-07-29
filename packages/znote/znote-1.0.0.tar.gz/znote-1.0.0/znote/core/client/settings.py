import __main__
import impmagic


class Settings():
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'os'},
        {'module': 'pyotp'},
        {'module': 'app.display','submodule': ['logs']},
        {'module': 'Crypto','submodule': ['Random']},
        {'module': 'Crypto.PublicKey','submodule': ['RSA']},
        {'module': 'core.config','submodule': ['Config']},
        {'module': 'core.client.token','submodule': ['get_token']}
    )
    def __init__(self, config_file):
        self.config_dir = os.path.abspath(os.path.expanduser('~/.config/znote'))
        
        self.token_file = os.path.join(self.config_dir, ".token")

        if not config_file:
            config_file = os.path.join(self.config_dir, "config.yml")

        self.config = Config(f"{config_file}")

        self.verbose = self.config.get('client.verbose', default=False, auto_set=True)
        
        self.host = self.config.get('client.host', default="127.0.0.1", auto_set=True)
        self.port = self.config.get('client.port', default=40017, auto_set=True)
        self.key_size = self.config.get('client.key_size', default=2048, auto_set=True)
        self.key_otp = self.config.get('client.key_otp', default='JBSWY3DPEHPK3PXP', auto_set=True)     
        self.totp = pyotp.TOTP(self.key_otp)

        self.PubServ = None
        self.keyC = None

        self.token = get_token(self.token_file)
        self.pubserv_set = None
        self.authenticated = False


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'os'},
        {'module': 'hashlib'},
        {'module': 'Crypto.PublicKey', 'submodule': ['RSA']},
        {'module': 'Crypto', 'submodule': ['Random']},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def load_key(self):
        privkey_path = os.path.join(self.config_dir, "client.key")
        pubkey_path = os.path.join(self.config_dir, "client.pem")
        
        if not os.path.exists(privkey_path) or not os.path.exists(pubkey_path):
            try:
                #Génération de la paire de clé pour les échanges avec le client
                logs("Création de la paire de clé", "info")
                rng = Random.new().read
                rsa_key = RSA.generate(self.key_size, rng)
                rsa_priv = rsa_key.exportKey("PEM")

                self.PrivKey = rsa_key.exportKey('PEM', pkcs=1)

                with open(privkey_path, "wb") as f:
                    f.write(self.PrivKey)

                key_pub = rsa_key.publickey()
                self.PubKey = key_pub.exportKey("PEM")
                
                with open(pubkey_path, "wb") as f:
                    f.write(self.PubKey)

                
                logs("Paire de clé créée", "success")

            except Exception as err:
                logs(f"Erreur lors de la création de la paire de clé: {err}", "error")

        else:
            try:
                logs("Chargement de la paire de clé", "info")
                
                with open(privkey_path, "rb") as f:
                    self.PrivKey = f.read()
                
                with open(pubkey_path, "rb") as f:
                    self.PubKey = f.read()
                
                logs("Paire de clé chargée", "success")

            except Exception as err:
                logs(f"Erreur lors du chargement de la paire de clé: {err}", "error")

        self.key = RSA.importKey(self.PrivKey)

        #Calcul du hash de la clé du client
        self.clienthash = hashlib.sha256(self.PubKey).hexdigest()


        #Chargement de la clé serveur stocké
        serverpub_path = os.path.join(self.config_dir, "server.pub")
        if os.path.exists(serverpub_path):
            try:
                logs("Chargement de la clé du serveur", "info")

                with open(serverpub_path, "rb") as f:
                    content = f.read()

                self.pubserv_set = True
                self.keyC = RSA.importKey(content)
                #Calcul du hash de la clé du serveur
                self.serverhash = hashlib.sha256(content).hexdigest()

            except Exception as err:
                logs(f"Erreur lors du chargement de la clé du serveur: {err}", "error")


    @impmagic.loader(
        {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
    )
    def init_settings(self):
        host = input(f"{fg('dark_gray')}host [{fg('cyan')}{self.host}{fg('dark_gray')}]: ")
        port = input(f"{fg('dark_gray')}port [{fg('cyan')}{self.port}{fg('dark_gray')}]: ")
        key_size = input(f"{fg('dark_gray')}key_size [{fg('cyan')}{self.key_size}{fg('dark_gray')}]: ")
        key_otp = input(f"{fg('dark_gray')}key_otp [{fg('cyan')}{self.key_otp}{fg('dark_gray')}]: ")
        verbose = input(f"{fg('dark_gray')}verbose [{fg('cyan')}{self.verbose}{fg('dark_gray')}]: ")
        
        if host:
            self.config.set('server.host', host)

        if port and isinstance(port, int):
            self.config.set('server.port', int(port))

        if key_size and isinstance(key_size, int): 
            self.config.set('server.key_size', int(key_size))
        
        if key_otp:
            self.config.set('server.key_otp', key_otp)
        
        if verbose:
            self.config.set('server.verbose', verbose)

