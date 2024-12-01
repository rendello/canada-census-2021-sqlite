
import sys
import sqlite3
from itertools import islice

CREATE_TABLE_CHARACTERISTIC = """
	CREATE TABLE characteristic (
		id INTEGER PRIMARY KEY,
		description TEXT NOT NULL UNIQUE,
		note INTEGER,
		parent_id INTEGER
	) WITHOUT ROWID, STRICT;
"""

INSERT_CHARACTERISTIC_VALUES = """
	INSERT INTO characteristic (
		id, description, note, parent_id
	) VALUES (?, ?, ?, ?);
"""

CREATE_TABLE_SYMBOL = """
	CREATE TABLE symbol (
		representation TEXT PRIMARY KEY,
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

CREATE_TABLE_GEO_LEVEL = """
	CREATE TABLE geo_level (
		id INTEGER PRIMARY KEY,
		name TEXT UNIQUE NOT NULL
	) STRICT;
"""

POPULATE_TABLE_GEO_LEVEL = """
	INSERT INTO geo_level(name) VALUES
		('Country'),
		('Territory'),
		('Census division'),
		('Census subdivision'),
		('Dissemination area');
"""

CREATE_TABLE_AREA = """
	CREATE TABLE area (
		id INTEGER PRIMARY KEY,
		dguid TEXT NOT NULL UNIQUE,
		alt_geo_code TEXT NOT NULL UNIQUE,
		geo_level_id INTEGER NOT NULL,
		geo_name TEXT NOT NULL,

		FOREIGN KEY (geo_level_id) REFERENCES geo_level(id)
	) STRICT;
"""

INSERT_AREA_VALUES = """
	INSERT OR IGNORE INTO area (
		dguid,
		alt_geo_code,
		geo_level_id,
		geo_name
	)
	VALUES (?,?,?,?);
