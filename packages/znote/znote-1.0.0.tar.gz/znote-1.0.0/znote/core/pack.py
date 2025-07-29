import impmagic


#Création de la signature d'une donnée
@impmagic.loader(
    {'module': 'Crypto.Hash', 'submodule': ['SHA256']},
    {'module': 'Crypto.Signature','submodule': ['PKCS1_v1_5']}
)
def sign(data, privKey):
    if not isinstance(data, bytes):
        data = data.encode()

    digest = SHA256.new(data)

    signature = PKCS1_v1_5.new(privKey).sign(digest)

    return signature


#Vérification de la signature d'une donnée
@impmagic.loader(
    {'module': 'Crypto.Hash', 'submodule': ['SHA256']},
    {'module': 'Crypto.Signature','submodule': ['PKCS1_v1_5']}
)
def verify(data, signature, pubKey):
    if not isinstance(data, bytes):
        data = data.encode()
    
    digest = SHA256.new(data)

    verifier = PKCS1_v1_5.new(pubKey)
    return verifier.verify(digest, signature)


#Création du package à envoyer
@impmagic.loader(
    {'module': 'dill', 'submodule': ['dumps']}
)
def pack(data, privKey):
    #Transformation d'un objet en binaire
    data = dumps(data)

    #Création de la signature de ce binaire
    signature = sign(data, privKey)

    return signature+data


#Transformation du package en objet
@impmagic.loader(
    {'module': 'dill', 'submodule': ['loads']}
)
def unpack(data, pubKey):
    if len(data)>256:
        #Récupération de la signature dans le bloc de données
        signature, data = data[0:256], data[256:]

        #Vérifie si la signature est valide et provient du serveur
        if verify(data, signature, pubKey):
            try:
                #Si la signature est valide, conversion du binaire en objet
                return loads(data)
            except:
                print("Pickle invalid")
                return
        else:
            print("Signature check: Bad return")
            return
    else:
        print("Pickle invalid")
        return

