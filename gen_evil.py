
import sqlite3

DB_PATH = "data copy.sqlite3"

con = sqlite3.connect(DB_PATH)
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

queries = []
for table in cursor.fetchall():
# for table in [("sqlite_stat1",)]:
	table_name = table[0]
	cursor.execute(f"PRAGMA table_info({table_name});")

	columns = [table_info[1] for table_info in cursor.fetchall()]


	queries.append(" UNION ALL ".join([f"SELECT {column} AS value FROM {table_name}" for column in columns]))
	# print(f"{s} UNION ")
print(" UNION ALL ".join(queries) + ";")


"""
CREATE VIEW cv AS
SELECT
    dguid,
    alt_geo_code,
    geo_level,
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
JOIN area ON census.area_id = area.id;

SELECT * FROM cv LIMIT 10;
"""

"""
SELECT  SUM(length(cast(dguid AS BLOB))) / 1024 FROM census;
OPT 7913
NON 8885

"""


"""
SELECT geo_name, c1_count_total FROM census
LEFT JOIN area ON census.dguid = area.dguid
LEFT JOIN characteristic ON characteristic_id = characteristic.id
WHERE area.geo_level = 'Census subdivision'
AND area.geo_name LIKE 'Toronto%'
AND characteristic_id = '390'
-- AND CAST(c1_count_total AS INTEGER) > 100
-- ORDER BY  CAST(c1_count_total AS INTEGER) DESC
; 

-- SELECT geo_name, c1_count_total, characteristic.description FROM census
-- LEFT JOIN area ON census.dguid = area.dguid
-- LEFT JOIN characteristic ON characteristic_id = characteristic.id
-- WHERE area.geo_name = 'Sherbrooke, Ville (V)'
-- AND characteristic_id = '390'
-- ;
"""


"""
WITH RECURSIVE ac AS (
	SELECT id, full_description, 1 depth, partial_description AS path
	FROM characteristics WHERE parent IS NULL
	UNION ALL
	SELECT characteristics.id, characteristics.full_description, depth + 1, concat(path, '; ', characteristics.partial_description)
	FROM ac
		INNER JOIN characteristics ON ac.id = characteristics.parent
)

SELECT full_description, path FROM ac where full_description == path;
"""