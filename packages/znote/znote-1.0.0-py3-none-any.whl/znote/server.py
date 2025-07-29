import __main__
import impmagic

import threading





#Supprime le nom d'utilisateur de la liste lorsqu'il se déconnecte
@impmagic.loader(
    {'module': '__main__'}
)
def del_username(token):
    if token in __main__.server.USER:
        del __main__.server.USER[token]


#Thread à la connexion d'un client
class ThreadClient(threading.Thread):
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'Crypto.PublicKey', 'submodule': ['RSA']},
        {'module': 'core.gen', 'submodule': ['UUID']}
    )
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn
        self.username = None
        self.key = None

        #Clé client
        self.keyC = None
        #Clé serveur
        self.keyP = RSA.importKey(__main__.settings.PrivKey)
        self.name = UUID()[0:8]
        self.killed = False

        self.authenticated = False


    #Déchiffrement avec OTP pour récupération de la configuration client
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'base64', 'submodule': ['b64decode']},
        {'module': 'Crypto.Cipher', 'submodule': ['AES']},
        {'module': 'Crypto.Hash', 'submodule': ['SHA256']}
    )
    def decrypt(self, source, decode=True):
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


    #Chiffrement avec OTP pour envoi de la configuration client
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'os'},
        {'module': 'base64', 'submodule': ['b64encode']},
        {'module': 'Crypto.Cipher', 'submodule': ['AES']},
        {'module': 'Crypto.Hash', 'submodule': ['SHA256']}
    )
    def encrypt(self, source, encode=True):
        key = __main__.settings.totp.now()
        key = SHA256.new(key.encode()).digest()
        IV = os.urandom(AES.block_size)

        encryptor = AES.new(key, AES.MODE_CBC, IV)
        padding = AES.block_size - len(source) % AES.block_size
        source += bytes([padding]) * padding
        data = IV + encryptor.encrypt(source)
        return b64encode(data) if encode else data


    #Envoi de message au client
    @impmagic.loader(
        {'module': 'os'},
        {'module': 'cryptography.hazmat.primitives.ciphers', 'submodule': ['Cipher', 'algorithms', 'modes']},
        {'module': 'cryptography.hazmat.backends', 'submodule': ['default_backend']},
        {'module': 'Crypto.PublicKey', 'submodule': ['RSA']},
        {'module': 'Crypto.Cipher', 'submodule': ['PKCS1_OAEP']},
        {'module': 'core.pack', 'submodule': ['pack']},
        {'module': 'core.gen', 'submodule': ['gen_password']}
    )
    def send(self, message):
        message = pack(message, self.keyP)

        if not isinstance(message, bytes):
            message = message.encode()
        
        # Génération de la clé symétrique (AES) et de l'IV
        sym_key = gen_password(32)  # 256 bits
        iv = os.urandom(16)  # IV de 128 bits pour AES

        # Chiffrement du fichier avec AES en mode CFB
        cipher = Cipher(algorithms.AES(sym_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message) + encryptor.finalize()

        # Chiffrement de la clé symétrique avec RSA
        encryptor = PKCS1_OAEP.new(self.keyC)
        sym_key_encrypted = encryptor.encrypt(sym_key)

        # Sauvegarde du IV, de la clé symétrique chiffrée et du fichier chiffré
        message_cipher = iv + sym_key_encrypted + ciphertext

        try:
            self.connexion.send(message_cipher)
        except:
            logs(f"[Thread:{self.name}] - Echec de l'envoi", "error")
            self.kill_thread()
            exit()

    #Réception des données
    @impmagic.loader(
        {'module': 'select'}
    )
    def receive(self):
        data = b""

        #Boucle pour récupérer l'ensemble des chunk d'un message
        while True:
            #Pour éviter les exceptions avec le socket non 
            #A voir si ça crash pas si on reçoit de gros fichiers
            ready_to_read, _, _ = select.select([self.connexion], [], [], 1)
            if ready_to_read:
                chunk = self.connexion.recv(2048)

                if chunk and len(chunk)<2048:
                    return data+chunk

                if not chunk:
                    return data

                data += chunk


    #Déchiffrement du message du client
    @impmagic.loader(
        {'module': 'cryptography.hazmat.primitives.ciphers', 'submodule': ['Cipher', 'algorithms', 'modes']},
        {'module': 'cryptography.hazmat.backends', 'submodule': ['default_backend']},
        {'module': 'Crypto.Cipher', 'submodule': ['PKCS1_OAEP']}
    )
    def decrypt_data(self, message):
        iv = message[:16]
        sym_key_encrypted = message[16:272]
        ciphertext = message[272:]

        # Déchiffrement de la clé symétrique avec RSA
        decryptor = PKCS1_OAEP.new(self.keyP)
        sym_key = decryptor.decrypt(sym_key_encrypted)

        # Déchiffrement du fichier avec AES en mode CFB
        cipher = Cipher(algorithms.AES(sym_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        #ATTENTION: A changer si option d'envoi de fichier
        #return plaintext.decode()
        return plaintext


    #Envoi d'un message avec le tag bypass pour affichage sans traitement sur client
    def status(self, message):
        self.send({'method': 'messageUnblock', 'content': message})


    def get_name_user(self):
        if self.username:
            return f"User:{self.username}"
        else:
            return f"Thread:{self.name}"


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'time'},
        {'module': 'json'},
        {'module': 'hashlib'},
        {'module': 'traceback'},
        {'module': 'core.pack', 'submodule': ['pack', 'unpack']},
        {'module': 'app.display', 'submodule': ['logs']},
        {'module': 'datetime', 'submodule': ['datetime']},
        {'module': 'core.auth', 'submodule': ['get_token', 'authenticate', 'get_userid']},
        {'module': 'pony.orm', 'as': 'pony'},
        {'module': 'core.workspace', 'submodule': ['list_workspace', 'create_workspace', 'remove_workspace']},
        {'module': 'core.server.note', 'submodule': ['get_note']},
    )
    def run(self):
        disconnected = False

        try:
            while 1:
                try:
                    msgClient = self.receive()
                except Exception as err:
                    if self.killed:
                        logs(f"[Thread:{self.name}] - Arrêt du thread")
                    elif not disconnected:
                        logs(f"[Thread:{self.name}] - Erreur avec le client. Arret de la connexion: {err}", "error")
                    del_username(self.username)
                    break
                else:
                    if len(msgClient):
                        if self.key==None:
                            #{'method': 'setUsername', 'value': username}
                            msgClient = self.decrypt(msgClient.decode())
                            msgClient = json.loads(msgClient)

                            if msgClient['method']=="sendKey":    #Récupération de la clé publique du client
                                self.key = msgClient['content']
                                if ("-----BEGIN PUBLIC KEY-----" in self.key) and ("-----END PUBLIC KEY-----" in self.key):
                                    self.keyC = RSA.importKey(self.key)

                                    logs(f"[{self.get_name_user()}] - Clé public reçu")
                                    payload = {'method': 'sendKey', 'content': __main__.settings.PubKey.decode()}
                                    self.connexion.send(self.encrypt(json.dumps(payload).encode()))
                                    logs(f"[{self.get_name_user()}] - Connecté")

                                else:
                                    logs(f'[{self.get_name_user()}] - Clé public invalide', 'error')
                                    self.key=None
                                    self.connexion.send("00000")
                            
                            elif msgClient['method']=="welcome":    #Récupération de la clé publique du client grâce au token
                                logs(f"[{self.get_name_user()}] - Welcome")

                                if 'token' in msgClient and 'serverhash' in msgClient and 'clienthash' in msgClient:
                                    if msgClient['token'] in __main__.server.USER:
                                        if __main__.settings.serverhash != msgClient['serverhash']:
                                            payload = {'method': 'welcome', 'message': 'Mauvaise clé public du serveur', 'status': 0}
                                            logs(f"[{self.get_name_user()}] - Mauvaise clé public du serveur", "error")
                                        
                                        elif __main__.server.USER[msgClient['token']]['clienthash'] != msgClient['clienthash']:
                                            payload = {'method': 'welcome', 'message': 'Mauvaise clé public du client', 'status': 0}
                                            logs(f"[{self.get_name_user()}] - Mauvaise clé public du client", "error")

                                        else:
                                            payload = {'method': 'welcome', 'status': 1}
                                            logs(f"[{self.get_name_user()}] - Welcome valide", "success")
                                            self.key = __main__.server.USER[msgClient['token']]['pubkey']
                                            self.keyC = RSA.importKey(self.key)
                                            self.user_id = __main__.server.USER[msgClient['token']]['user_id']

                                    else:
                                        payload = {'method': 'welcome', 'message': 'Bad token', 'status': 2}
                                        logs(f"[{self.get_name_user()}] - Bad token", "error")

                                else:
                                    payload = {'method': 'welcome', 'message': 'Bad request', 'status': 0}
                                    logs(f"[{self.get_name_user()}] - Bad request", "error")

                                self.connexion.send(self.encrypt(json.dumps(payload).encode()))


                        elif self.key!=None:
                            message = self.decrypt_data(msgClient)
                            message = unpack(message, self.keyC)

                            payload = None

                            if 'token' in message:
                                if message['token'] in __main__.server.USER:
                                    self.username = __main__.server.USER[message['token']]['username']

                            #Commande spéciale
                            if message['method']=="status":
                                logs(f"[{self.get_name_user()}] - Récupération du statut", "info")
                                
                                payload = {'method': 'status', 'notes': 0}
                                
                                connected = False
                                if 'token' in message:
                                    if message['token'] in __main__.server.USER:
                                        connected = True

                                        token = message['token']

                                        if 'workspace' in __main__.server.USER[token]:
                                            payload['workspace'] = __main__.server.USER[token]['workspace']

                                        with pony.db_session:
                                            #note = pony.select(n for n in __main__.settings.orm.Note if n.creator_id == self.user_id)
                                            note = get_note(self.user_id)
                                            if note:
                                                payload['notes'] = len(note)
                                
                                payload['connected'] = connected

                            elif message['method']=="endSession":
                                disconnected = True

                            elif message['method']=="logout":
                                del_username(message['token'])
                                logs(f"[{self.get_name_user()}] - Déconnexion de la session", "info")
                                payload = {'method': 'notify', 'message': 'Déconnexion de la session', 'status_code': 'info'}
                            
                                #logs(f"[{self.get_name_user()}] - Demande de déconnexion reçue", "info")
                            #Commande spéciale

                            elif 'token' in message:
                                if message['token'] in __main__.server.USER:
                                    token = message['token']

                                    if message['method']=="workspace":
                                        if 'workspace' in message:
                                            if 'action' in message:
                                                if message['action']=="create":
                                                    logs(f"[{self.get_name_user()}] - Demande de création du workspace {message['workspace']}", "info")
                                                    status_code = create_workspace(self.username, message['workspace'])
                                                    if status_code:
                                                        logs(f"[{self.get_name_user()}] - Création du workspace {message['workspace']}", "success")
                                                        payload = {'method': 'notify', 'message': f"Création du workspace {message['workspace']}", 'status_code': 'success'}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - Erreur lors de la création du workspace {message['workspace']}", "error")
                                                        payload = {'method': 'notify', 'message': f"Erreur lors de la création du workspace {message['workspace']}", 'status_code': 'error'}
                                                
                                                elif message['action']=="remove":
                                                    logs(f"[{self.get_name_user()}] - Demande de suppression du workspace {message['workspace']}", "info")
                                                    status_code = remove_workspace(self.username, message['workspace'])
                                                    if status_code:
                                                        logs(f"[{self.get_name_user()}] - Suppression du workspace {message['workspace']}", "success")
                                                        payload = {'method': 'notify', 'message': f"Suppression du workspace {message['workspace']}", 'status_code': 'success'}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - Erreur lors de la suppression du workspace {message['workspace']}", "error")
                                                        payload = {'method': 'notify', 'message': f"Erreur lors de la suppression du workspace {message['workspace']}", 'status_code': 'error'}
                                            else:
                                                logs(f"[{self.get_name_user()}] - Demande de switch sur le workspace {message['workspace']}", "info")
                                                workspaces = list_workspace(self.username)

                                                if message['workspace'] in workspaces:
                                                    logs(f"[{self.get_name_user()}] - Switch sur le workspace {message['workspace']}", "success")
                                                    with pony.db_session:
                                                        user_db = __main__.settings.orm.User.get(id=self.user_id)
                                                        if user_db:
                                                            workspaces = user_db.workspace.split(",")

                                                            if message['workspace'] in workspaces:
                                                                __main__.server.USER[token]['workspace'] = message['workspace']
                                                                user_db.active_workspace = message['workspace']

                                                                pony.commit()

                                                                payload = {'method': 'notify', 'message': f"Workspace {message['workspace']} initialisé", 'status_code': 'success'}
                                                            else:
                                                                payload = {'method': 'notify', 'message': f"Workspace {message['workspace']} introuvable", 'status_code': 'error'}
                                                        
                                                        else:
                                                            payload = {'method': 'notify', 'message': f"Donnée introuvable dans la base", 'status_code': 'error'}

                                                else:
                                                    logs(f"[{self.get_name_user()}] - Le workspace {message['workspace']} n'existe pas", "error")
                                                    payload = {'method': 'notify', 'message': f"Le workspace {message['workspace']} n'existe pas", 'status_code': 'error'}

                                        else:
                                            logs(f"[{self.get_name_user()}] - Récupération de la liste des workspaces", "info")
                                            content = list_workspace(self.username)

                                            payload = {'method': 'workspace', 'content': content, 'active': __main__.server.USER[token]['workspace']}

                                    
                                    elif message['method']=="note":
                                        if 'action' in message and 'note' in message:
                                            with pony.db_session:
                                                if message['action'] == "add" and 'content' in message:
                                                    logs(f"[{self.get_name_user()}] - Demande de création de la note {message['note']}", "info")

                                                    #existing = pony.select(n for n in __main__.settings.orm.Note if n.title == message['note'] and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()
                                                    existing = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])
                                                    if existing:
                                                        logs(f"[{self.get_name_user()}] - La note {message['note']} existe déjà", "error")
                                                        payload = {'method': 'notify', 'message': 'Une note porte déjà ce nom', "status_code": "error"}
                                                    else:
                                                        try:
                                                            now = datetime.now()
                                                            __main__.settings.orm.Note(
                                                                title=message['note'],
                                                                content=message['content'],
                                                                created_at=now,
                                                                updated_at=now,
                                                                creator_id=self.user_id,
                                                                editor_id=self.user_id,
                                                                protected="",
                                                                workspace=__main__.server.USER[token]['workspace']
                                                            )
                                                            logs(f"[{self.get_name_user()}] - Note {message['note']} créée", "success")
                                                            payload = {'method': 'notify', 'message': 'Note sauvegardée', 'status_code': "success"}
                                                        except Exception as err:
                                                            logs(f"[{self.get_name_user()}] - Erreur lors de la création: {err}", "error")
                                                            payload = {'method': 'notify', 'message': 'Erreur lors de la création', 'status_code': "error"}


                                                elif message['action'] == "edit" and 'content' in message:
                                                    logs(f"[{self.get_name_user()}] - Demande d'édition de la note {message['note']}", "info")
                                                    
                                                    #note = pony.select(n for n in __main__.settings.orm.Note if n.title == message['note'] and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()
                                                    note = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])
                                                    if note:
                                                        try:
                                                            note.content = message['content']
                                                            note.updated_at = datetime.now()
                                                            note.editor_id = self.user_id
                                                            pony.commit()
                                                            logs(f"[{self.get_name_user()}] - Note {message['note']} sauvegardée", "success")
                                                            payload = {'method': 'notify', 'message': 'Note sauvegardée', 'status_code': "success"}
                                                        except Exception as err:
                                                            logs(f"[{self.get_name_user()}] - Erreur lors de la sauvegarde: {err}", "error")
                                                            payload = {'method': 'notify', 'message': 'Erreur lors de la sauvegarde', 'status_code': "error"}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - La note {message['note']} n'existe pas", "error")
                                                        payload = {'method': 'notify', 'message': "La note n'existe pas", 'status_code': "error"}

                                                elif message['action'] == "get":
                                                    logs(f"[{self.get_name_user()}] - Demande de récupération de la note {message['note']}", "info")

                                                    #note = pony.select(n for n in __main__.settings.orm.Note if n.title == message['note'] and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()
                                                    note = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])
                                                    if note:
                                                        if len(note.protected):
                                                            if 'password_hash' in message:
                                                                if note.protected==message['password_hash']:
                                                                    payload = {'method': 'note', 'content': note.content}
                                                                else:
                                                                    payload = {'method': 'notify', 'message': "Mot de passe incorrecte", 'status_code': "error"}

                                                            else:
                                                                payload = {'method': 'password_required', 'payload': message}

                                                        else:
                                                            payload = {'method': 'note', 'content': note.content}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - La note {message['note']} n'existe pas", "error")
                                                        payload = {'method': 'notify', 'message': "La note n'existe pas", 'status_code': "error"}

                                                elif message['action'] == "remove":
                                                    logs(f"[{self.get_name_user()}] - Demande de suppression de la note {message['note']}", "info")

                                                    #note = pony.select(n for n in __main__.settings.orm.Note if n.title == message['note'] and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()
                                                    note = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])
                                                    if note:
                                                        try:
                                                            note.delete()
                                                            payload = {'method': 'notify', 'message': "Note supprimée", "status_code": "success"}
                                                        except Exception as err:
                                                            logs(f"[{self.get_name_user()}] - Erreur lors de la suppression: {err}", "error")
                                                            payload = {'method': 'notify', 'message': 'Erreur lors de la suppression', 'status_code': "error"}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - La note {message['note']} n'existe pas", "error")
                                                        payload = {'method': 'notify', 'message': "La note n'existe pas", 'status_code': "error"}
                                                
                                                elif message['action'] == "list":
                                                    logs(f"[{self.get_name_user()}] - Demande de la liste des notes", "info")
                                                    titles = []

                                                    notes = get_note(self.user_id, __main__.server.USER[token]['workspace'])
                                                    for n in notes:
                                                        titles.append(n.title)

                                                    payload = {'method': 'list', 'notes': titles}

                                                elif message['action'] == "info":
                                                    logs(f"[{self.get_name_user()}] - Demande d'informations sur la note {message['note']}", "info")
                                                    
                                                    note_title = message['note']
                                                    #note = pony.select(n for n in __main__.settings.orm.Note if n.title == note_title and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()
                                                    note = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])

                                                    if note:
                                                        # Récupérer les noms d'utilisateur
                                                        creator_user = __main__.settings.orm.User.get(id=note.creator_id)
                                                        editor_user = __main__.settings.orm.User.get(id=note.editor_id)

                                                        creator_name = creator_user.username if creator_user else "Inconnu"
                                                        editor_name = editor_user.username if editor_user else "Inconnu"

                                                        # Gérer le protected (True si texte non vide par exemple)
                                                        is_protected = True if note.protected else False

                                                        # Gérer shared_with (séparer les IDs, récupérer les noms)
                                                        shared_with_list = []
                                                        if note.shared_with:
                                                            shared_ids = note.shared_with.split(",")  # suppose que c'est un string "1,2,3"
                                                            for uid in shared_ids:
                                                                shared_user = __main__.settings.orm.User.get(id=int(uid))
                                                                username = shared_user.username if shared_user else "Inconnu"
                                                                shared_with_list.append(username)

                                                        payload = {
                                                            'method': 'info',
                                                            'note': {
                                                                'title': note.title,
                                                                'created_at': note.created_at.isoformat(),
                                                                'updated_at': note.updated_at.isoformat(),
                                                                'creator_name': creator_name,
                                                                'editor_name': editor_name,
                                                                'protected': is_protected,
                                                                'shared_with': ", ".join(shared_with_list)
                                                            }
                                                        }
                                                    else:
                                                        payload = {'method': 'notify', 'message': "La note n'existe pas", 'status_code': "error"}
                                                
                                                elif message['action'] == "protect" and 'password_hash' in message:
                                                    logs(f"[{self.get_name_user()}] - Demande de protection de la note {message['note']}", "info")

                                                    #note = pony.select(n for n in __main__.settings.orm.Note if n.title == message['note'] and n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace']).first()

                                                    note = __main__.settings.orm.Note.get(title=message['note'], creator_id=self.user_id, workspace=__main__.server.USER[token]['workspace'])
                                                    if note:
                                                        if len(note.protected):
                                                            logs(f"[{self.get_name_user()}] - La note {message['note']} est déjà protégée", "error")
                                                            payload = {'method': 'notify', 'message': "La note est déjà protégée", 'status_code': "error"}

                                                        else:
                                                            note.protected = message['password_hash']
                                                            pony.commit()
                                                            payload = {'method': 'notify', 'message': "La note a été protégée", 'status_code': "success"}
                                                    else:
                                                        logs(f"[{self.get_name_user()}] - La note {message['note']} n'existe pas", "error")
                                                        payload = {'method': 'notify', 'message': "La note n'existe pas", 'status_code': "error"}

                                        elif 'action' in message:
                                            with pony.db_session:
                                                if message['action'] == "find" and 'pattern' in message:
                                                    logs(f"[{self.get_name_user()}] - Demande de recherche dans les notes", "info")

                                                    note_list = []

                                                    #notes = pony.select(n for n in __main__.settings.orm.Note if n.creator_id == self.user_id and n.workspace == __main__.server.USER[token]['workspace'])[:]
                                                    #notes = __main__.settings.orm.Note.select().filter(lambda n: n.creator_id == self.user_id).filter(lambda n: n.workspace == __main__.server.USER[token]['workspace'])[:]
                                                    
                                                    notes = get_note(self.user_id, __main__.server.USER[token]['workspace'])

                                                    for note in notes:
                                                        if message['pattern'] in note.content:
                                                            note_list.append(note.title)

                                                    if len(note_list):
                                                        payload = {'method': 'find', 'content': note_list}
                                                    else:
                                                        payload = {'method': 'notify', 'message': "Aucune note trouvée", 'status_code': "error"}

                                    else:
                                        logs(f"[{self.get_name_user()}] - Commande reçu >> {message['method']}", "info")
                                else:
                                    payload = {'method': 'notify', 'message': 'Bad token', 'status_code': 'error'}

                            else:
                                if message['method']=="authentication":    #Déclaration du nom d'utilisateur
                                    logs(f"[{self.get_name_user()}] - Demande d'authentification", "info")
                                    if 'username' in message and 'password' in message:
                                        if authenticate(message['username'], message['password']):
                                            nameu = message['username']
                                            self.username=nameu
                                            logs(f"[{self.get_name_user()}] - Utilisateur {self.username} identifié", "info")

                                            token = get_token(self.username)
                                            self.user_id = get_userid(self.username)

                                            active_workspace = 'default'
                                            with pony.db_session:
                                                user_db = __main__.settings.orm.User.get(id=self.user_id)
                                                if user_db:
                                                    active_workspace = user_db.active_workspace

                                            __main__.server.USER[token]['user_id'] = self.user_id
                                            __main__.server.USER[token]['workspace'] = active_workspace
                                            __main__.server.USER[token]['pubkey'] = self.key
                                            __main__.server.USER[token]['clienthash'] = hashlib.sha256(self.key.encode()).hexdigest()
                                            payload = {'method': 'setToken', 'content': token}
                                        else:
                                            logs(f"[{self.get_name_user()}] - Authentification echouée", "error")
                                            payload = {'method': 'notify', 'message': 'Authentification failed', 'status_code': 'error'}
                                    else:
                                        logs(f"[{self.get_name_user()}] - Bad request", "error")
                                        payload = {'method': 'notify', 'message': 'Bad request', 'status_code': 'error'}

                            if payload:
                                self.send(payload)

        except Exception as err:
            logs(traceback.format_exc(), "error")

        finally:
            self.connexion.close()
            del __main__.server.conn_client[self.name]

            logs(f"[{self.get_name_user()}] - Deconnecté", "info")


    #Récupération de l'id du thread en cours
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id


    #Permet l'arrêt du thread en cours
    @impmagic.loader(
        {'module': 'ctypes'},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def kill_thread(self):
        logs(f"[Thread:{self.name}] - Requête d'arrêt reçue", "info")
        del_username(self.username)
        self.killed = True
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        self.connexion.close()


#Thread qui attend la connexion d'un client
class ArgosServer():
    def __init__(self): 
        self.error = None

        self.USER = {}
        self.THREAD = []
        self.conn_client = {}


    @impmagic.loader(
        {'module': 'socket'},
        {'module': 'select'},
        {'module': 'traceback'},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def run(self):
        try:
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.bind((__main__.settings.host, __main__.settings.port))
            
            logs("Serveur prêt, en attente de requêtes", "info")
            mySocket.listen(5)
            mySocket.setblocking(False)

            while 1:
                ready_to_read, _, _ = select.select([mySocket], [], [], 1)
                if ready_to_read:
                    connexion, adresse = mySocket.accept()
                    th = ThreadClient(connexion)
                    th.start()
                    self.THREAD.append(th)
                    it = th.name
                    self.conn_client[th.name] = connexion

                    logs(f"[Thread:{th.name}] - Client connecté, adresse IP {adresse[0]}, port {adresse[1]}", "info")

        except Exception as err:
            logs(traceback.format_exc(), "error")
            self.error = traceback.format_exc()

        finally:
            logs("Envoi de la requête d'arrêt à l'ensemble des clients", "info")
            for client in self.THREAD:
                client.kill_thread()


    #Récupération de l'id du thread en cours
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id


    #Permet l'arrêt du thread en cours
    @impmagic.loader(
        {'module': 'ctypes'},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def kill_server(self):
        logs("Requête d'arrêt reçue", "info")
        
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)


@impmagic.loader(
        {'module': 'zpp_args'},
        {'module': 'core.server.settings', 'submodule': ['Settings']},
        {'module': 'core.server.note', 'submodule': ['get_note']},
    )
def run_server():
    parse = zpp_args.parser()
    parse.set_description("znote server")
    parse.set_argument(longname="create_user", description="Créer un utilisateur", default=False)
    parse.set_argument(longname="username", description="Spécifier le nom d'utilisateur", store="value", default=False)
    parse.set_argument(longname="password", description="Spécifier le mot de passe de l'utilisateur", store="value", default=False)
    parse.set_argument(longname="config", description="Spécifier le chemin du fichier de config", store="value", default=None)
    parse.set_argument(longname="init", description="Initialiser les paramètres de l'application", default=None)
    parameter, argument = parse.load()

    if argument!=None:
        __main__.settings = Settings(argument.config)


        if argument.init:
            __main__.settings.init_settings()

        else:
            __main__.settings.load_key()
            __main__.settings.load_db()

            if argument.create_user:
                from core.auth import create_user
                message = create_user(argument.username, argument.password)
                if message:
                    print(message)
            else:
                __main__.server = ArgosServer()
                __main__.server.run()


if __name__ == "__main__":
    run_server()
