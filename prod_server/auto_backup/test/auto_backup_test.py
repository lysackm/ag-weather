import os.path

from ..auto_backup import *
import shutil
import unittest
import filecmp


def reset_dats(backup_dir):
    # delete new backup dats in format
    shutil.rmtree(backup_dir)
    # delete files in test_dats
    shutil.rmtree("./auto_backup/test/test_dats")
    # copy files from test_dats_backup to test_dats
    shutil.copytree("./auto_backup/test/test_dats_backup", "./auto_backup/test/test_dats")


class TestCreateBackup(unittest.TestCase):
    def test_backup_creation(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = False
        create_backup = CreateBackup(file_regex, files, dats_dir, keep_split_start_date)
        create_backup.backup_dats()

        backup_dir = os.path.abspath(create_backup.backup_dir)
        self.assertTrue(os.path.isdir(backup_dir))

        for file in glob.glob("./test/test_dats/*.dat"):
            backup_file = file.replace("test/test_dats", ".dats")
            self.assertTrue(os.path.isdir(backup_file))
            self.assertTrue(filecmp.cmp(file, backup_file, shallow=False))

        reset_dats(backup_dir)

    def test_regex(self):
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = False

        file_regex = r".*60\.dat"
        create_backup = CreateBackup(file_regex, files, dats_dir, keep_split_start_date)
        regex_files_60 = ['./auto_backup/test/test_dats\\alexander60.dat', './auto_backup/test/test_dats\\bede2_60.dat',
                          './auto_backup/test/test_dats\\carman60.dat']
        self.assertEqual(regex_files_60, create_backup.get_dat_files_regex())

        file_regex = r"\\MB\\(.+)\.dat"
        create_backup = CreateBackup(file_regex, files, dats_dir, keep_split_start_date)
        regex_files_MB = ['./auto_backup/test/test_dats\\MB\\MB10.dat']
        self.assertEqual(regex_files_MB, create_backup.get_dat_files_regex())

        file_regex = r".*WG15\.dat"
        create_backup = CreateBackup(file_regex, files, dats_dir, keep_split_start_date)
        regex_files_WG = ['./auto_backup/test/test_dats\\alexanderWG15.dat',
                          './auto_backup/test/test_dats\\bede2_WG15.dat',
                          './auto_backup/test/test_dats\\carmanWG15.dat']
        self.assertEqual(regex_files_WG, create_backup.get_dat_files_regex())

    def test_keep_date_with_previous_lines(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = True
        previous_lines = 10
        create_backup = CreateBackupSavePreviousRows(file_regex, files, dats_dir, keep_split_start_date, previous_lines)
        create_backup.backup_dats()

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            previous_line_count = 0
            saved_date_count = 0
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    if re.search(r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}", line[1:20]):
                        saved_date_count += 1
                    else:
                        previous_line_count += 1

            self.assertEqual(10, previous_line_count)
            self.assertTrue(saved_date_count > 0)
        reset_dats(backup_dir)

    def test_not_keep_date_with_previous_lines(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = False
        previous_lines = 10
        create_backup = CreateBackupSavePreviousRows(file_regex, files, dats_dir, keep_split_start_date, previous_lines)

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            previous_line_count = 0
            saved_date_count = 0
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    if re.search(r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}", line[1:20]):
                        saved_date_count += 1
                    else:
                        previous_line_count += 1

            self.assertEqual(10, previous_line_count)
            self.assertEqual(0, saved_date_count)
        reset_dats(backup_dir)

    def test_keep_date_with_date_cut_off(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = True
        start_date = "2024-08-06 00:00:00"
        create_backup = CreateBackupSaveFromDate(file_regex, files, dats_dir, keep_split_start_date, start_date)

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            cut_off_count = 0
            saved_date_count = 0
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    if re.search(r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}", line[1:20]):
                        saved_date_count += 1
                    else:
                        cut_off_count += 1

            self.assertTrue(cut_off_count > 0)
            self.assertTrue(saved_date_count > 0)
        reset_dats(backup_dir)

    def test_not_keep_date_with_date_cut_off(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = False
        start_date = "2024-08-06 00:00:00"
        create_backup = CreateBackupSaveFromDate(file_regex, files, dats_dir, keep_split_start_date, start_date)

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            cut_off_count = 0
            saved_date_count = 0
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    if re.search(r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}", line[1:20]):
                        saved_date_count += 1
                    else:
                        cut_off_count += 1

            self.assertTrue(cut_off_count > 0)
            self.assertEqual(0, saved_date_count)
        reset_dats(backup_dir)

    def test_save_previous_lines(self):
        file_regex = ".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        keep_split_start_date = False
        previous_rows = 10
        create_backup = CreateBackupSavePreviousRows(file_regex, files, dats_dir, keep_split_start_date, previous_rows)

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                self.assertEqual(12, len(lines))

        reset_dats(backup_dir)

    def test_save_previous_rows(self):
        file_regex = r".*"
        files = ""
        dats_dir = "./auto_backup/test/test_dats/"
        start_date = "2024-08-06 00:00:00"
        create_backup = CreateBackupSaveFromDate(file_regex, files, dats_dir, False, start_date)

        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    self.assertTrue(start_date <= line[1:20])

        reset_dats(backup_dir)

        create_backup = CreateBackupSaveFromDate(file_regex, files, dats_dir, True, start_date)
        backup_dir = os.path.abspath(create_backup.backup_dir)
        create_backup.backup_dats()
        create_backup.clear_dats_data()

        for file in glob.glob("./auto_backup/test/test_dats/*.dat"):
            with open(file, "r") as dat_file:
                lines = dat_file.readlines()
                for line in lines[2:]:
                    self.assertTrue(start_date <= line[1:20] or
                                    re.search(r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}", line[1:20]))

        reset_dats(backup_dir)


if __name__ == "__main__":
    unittest.main()
