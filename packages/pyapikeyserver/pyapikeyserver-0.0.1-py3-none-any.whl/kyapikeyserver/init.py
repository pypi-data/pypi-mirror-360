from kyapikeyserver.server import sync_user
from ahserver.serverenv import ServerEnv

def load_kyapikeyserver():
	env = ServerEnv()
	env.sync_user = sysnc_user

