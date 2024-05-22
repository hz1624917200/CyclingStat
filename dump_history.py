from pywxdump import VERSION_LIST, wx_info, decrypt_merge, dbpreprocess
import json
import os

from typing import Tuple

WORKDIR = "./workdir"


# get user info from cache or a running wx instance
def get_user_info(refresh: bool = False) -> dict[str, str]:
	# try to read from cache in the workdir
	if os.path.exists(WORKDIR + "/user_info.json") and not refresh:
		with open(WORKDIR + "/user_info.json", "r") as f:
			return json.load(f)
	# if not exists, read from the wx_info
	info: dict[str, str] = wx_info.read_info(VERSION_LIST, is_logging=True)[0]
	# delete some useless keys
	for key in ["pid", "version", "mail"]:
		if key not in info:
			raise ValueError(f"Key {key} not found in the wx_info")
		del info[key]
	# write to cache
	with open(WORKDIR + "/user_info.json", "w") as f:
		json.dump(info, f)
	return info

# decrypt the wx db and merge it
def decrypt_db(user_info: dict[str, str]) -> None:
	res, db_path = decrypt_merge(user_info["filePath"], user_info["key"], f"{WORKDIR}/decrypted", db_type=["MSG", "MicroMsg"])
	if res == False:
		raise ValueError("Failed to decrypt the wx db")
	print(f"Decrypted db path: {db_path}")

if __name__ == "__main__":
	user_info = get_user_info() # first get the user info
	decrypt_db(user_info) # then decrypt the wx db
	dbpreprocess.ParsingMSG
	pass