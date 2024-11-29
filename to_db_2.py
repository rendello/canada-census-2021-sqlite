import sqlite3
from itertools import islice

CREATE_TABLE_SYMBOL = """
	CREATE TABLE symbol (
		id INTEGER PRIMARY KEY,
		representation TEXT UNIQUE NOT NULL,
		description_en TEXT UNIQUE NOT NULL
	) STRICT;
"""

POPULATE_TABLE_SYMBOL = """
	INSERT INTO symbol(representation, description_en) VALUES
		('..', 'not available for a specific reference period'),
		('...', 'not applicable'),
		('E', 'use with caution'),
		('F', 'too unreliable to be published'),
		('r', 'revised'),
		('x', 'suppressed to meet the confidentiality requirements of the Statistics Act'),
		('rE', 'Revised. Use with caution.');
"""

CREATE_TABLE_AREA = """
	CREATE TABLE area (
		id INTEGER PRIMARY KEY,
		dguid TEXT NOT NULL UNIQUE,
		alt_geo_code TEXT NOT NULL UNIQUE,
		geo_level TEXT NOT NULL,
		geo_name TEXT NOT NULL
	) STRICT;
"""

CREATE_TABLE_CENSUS = """
	CREATE TABLE census (
		area_id INTEGER NOT NULL,
		characteristic_id INTEGER NOT NULL,
		tnr_sf REAL NOT NULL,
		tnr_lf REAL NOT NULL,
		data_quality_flag TEXT NOT NULL,
		c1_count_total REAL,
		c1_count_total_symbol INTEGER,
		c2_count_men REAL,
		c2_count_men_symbol INTEGER,
		c3_count_women REAL,
		c3_count_women_symbol INTEGER,
		c10_rate_total REAL,
		c10_rate_total_symbol INTEGER,
		c11_rate_men REAL,
		c11_rate_men_symbol INTEGER,
		c12_rate_women REAL,
		c12_rate_women_symbol INTEGER,

		PRIMARY KEY (area_id, characteristic_id),

		FOREIGN KEY(area_id) REFERENCES area(id),
		FOREIGN KEY(characteristic_id) REFERENCES characteristic(id),

		FOREIGN KEY(c1_count_total_symbol)	REFERENCES symbol(id),
		FOREIGN KEY(c2_count_men_symbol)	REFERENCES symbol(id),
		FOREIGN KEY(c3_count_women_symbol)	REFERENCES symbol(id),
		FOREIGN KEY(c10_rate_total_symbol)	REFERENCES symbol(id),
		FOREIGN KEY(c11_rate_men_symbol)	REFERENCES symbol(id),
		FOREIGN KEY(c12_rate_women_symbol)	REFERENCES symbol(id)
	) WITHOUT ROWID, STRICT;
"""

INSERT_CENSUS_VALUES = """
	INSERT OR IGNORE INTO census (
		area_id,
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

BATCH_SIZE = 1000

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
	split = s.split("\t")
	assert_eq(len(split), 23)
	return split

def nonempty_str_or_none(s: str) -> str|None:
	if s == "": return None
	else: return s

def dguid_to_area_id(dguid: str,  cur) -> int|None:
	cur.execute("SELECT id FROM area WHERE dguid = (?);", [dguid])
	res = cur.fetchone()
	if res: return res[0]
	else: return None

def symbol_to_symbol_id(symbol: str, cur) -> int|None:
	symbol = symbol.strip() # symbols sometimes have whitespace.
	if symbol == "": return None
	cur.execute("SELECT id FROM symbol WHERE representation = (?);", [symbol])
	try:
		return cur.fetchone()[0]
	except TypeError as e:
		print(f'"{symbol}"')
		raise e
	

if __name__ == "__main__":
	con = sqlite3.connect("data.sqlite3")
	cur = con.cursor()
	cur.execute("PRAGMA foreign_keys = TRUE;")
	con.execute("PRAGMA synchronous = OFF")
	con.execute("PRAGMA journal_mode = MEMORY")
	con.execute("PRAGMA temp_store = MEMORY")
	con.execute("PRAGMA page_size = 65536")
	con.execute("PRAGMA locking_mode = EXCLUSIVE")

	cur.execute(CREATE_TABLE_SYMBOL)
	cur.execute(POPULATE_TABLE_SYMBOL)

	cur.execute(CREATE_TABLE_AREA)
	cur.execute(CREATE_TABLE_CENSUS)

	for path in PATHS:
		print(f"Processing `{path}`.")
		with open(path, encoding="latin1") as f:
			next(f) # Skip header

			while True:
				census_data = []
				for line in islice(f, BATCH_SIZE):
					p_line = latin1_to_utf8(line).rstrip("\n")
					split = split_line(p_line)
					# print(split)

					maybe_area_id = dguid_to_area_id(split[DGUID], cur)
					if not maybe_area_id:
						cur.execute(INSERT_AREA_VALUES, (
							split[DGUID],
							split[ALT_GEO_CODE],
							split[GEO_LEVEL],
							split[GEO_NAME]
						))
						area_id = dguid_to_area_id(split[DGUID], cur)
					else:
						area_id = maybe_area_id

					census_data.append((
						area_id,
						split[CHARACTERISTIC_ID],
						split[TNR_SF],
						split[TNR_LF],
						split[DATA_QUALITY_FLAG],
						nonempty_str_or_none(split[C1_COUNT_TOTAL]),
						symbol_to_symbol_id(split[C1_COUNT_TOTAL_SYMBOL], cur),
						nonempty_str_or_none(split[C2_COUNT_MEN]),
						symbol_to_symbol_id(split[C2_COUNT_MEN_SYMBOL], cur),
						nonempty_str_or_none(split[C3_COUNT_WOMEN]),
						symbol_to_symbol_id(split[C3_COUNT_WOMEN_SYMBOL], cur),
						nonempty_str_or_none(split[C10_RATE_TOTAL]),
						symbol_to_symbol_id(split[C10_RATE_TOTAL_SYMBOL], cur),
						nonempty_str_or_none(split[C11_RATE_MEN]),
						symbol_to_symbol_id(split[C11_RATE_MEN_SYMBOL], cur),
						nonempty_str_or_none(split[C12_RATE_WOMEN]),
						symbol_to_symbol_id(split[C12_RATE_WOMEN_SYMBOL], cur)
					))

				if census_data == []:
					break

				# cur.executemany(INSERT_CENSUS_VALUES, census_data)
				try:
					cur.executemany(INSERT_CENSUS_VALUES, census_data)
				except sqlite3.IntegrityError as e:
					print(census_data)
					raise e

				con.commit()
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