"
					LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Data\\historical\\clean\\alexander15.txt'
					IGNORE INTO TABLE data_15
					FIELDS TERMINATED BY ','
					ENCLOSED BY '""'
					ESCAPED BY '""'
					LINES TERMINATED BY '
'
					IGNORE 0 ROWS;
					"
