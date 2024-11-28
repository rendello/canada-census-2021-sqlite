import sqlite3
from itertools import islice

CREATE_TABLE_AREA = """
	CREATE TABLE area (
		dguid TEXT PRIMARY KEY,
		alt_geo_code TEXT NOT NULL UNIQUE,
		geo_level TEXT NOT NULL,
		geo_name TEXT NOT NULL
	) WITHOUT ROWID, STRICT;
"""

CREATE_TABLE_CENSUS = """
	CREATE TABLE census (
		dguid TEXT,
		characteristic_id TEXT,
		tnr_sf TEXT,
		tnr_lf TEXT,
		data_quality_flag TEXT,
		c1_count_total TEXT,
		c1_count_total_symbol TEXT,
		c2_count_men TEXT,
		c2_count_men_symbol TEXT,
		c3_count_women TEXT,
		c3_count_women_symbol TEXT,
		c10_rate_total TEXT,
		c10_rate_total_symbol TEXT,
		c11_rate_men TEXT,
		c11_rate_men_symbol TEXT,
		c12_rate_women TEXT,
		c12_rate_women_symbol TEXT,
		FOREIGN KEY(dguid) REFERENCES area(dguid),
		FOREIGN KEY(characteristic_id) REFERENCES characteristic(id),
		PRIMARY KEY (dguid, characteristic_id)
	) WITHOUT ROWID, STRICT;
"""

INSERT_CENSUS_VALUES = """
	INSERT OR IGNORE INTO census (
		dguid,
		characteristic_id,
		tnr_sf,
		tnr_lf,
		data_quality_flag,
		c1_count_total,
		c1_count_total_symbol,
		c2_count_men,
		c2_count_men_symbol,
		c3_count_women,
		c3_count_women_symbol,
		c10_rate_total,
		c10_rate_total_symbol,
		c11_rate_men,
		c11_rate_men_symbol,
		c12_rate_women,
		c12_rate_women_symbol
	)

	VALUES
	(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
"""

INSERT_AREA_VALUES = """
INSERT OR IGNORE INTO area (
	dguid,
	alt_geo_code,
	geo_level,
	geo_name
)
VALUES (?,?,?,?);
"""

CENSUS_YEAR = 0
DGUID = 1
ALT_GEO_CODE = 2
GEO_LEVEL = 3
GEO_NAME = 4
TNR_SF = 5
TNR_LF = 6
DATA_QUALITY_FLAG = 7
CHARACTERISTIC_ID = 8
CHARACTERISTIC_NAME = 9
CHARACTERISTIC_NOTE = 10
C1_COUNT_TOTAL = 11
C1_COUNT_TOTAL_SYMBOL = 12
C2_COUNT_MEN = 13
C2_COUNT_MEN_SYMBOL = 14
C3_COUNT_WOMEN = 15
C3_COUNT_WOMEN_SYMBOL = 16
C10_RATE_TOTAL = 17
C10_RATE_TOTAL_SYMBOL = 18
C11_RATE_MEN = 19
C11_RATE_MEN_SYMBOL = 20
C12_RATE_WOMEN = 21
C12_RATE_WOMEN_SYMBOL = 22

BATCH_SIZE = 50000

PATHS = [
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_Atlantic.TAB",
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_BritishColumbia.TAB",
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_Ontario.TAB",
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_Prairies.TAB",
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_Quebec.TAB",
	"98-401-X2021006_eng_TAB/98-401-X2021006_English_TAB_data_Territories.TAB"
]

def assert_eq(a, b) -> None:
	try:
		assert a == b
	except AssertionError as e:
		print(f"ASSERT EQUAL FAILURE: {a} != {b}")
		raise e

def latin1_to_utf8(s: str) -> str:
	return s.encode("utf8").decode("utf8")

def split_line(s: str) -> list[str]:
	split = line.split("\t")
	assert_eq(len(split), 23)
	return split



if __name__ == "__main__":
	con = sqlite3.connect("data.sqlite3")
	cur = con.cursor()
	cur.execute("PRAGMA foreign_keys = TRUE;")
	con.execute("PRAGMA synchronous = OFF")
	con.execute("PRAGMA journal_mode = MEMORY")
	con.execute("PRAGMA temp_store = MEMORY")
	con.execute("PRAGMA page_size = 65536")
	con.execute("PRAGMA locking_mode = EXCLUSIVE")

	cur.execute(CREATE_TABLE_AREA)
	cur.execute(CREATE_TABLE_CENSUS)

	for path in PATHS:
		print(f"Processing `{path}`.")
		with open(path, encoding="latin1") as f:
			next(f) # Skip header

			while True:
				area_data = set()
				census_data = []
				for line in islice(f, BATCH_SIZE):
					split = split_line(line)

					area_data.add((
						split[DGUID],
						split[ALT_GEO_CODE],
						split[GEO_LEVEL],
						split[GEO_NAME]
					))

					census_data.append((
						split[DGUID],
						split[CHARACTERISTIC_ID],
						split[TNR_SF],
						split[TNR_LF],
						split[DATA_QUALITY_FLAG],
						split[C1_COUNT_TOTAL],
						split[C1_COUNT_TOTAL_SYMBOL],
						split[C2_COUNT_MEN],
						split[C2_COUNT_MEN_SYMBOL],
						split[C3_COUNT_WOMEN],
						split[C3_COUNT_WOMEN_SYMBOL],
						split[C10_RATE_TOTAL],
						split[C10_RATE_TOTAL_SYMBOL],
						split[C11_RATE_MEN],
						split[C11_RATE_MEN_SYMBOL],
						split[C12_RATE_WOMEN],
						split[C12_RATE_WOMEN_SYMBOL]
					))

				if census_data == []:
					assert_eq(area_data, set())
					break

				try:
					cur.executemany(INSERT_AREA_VALUES, list(area_data))
					cur.executemany(INSERT_CENSUS_VALUES, census_data)
				except sqlite3.IntegrityError:
					print([f"{d[0]}:{d[1]}" for d in census_data])
				con.commit()
				area_data = []
				census_data = []

	cur.execute("PRAGMA OPTIMIZE;")
	con.close()




"""
		dguid,
		characteristic_id,
		tnr_sf,
		tnr_lf,
		data_quality_flag,
		c1_count_total,
		c1_count_total_symbol,
		c2_count_men,
		c2_count_men_symbol,
		c3_count_women,
		c3_count_women_symbol,
		c10_rate_total,
		c10_rate_total_symbol,
		c11_rate_men,
		c11_rate_men_symbol,
		c12_rate_women,
		c12_rate_women_symbol
"""