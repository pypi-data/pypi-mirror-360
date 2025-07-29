import __main__
import impmagic


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'base64'},
	{'module': 'secrets'}
)
def get_token(username):
	length = 32
	# Génère un token binaire aléatoire
	token_bytes = secrets.token_bytes(length)
	# Encode le token en base64 pour qu'il soit lisible et transmissible
	token = base64.urlsafe_b64encode(token_bytes).rstrip(b'=').decode('utf-8')

	user_data = {
		'username': username,
	}

	__main__.server.USER[token] = user_data

	return token


@impmagic.loader(
	{'module': 'hashlib', 'submodule': ['sha256']}
)
def hash_password(password):
	return sha256(password.encode("utf-8")).hexdigest()


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'pony.orm', 'submodule': ['db_session']}
)
def authenticate(username, password):
	with db_session:
		user = __main__.settings.orm.User.get(username=username)
		if user and user.password_hash == hash_password(password):
			return True
		return False


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'pony.orm', 'submodule': ['db_session']}
)
def get_userid(username):
	with db_session:
		user = __main__.settings.orm.User.get(username=username)
		if user:
			return user.id
	return None


#Création d'un nouvel utilisateur
@impmagic.loader(
	{'module': '__main__'},
	{'module': 'datetime', 'submodule': ['datetime']},
	{'module': 'pony.orm', 'submodule': ['db_session', 'commit']}
)
def create_user(username, password):
	with db_session:
		if not __main__.settings.orm.User.get(username=username):
			__main__.settings.orm.User(username=username, password_hash=hash_password(password), created_at=datetime.utcnow())
			commit()

			return ""
		else:
			return "User already exist"