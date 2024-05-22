# Process data and do statistics
from utils import COMMAND_TABLE, Command

# filter the msg list, only keep group note message
# @return: the filtered msg list, the last is the latest
def msg_filter(msg_list: list[dict[str, str]]) -> dict[str, int]:
	msg_list_filtered = [] 
	for msg in msg_list[::-1]:
		content = msg["content"]["msg"]
		if content[0] != "#":
			continue
		# check the split command
		command_endpos = content.find("\n")
		if (command_endpos == -1):
			command_endpos = len(content)
		command: Command = COMMAND_TABLE[content[1:command_endpos]]

		# dispatch the command
		if command == Command.MAIN:
			msg_list_filtered.append(msg)
		elif command == Command.SPLIT:
			# if msg["is_sender"] == 1:
				# break
			# current cycle is over TODO: change back to break
			continue

	return msg_list_filtered[::-1]


# process the data
# @return: group note mapping: {date: {remark: note}}
def process_data(msg_list: list[dict[str, str]], wxid2remark: dict[str, str]) -> dict[str, dict[str, str]]:
	msg_list = msg_filter(msg_list)
	group_notes: dict[str, list[str]] = {}
	record: dict[str, dict[str, str]] = {}
	for msg in msg_list:
		content = msg["content"]["msg"].split("\n")
		# print("\n".join(content))

		# date is in line 2
		last_note: list[str] = []
		date = content[1]
		if date in group_notes:
			last_note = group_notes[date]	
		start = 2
		while start < len(content) and content[start] == "":
			start += 1
		content = content[start:]
		
		if len(last_note) + 1 <= len(content):
			# append a line in the notes
			if date not in record:
				record[date] = {}
			record[date][wxid2remark[msg["talker"]]] = content[-1]
		elif len(last_note) == len(content):
			# edit one line
			for i in range(3, len(content)):
				if last_note[i] != content[i]:
					record[date][wxid2remark[msg["talker"]]] = content[i]
		elif len(last_note) - 1 == len(content):
			# delete one line
			record[date].pop(wxid2remark[msg["talker"]])
		group_notes[date] = content

		pass
		# process the group note message
	pass