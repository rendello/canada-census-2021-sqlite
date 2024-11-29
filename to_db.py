
import re
import sqlite3


def strip_footnotes(s: str) -> str:
	m = re.match(r"^(.*?)(?:\s\(\d+\))?$", s)
	return m.group(1)


def latin1_to_utf8(s: str) -> str:
	return s.encode("utf8").decode("utf8")


class DescriptionState:
	_buffer: list
	_SEPERATOR: str

	def __init__(self):
		self._buffer = []
		self._SEPERATOR = ";"
		current_indent_level = 0

	@staticmethod
	def _indent_level(s: str) -> int:
		n = 0
		for c in s:
			if c == " ": n += 1
			else: break
		assert n % 2 == 0
		return int(n / 2)

	def add_description(self, cid: str, description: str) -> None:
		assert self._SEPERATOR not in description
		level = self._indent_level(description)
		self._buffer = self._buffer[:level] + [(cid, description.strip())]

	def get_full_description(self) -> None:
		return f"{self._SEPERATOR} ".join([s for (_cid, s) in self._buffer])

	def get_parent(self) -> int|None:
		try: return self._buffer[-2][0]
		except IndexError: return None

if __name__ == "__main__":
	l = []
	d = DescriptionState()
	with open("characteristics.txt", encoding="latin1") as f:
		for latin1_line in f:
			line = strip_footnotes(latin1_to_utf8(latin1_line))

			cid, description = line.split("\t")

			d.add_description(cid, description)

			l.append((
				cid,
				d.get_full_description(),
			 	d.get_parent()
			 ))

	con = sqlite3.connect("data.sqlite3")
	cur = con.cursor()
	cur.execute("PRAGMA journal_mode = WAL;")
	cur.execute("PRAGMA foreign_keys = TRUE;")
	cur.execute(
		"""CREATE TABLE characteristic (
			id INTEGER PRIMARY KEY,
			description TEXT NOT NULL UNIQUE,
			parent_id INTEGER
		) WITHOUT ROWID, STRICT;""")
	cur.executemany("INSERT INTO characteristic VALUES (?, ?, ?)", l)
	con.commit()
	cur.execute("PRAGMA OPTIMIZE;")

	con.close()


"""
	cur.execute("PRAGMA OPTIMIZE;")
	cur.execute("PRAGMA query_only = TRUE;")
	cur.execute("PRAGMA synchronous = 0;")
	cur.execute("PRAGMA journal_mode = OFF;")
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