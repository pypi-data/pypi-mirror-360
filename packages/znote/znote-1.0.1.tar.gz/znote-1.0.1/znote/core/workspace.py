import impmagic


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'os'},
	{'module': 'pony.orm', 'submodule': ['db_session']}
)
def list_workspace(user):
	#create_workspace(user)

	with db_session:
		user_db = __main__.settings.orm.User.get(username=user)
		if user_db:
			return user_db.workspace.split(",")
	return []


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'os'},
	{'module': 'pony.orm', 'submodule': ['db_session', 'commit']}
)
def create_workspace(user, namespace):
	try:
		with db_session:
			user_db = __main__.settings.orm.User.get(username=user)
			if user_db:
				user_workspace = user_db.workspace.split(",")

				if namespace not in user_workspace:
					user_workspace.append(namespace)
					user_db.workspace = ",".join(user_workspace)

					commit()

					return True

		return False
	except:
		return False


@impmagic.loader(
	{'module': '__main__'},
	{'module': 'os'},
	{'module': 'shutil'},
	{'module': 'pony.orm', 'submodule': ['db_session', 'commit']}
)
def remove_workspace(user, namespace):
	try:
		with db_session:
			user_db = __main__.settings.orm.User.get(username=user)
			if user_db:
				user_workspace = user_db.workspace.split(",")

				if namespace in user_workspace:
					user_workspace.remove(namespace)
					user_db.workspace = ",".join(user_workspace)

					commit()

					return True

		return False
	except:
		return False