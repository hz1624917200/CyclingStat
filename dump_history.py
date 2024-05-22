from pywxdump import VERSION_LIST, wx_info, decrypt_merge, dbpreprocess
from utils import WORKDIR

import json
import os

# get user info from cache or a running wx instance
def get_user_info(refresh: bool = False) -> dict[str, str]:
	# try to read from cache in the workdir
	user_info_fname = WORKDIR + "/user_info.json"
	if os.path.exists(user_info_fname) and not refresh:
		with open(user_info_fname, "r") as f:
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
# @return: the path of the decrypted db
def decrypt_db(user_info: dict[str, str]) -> str:
	res, db_path = decrypt_merge(user_info["filePath"], user_info["key"], f"{WORKDIR}/decrypted", db_type=["MSG", "MicroMsg"])
	if res == False:
		raise ValueError("Failed to decrypt the wx db")
	print(f"Decrypted db path: {db_path}")
	return db_path

# Extract the chat history from specified chat
# @return: the message list and the wxid2remark dict
def extract_chat_history(db_path: str, name: str) -> tuple[list[dict[str, str]], dict[str, str]]:
	# extract the chat history
	parsing_micromsg = dbpreprocess.ParsingMicroMsg(db_path)
	parsing_msg = dbpreprocess.ParsingMSG(db_path)
	user_list = parsing_micromsg.user_list()
	user_nickname = {user["wxid"]: user["nickname"] for user in user_list}
	
	group_wxid = parsing_micromsg.user_list(name)
	if len(group_wxid) != 1:
		raise ValueError(f"Failed to get the chat name: {name}, has {len(group_wxid)} results")
	group_wxid = group_wxid[0]["wxid"]
	chatroom_info = parsing_micromsg.chatroom_list(group_wxid)[0]
	wxid2remark = chatroom_info["wxid2remark"]
	special_keys = ["系统", "我"]
	for key in special_keys:
		wxid2remark[key] = key
	for wxid in chatroom_info["UserNameList"]:
		if wxid not in wxid2remark:
			# find the nickname in user_list
			wxid2remark[wxid] = user_nickname[wxid]

	msg_list, _ = parsing_msg.msg_list(group_wxid, msg_type="1")
	# for msg in msg_list:
		# print(f"{wxid2remark[msg['talker']]}: {msg['content']['msg']}")
	return msg_list, wxid2remark
	

# Dump the chat history of the specified group, all in one
# ! Only import this function from external scripts
# @return: the message list and the wxid2remark dict
def dump_history(group_name: str, update_db: bool = True) -> tuple[list[dict[str, str]], dict[str, str]]:
	if update_db:
		user_info = get_user_info() # get user info
		db_path = decrypt_db(user_info)
	else:
		db_path = WORKDIR + "/decrypted/merge_all.db"
	# extract the chat history
	return extract_chat_history(db_path, group_name)

if __name__ == "__main__":
	dump_history("北大车队23-24秋季正式队员群", update_db=False)
	pass