import csv

main_log = csv.writer(open("log.csv", "w", newline=''))
def main(*args):
	args = tuple(map(str, args))
	print(",".join(args))
	main_log.writerow(args)

renamed_log = csv.writer(open("renamed.csv", "w", newline=''))
def renamed(*args):
	args = tuple(map(str, args))
	main_log.writerow(("renamed",) + args)
	renamed_log.writerow(args)

deleted_log = csv.writer(open("deleted.csv", "w", newline=''))
def deleted(*args):
	args = tuple(map(str, args))
	main_log.writerow(("deleted",) + args)
	deleted_log.writerow(args)

modified_log = csv.writer(open("modified.csv", "w", newline=''))
def modified(*args):
	args = tuple(map(str, args))
	main_log.writerow(("modified",) + args)
	modified_log.writerow(args)

query_log = csv.writer(open("query.sql", "w", newline=''))
def query(*args):
	query_log.writerow(map(str, args))

wg60_24_log = csv.writer(open("wg60_24.csv", "w", newline=''))
def wg60_24(*args):
	wg60_24_log.writerow(map(str, args))

def consec_val(*args):
	# note: opening consec_val_log in append mode
	log_file = open("consec_val.csv", "a")
	consec_val_log = csv.writer(log_file)
	consec_val_log.writerow(map(str, args))
	log_file.close()




