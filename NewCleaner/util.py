import log
import os, shutil

def drop_suffix(s, suf):
	"Remove a suffix from a string, if it exists"
	
	if s.endswith(suf):
		return s[:-len(suf)]
	else:
		return s

def drop_prefix(s, pref):
	"Remove a prefix from a string, if it exists"
	
	if s.startswith(pref):
		return s[len(pref):]
	else:
		return s

def each_file(folder):
	"Yield a DataFile for each file in the given folder, recursively"
	
	# if the folder is really a file, os.walk does weird things
	if not os.path.isdir(folder):
		yield folder
		return
	
	for root, dirs, files in os.walk(folder):
		for file_name in files:
			yield os.path.join(root, file_name)

def file_exists(path):
	"Check if a file or folder exists with the given path"
	return os.path.isfile(path) or os.path.isdir(path)

class RenameException(Exception):
	pass
def rename(old_path, new_path, *args):
	# no sense in renaming a file to the same thing
	if new_path == old_path:
		return
	
	# windows won't let os.rename() change case, so we make the old file different
	if new_path.lower() == old_path.lower():
		os.rename(old_path, old_path + '~')
		old_path = old_path + '~'
	
	# actually rename the thing
	try:
		os.rename(old_path, new_path)
	except OSError as e:
		raise RenameException(e, old_path, new_path)
	
	log.renamed(old_path, new_path, *args)
	return new_path

def delete(path, *args):
	log.deleted(path, *args)
	if os.path.isdir(path):
		shutil.rmtree(path)
	else:
		os.unlink(path)

def try_delete(path, *args):
	if file_exists(path):
		delete(path, *args)

def try_rename(old_path, new_path, *args):
	if file_exists(old_path) and not file_exists(new_path):
		rename(old_path, new_path, *args)

def try_create_dir(directory):
	if not file_exists(directory):
		os.mkdir(directory)

def has_duplicates(xs):
	return len(set(xs)) != len(list(xs))

def copy(old_path, new_path, *args):
	shutil.copytree(old_path, new_path)
	log.main("copied", old_path, new_path, *map(str, args))

def file_empty(path):
	return os.path.getsize(path) == 0

def delete_folder_contents(folder, *args):
	for path in each_file(folder):
		try_delete(path)