import sqlite3
import os
import hashlib
import subprocess
from pathlib import Path

from eralchemy import render_er

from to_db import create_db


DB_NAME = "census.sqlite3"
COMPRESSED_NAME = DB_NAME + ".zst"


def checksum(path) -> str:
	with open(path, 'rb', buffering=0) as f:
		return hashlib.file_digest(f, 'sha256').hexdigest()


def file_size(path) -> str:
	size = Path(path).stat().st_size

	for unit in ["B", "KiB", "MiB", "GiB"]:
		if size < 1024.0 or unit == 'GiB':
			break
		size /= 1024.0
	return f"{size:.2f} {unit}"


def create_release(version: str):
	path = (Path("release") / version)
	staging = (Path("staging") / version)

	db_path = path / DB_NAME
	compressed_path = path / COMPRESSED_NAME
	diagram_path = path / "diagram.png"
	release_notes_path = path / "release_notes.md"

	path.mkdir(parents=True, exist_ok=True)
	staging.mkdir(parents=True, exist_ok=True)

	if not db_path.is_file():
		print("[CREATING DATABASE]")
		db_staging_path = staging / DB_NAME
		create_db(db_staging_path)
		os.rename(db_staging_path, db_path)
	else:
		print("[DATABASE EXISTS; SKIPPING]")


	if not compressed_path.is_file():
		print("[COMPRESSING DATABASE]")
		compressed_staging_path = staging / COMPRESSED_NAME
		try:
			subprocess.check_call(
				["zstd", str(db_path), "--ultra", "-3", "--long=windowLog", "-o", str(compressed_staging_path)]
			)
		except subprocess.CalledProcessError as e:
			print(e.returncode, e.output)
			raise e
		os.rename(compressed_staging_path, compressed_path)
	else:
		print("[COMPRESSED DATABASE EXISTS; SKIPPING]")

	if not diagram_path.is_file():
		print("[CREATING DIAGRAM]")
		render_er("sqlite:///" + str(db_path), str(diagram_path))
	else:
		print("[DIAGRAM EXISTS; SKIPPING]")

	if not release_notes_path.is_file():
		print("[GENERATING RELEASE NOTES]")
		with open("release_template.md", "r") as f:
			template = f.read()

		s = (template
			.replace("[!!VERSION]", version)
			.replace("[!!COMPRESSED_SIZE]", file_size(compressed_path))
			.replace("[!!COMPRESSED_CHECKSUM]", checksum(compressed_path))
			.replace("[!!DECOMPRESSED_SIZE]", file_size(db_path))
			.replace("[!!DECOMPRESSED_CHECKSUM]", checksum(db_path))
		)
		with open(release_notes_path, "w") as f:
			f.write(s)
	else:
		print("[RELEASE NOTES EXIST; SKIPPING]")