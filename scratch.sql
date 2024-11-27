"""
X	CENSUS_YEAR
T	DGUID
T	ALT_GEO_CODE
T	GEO_LEVEL
T	GEO_NAME
	TNR_SF
	TNR_LF
	DATA_QUALITY_FLAG
	CHARACTERISTIC_ID
T	CHARACTERISTIC_NAME
	CHARACTERISTIC_NOTE
	C1_COUNT_TOTAL
	C1_COUNT_TOTAL_SYMBOL
	C2_COUNT_MEN+
	C2_COUNT_MEN+_SYMBOL
	C3_COUNT_WOMEN+
	C3_COUNT_WOMEN+_SYMBOL
	C10_RATE_TOTAL
	C10_RATE_TOTAL_SYMBOL
	C11_RATE_MEN+
	C11_RATE_MEN+_SYMBOL
	C12_RATE_WOMEN+
	C12_RATE_WOMEN+_SYMBOL
"""

CREATE TABLE characteristic (
	id INTEGER PRIMARY KEY,
	description TEXT NOT NULL UNIQUE,
	note TEXT,
	parent_id INTEGER
) WITHOUT ROWID, STRICT;


CREATE TABLE area (
	dguid TEXT PRIMARY KEY,
	alt_geo_code TEXT NOT NULL UNIQUE,
	geo_level TEXT NOT NULL,
	geo_name TEXT NOT NULL
) WITHOUT ROWID, STRICT;


CREATE TABLE census (
	dguid TEXT,
	characteristic_id INTEGER,
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
	FOREIGN KEY(dguid) REFERENCES area(dguid)
	FOREIGN KEY(characteristic_id) REFERENCES characteristic(id),
	PRIMARY KEY (dguid, characteristic_id)
) WITHOUT ROWID, STRICT;