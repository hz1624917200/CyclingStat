# Process data and do statistics
from utils import COMMAND_TABLE, Command, Stat, DUMP_CSV, WORKDIR
import logging
import json

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
# @return: message record: {date: {remark: note}}
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
			for i in range(len(content)):
				if last_note[i] != content[i]:
					record[date][wxid2remark[msg["talker"]]] = content[i]
		elif len(last_note) - 1 == len(content):
			# delete one line
			record[date].pop(wxid2remark[msg["talker"]])
		group_notes[date] = content
	return record

# parse a single word
def parse_word(word: str, pos: int, kw: str) -> tuple[int, float]:
	distance: int = 0
	duration: int = 0
	digit_start = pos - 1
	while digit_start >= 0 and (word[digit_start].isdigit() or word[digit_start] == "."):
		digit_start -= 1
	if kw == "km" or kw == "k":
		distance = round(float(word[digit_start + 1:pos]))
	elif kw == "h" or kw == "hour":
		duration = float(word[digit_start + 1:pos])
	elif kw == "min":
		duration = float(word[digit_start + 1:pos]) / 60
	return distance, duration
	


# parse a message to distance and duration stats
# return: distance (km), duration (min)
def parse_message(msg: str) -> tuple[int , float]:
	KEYWORDS = {"km", "k", "h", "hour", "min"}

	def check_indoor(word: str) -> bool:
		INDOOR_KW = {"台子", "骑行台"}
		for indoor_kw in INDOOR_KW:
			pos = word.find(indoor_kw)
			if pos != -1:
				for kw in KEYWORDS:
					kw_pos = word.find(kw)
					if kw_pos >= 1 and kw_pos < pos and word[kw_pos - 1].isdigit():
						return False
				return True
		return False


	distance: int = 0
	duration: float = 0
	words = msg.split(" ")[2:]
	# test passed
	# words += ["abc15k+dx30k", "14", "k", "台子13", "min", "台子", "1.5", "h"]
	# words += ["台子", "1.5", "h"]
	# words += ["hdgy15k+台子3h"]
	indoor: bool = False
	for word_i in range(len(words)):
		word = words[word_i]
		if not indoor:
			indoor = check_indoor(word)
		for kw in KEYWORDS:
			pos = word.find(kw)
			while pos != -1:
				if pos == 0:
					if word_i == 0:
						break
					word = words[word_i - 1] + word
					pos = word.find(kw)
					continue
				elif word[pos - 1].isdigit():
					dis, dur = parse_word(word, pos, kw)
					if indoor and dur > 0:
						dis = round(dur * 32)
						dur = 0
						indoor = False
					distance += dis
					duration += dur
					if dis == 0 and dur == 0:
						logging.warning(f"parse may failed: {msg}: {word}")

				word = word[pos + len(kw):]
				if not indoor:
					indoor = check_indoor(word)
				pos = word.find(kw)

			# if kw in word:
			# 	logging.info(f"{msg}: {word}")
	return distance, duration


# parse message record to number statistics
# @return: statistics: {date: {remark: [distance, duration]}}
def parse_data(msg_record: dict[str, dict[str, str]]) -> dict[str, dict[str, tuple[int, float]]]:
	statistics = {}
	for date, record in msg_record.items():
		logging.debug(f"------------------------\ndate: {date}")
		statistics[date] = {}
		for remark, msg in record.items():
			distance, duration = parse_message(msg)
			logging.debug(f"{remark}: {msg} - {distance} km, {duration} h")
			statistics[date][remark] = (distance, duration)
	return statistics


# calculate the statistics of each group member, by remark
def statistic(msg_record: dict[str, dict[str, str]]) -> dict[str, Stat]:
	num_record = parse_data(msg_record)

	if DUMP_CSV:
		csv_file = open(WORKDIR + "/statistics.csv", "w", encoding="utf-8")
		csv_file.write("date,remark,distance,duration,message\n")
	statistics = {}
	for date, record in num_record.items():
		for remark, num in record.items():
			if remark not in statistics:
				statistics[remark] = Stat(remark)
			statistics[remark].append(num[0], num[1])
			if DUMP_CSV:
				csv_file.write(f"{date},{remark},{num[0]},{num[1]},{msg_record[date][remark]}\n")
	if DUMP_CSV:
		csv_file.close()
	return statistics