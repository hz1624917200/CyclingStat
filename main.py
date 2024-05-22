from dump_history import dump_history
from stats import process_data

if __name__ == "__main__":
	msg_list, wxid2remark = dump_history("北大车队23-24秋季正式队员群", update_db=True)
	# process_data(msg_list, wxid2remark)
	pass