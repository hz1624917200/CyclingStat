from dump_history import dump_history
from stats import process_data, statistic
from utils import WORKDIR, GROUP_NAME, DUMP_RECORD, UPDATE_DB
import json
import os


if __name__ == "__main__":
	if not UPDATE_DB:
		msg_list, wxid2remark = dump_history(GROUP_NAME, update_db=False)
	else:
		# remove old db
		try:
			os.remove(WORKDIR + "/decrypted/merge_all.db")
		except FileNotFoundError:
			pass
		msg_list, wxid2remark = dump_history(GROUP_NAME, update_db=True)
	msg_record = process_data(msg_list, wxid2remark, start_date="5.21")

	# dump message record
	if DUMP_RECORD:
		with open(WORKDIR + "/message_record.json", "w", encoding="utf-8") as f:
			json.dump(msg_record, f, indent=4, ensure_ascii=False)
	
	# statistics
	stats = statistic(msg_record)
	sorted_stats = sorted(stats.values(), reverse=True)
	for stat in sorted_stats:
		print(stat)
	pass