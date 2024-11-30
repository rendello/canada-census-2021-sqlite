# Canada Census 2021 SQLite – Version `[VERSION]`

An unofficial consolidation of the Canada *Census Profile, 2021 Census of Population* into a SQLite database file.

The official downloads of the census profile are offered split into multiple multi-gigabyte textual files that are not possible to query directly, and are generally too large to load into memory for tools like Pandas. They are in the legacy `ISO-8859-1` (Latin 1) encoding, causing many issues with import tools, and their format is difficult to work with.

The SQLite database allows direct querying, and does not require the entire database to be loaded into memory at once.

---

The canonical Census Profile is offered by the Statistics Canada website in [English](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm) and [French](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=F) in CSV, TAB, and IVT formats for 35 sets of geographic levels, with or without confidence intervals. Of the $\( 2 \times 35 \times 3 \times 2 = 420 \)$ download options, this consolidation is based on:

- [English; No confidence intervals] `Canada, provinces, territories, census divisions (CDs), census subdivisions (CSDs) and dissemination areas (DAs)` [`TAB`]

The database is the *consolidation* of the six `TAB`  (tab separated values) files representing the regions `Atlantic`, `BritishColumbia`, `Ontario`, `Prairies`, `Quebec`, and `Territories` offered by the aforementioned download.  It is not a *consolidation* of *all data* offered by the Census Profile, as French data, confidence intervals, and the geographic levels of `CMA`, `CA`, `CT`, `ER`, `POPCTR`, `FED`, `DPL`, `ADA`, `FSA`, `Dissolved CSD`, and `HR` are not included in the current dataset.

---

Querying can be done on the view `cview`, which provides basically the same interface as the text files:

$$
\begin{aligned}
    \textbf{StatCan Column} &\quad \textbf{Database Column} \\
    \text{DGUID} &\to \text{dguid} \\
    \text{ALT\\_GEO\\_CODE} &\to \text{alt\\_geo\\_code} \\
    \text{GEO\\_LEVEL} &\to \text{geo\\_level\\_name} \\
    \text{GEO\\_NAME} &\to \text{geo\\_name} \\
    \text{CHARACTERISTIC\\_ID} &\to \text{characteristic\\_id} \\
    \text{CHARACTERISTIC\\_NAME} &\to \text{characteristic\\_description} \\
    \text{(no mapping)} &\to \text{characteristic\\_parent\\_id} \\
    \text{TNR\\_SF} &\to \text{tnr\\_sf} \\
    \text{TNR\\_LF} &\to \text{tnr\\_lf} \\
    \text{DATA\\_QUALITY\\_FLAG} &\to \text{data\\_quality\\_flag} \\
    \text{C1\\_COUNT\\_TOTAL} &\to \text{c1\\_count\\_total} \\
    \text{SYMBOL (C1)} &\to \text{c1\\_count\\_total\\_symbol} \\
    \text{C2\\_COUNT\\_MEN+} &\to \text{c2\\_count\\_men} \\
    \text{SYMBOL (C2)} &\to \text{c2\\_count\\_men\\_symbol} \\
    \text{C3\\_COUNT\\_WOMEN+} &\to \text{c3\\_count\\_women} \\
    \text{SYMBOL (C3)} &\to \text{c3\\_count\\_women\\_symbol} \\
    \text{C10\\_RATE\\_TOTAL} &\to \text{c10\\_rate\\_total} \\
    \text{SYMBOL (C10)} &\to \text{c10\\_rate\\_total\\_symbol} \\
    \text{C11\\_RATE\\_MEN+} &\to \text{c11\\_rate\\_men} \\
    \text{SYMBOL (C11)} &\to \text{c11\\_rate\\_men\\_symbol} \\
    \text{C12\\_RATE\\_WOMEN+} &\to \text{c12\\_rate\\_women} \\
    \text{SYMBOL (C12)} &\to \text{c12\\_rate\\_women\\_symbol} \\
\end{aligned}
$$

Empty cells in the TAB files are converted to `NULL`s in the database. Counts are stored as `REAL`s, floating-point values. This is subject to change.

Internally, the database follows this schema:

[!!! Put the picture here !!!]

---

## Download info:

### Version
- `[VERSION]`

### Compressed

- Format: `.zst` [ZStandard](https://github.com/facebook/zstd/releases) compressed file (Less common file format but very good compression ratio);
- Size: [COMPRESSED_SIZE];
- `SHA256` checksum: [COMPRESSED_CHECKSUM].

### Decompressed

- Format: `.sqlite3` [SQLite](https://www.sqlite.org/);
- Size: [DECOMPRESSED_SIZE];
- `SHA256` checksum: [DECOMPRESSED_CHECKSUM].