"""

CREATE_TABLE_CENSUS = """
	CREATE TABLE census (
		area_id INTEGER NOT NULL,
		characteristic_id INTEGER NOT NULL,
		tnr_sf REAL NOT NULL,
		tnr_lf REAL NOT NULL,
		data_quality_flag TEXT NOT NULL,
		c1_count_total REAL,
		c1_count_total_symbol TEXT,
		c2_count_men REAL,
		c2_count_men_symbol TEXT,
		c3_count_women REAL,
		c3_count_women_symbol TEXT,
		c10_rate_total REAL,
		c10_rate_total_symbol TEXT,
		c11_rate_men REAL,
		c11_rate_men_symbol TEXT,
		c12_rate_women REAL,
		c12_rate_women_symbol TEXT,

		PRIMARY KEY (area_id, characteristic_id),

		FOREIGN KEY(area_id) REFERENCES area(id),
		FOREIGN KEY(characteristic_id) REFERENCES characteristic(id)
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

CREATE_VIEW_CVIEW = """
	CREATE VIEW cview AS
	SELECT
	    dguid,
	    alt_geo_code,
	    geo_level.name AS geo_level_name,
	    geo_name,
	    characteristic_id,
	    description AS characteristic_description,
	    parent_id AS characteristic_parent_id,
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
	FROM census 
	JOIN characteristic ON census.characteristic_id = characteristic.id
	JOIN area ON census.area_id = area.id
	JOIN geo_level ON area.geo_level_id = geo_level.id;
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
	try: assert a == b
	except AssertionError as e:
		print(f"ASSERT EQUAL FAILURE: {a} != {b}", file=sys.stderr)
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

def geo_level_name_to_id(geo_level_name: str, cur) -> int|None:
	cur.execute("SELECT id FROM geo_level WHERE name = (?)", [geo_level_name])
	res = cur.fetchone()
	if res: return res[0]
	else: return None

class DescriptionContext:
	_buffer: list
	_SEPERATOR: str

	@staticmethod
	def _indent_level(s: str) -> int:
		n = 0
		for c in s:
			if c == " ": n += 1
			else: break
		assert n % 2 == 0
		return int(n / 2)

	def __init__(self):
		self._buffer = []
		self._SEPERATOR = ";"

	def add_fragment(self, cid: str, description: str) -> None:
		assert self._SEPERATOR not in description
		level = self._indent_level(description)
		self._buffer = self._buffer[:level] + [(cid, description.strip())]

	def get_full_description(self) -> None:
		return f"{self._SEPERATOR} ".join([s for (_cid, s) in self._buffer])

	def get_parent(self) -> int|None:
		try: return self._buffer[-2][0]
		except IndexError: return None


def create_db(db_path: str):

	# The TSV format is highly redundant and allows any given row to stand on
	# its own, except with regard to characteristic descriptions. The descriptions
	# are indented, and their format is therefore recursive and relies on the rows
	# ahead of it. Here, the full descriptions are rebuilt and every characteristic
	# is associated with its parent's ID. The characteristics should be the same
	# across files, so we use the first one.
	path = PATHS[0]
	print(f"Processing characteristics from `{path}`.")

	dc = DescriptionContext()
	last_cid = 0
	characteristics = []

	with open(path, encoding="latin1") as f:
		next(f) # Skip header

		for line in f:
			p_line = latin1_to_utf8(line).rstrip("\n")
			split = split_line(p_line)

			cid = split[CHARACTERISTIC_ID]
			fragment = split[CHARACTERISTIC_NAME]
			note = split[CHARACTERISTIC_NOTE]

			if last_cid > int(cid):
				break
			else:
				last_cid = int(cid)

			dc.add_fragment(cid, fragment)

			characteristics.append((
				cid,
				dc.get_full_description(),
				nonempty_str_or_none(note),
			 	dc.get_parent()
			 ))

	con = sqlite3.connect(db_path)
	cur = con.cursor()
	cur.execute("PRAGMA foreign_keys = TRUE;")
	cur.execute("PRAGMA synchronous = OFF")
	cur.execute("PRAGMA journal_mode = MEMORY")
	cur.execute("PRAGMA temp_store = MEMORY")
	cur.execute("PRAGMA page_size = 65536")
	cur.execute("PRAGMA locking_mode = EXCLUSIVE")

	cur.execute(CREATE_TABLE_CHARACTERISTIC)
	cur.executemany(INSERT_CHARACTERISTIC_VALUES, characteristics)

	cur.execute(CREATE_TABLE_SYMBOL)
	cur.execute(POPULATE_TABLE_SYMBOL)

	cur.execute(CREATE_TABLE_GEO_LEVEL)
	cur.execute(POPULATE_TABLE_GEO_LEVEL)

	cur.execute(CREATE_TABLE_AREA)
	cur.execute(CREATE_TABLE_CENSUS)

	cur.execute(CREATE_VIEW_CVIEW)

	cur.execute("PRAGMA OPTIMIZE;")

	for path in PATHS:
		print(f"Processing `{path}`.")
		with open(path, encoding="latin1") as f:
			next(f) # Skip header

			while True:
				census_data = []
				for line in islice(f, BATCH_SIZE):
					p_line = latin1_to_utf8(line).rstrip("\n")
					split = split_line(p_line)

					maybe_area_id = dguid_to_area_id(split[DGUID], cur)
					if not maybe_area_id:
						geo_level_id = geo_level_name_to_id(split[GEO_LEVEL], cur)

						cur.execute(INSERT_AREA_VALUES, (
							split[DGUID],
							split[ALT_GEO_CODE],
							geo_level_id,
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
						nonempty_str_or_none(split[C1_COUNT_TOTAL_SYMBOL].strip()),
						nonempty_str_or_none(split[C2_COUNT_MEN]),
						nonempty_str_or_none(split[C2_COUNT_MEN_SYMBOL].strip()),
						nonempty_str_or_none(split[C3_COUNT_WOMEN]),
						nonempty_str_or_none(split[C3_COUNT_WOMEN_SYMBOL].strip()),
						nonempty_str_or_none(split[C10_RATE_TOTAL]),
						nonempty_str_or_none(split[C10_RATE_TOTAL_SYMBOL].strip()),
						nonempty_str_or_none(split[C11_RATE_MEN]),
						nonempty_str_or_none(split[C11_RATE_MEN_SYMBOL].strip()),
						nonempty_str_or_none(split[C12_RATE_WOMEN]),
						nonempty_str_or_none(split[C12_RATE_WOMEN_SYMBOL].strip())
					))

				if census_data == []:
					break

				cur.executemany(INSERT_CENSUS_VALUES, census_data)
				# try:
				# 	cur.executemany(INSERT_CENSUS_VALUES, census_data)
				# except sqlite3.IntegrityError as e:
				# 	print(census_data)
				# 	raise e

				con.commit()
				census_data = []

	con.close()


if __name__ == "__main__":
	create_db("data.sqlite3")