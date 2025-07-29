"""
Build an IUPAC/Synonym -> SMILES SQLite database from PubChem
and fall back to OPSIN for names not found locally.

New in this version
-------------------
- Downloads and ingests CID-Synonym-filtered.gz
- Adds a simple opsin_lookup() fallback
- locate_db() helper so user code can find the DB

Usage
-----
python build_db.py        # one-time build (3-4 GB disk, <6 GB RAM)
python -m i2s "ethyl 2-(dimethyl(p-tolyl)silyl)propanoate"
"""

from __future__ import annotations
import gzip, sqlite3, urllib.request, pathlib, sys, subprocess, shutil, os
from typing import Optional

# ---------------------------------------------------------------------------
# 0.  Where to keep big files?
# ---------------------------------------------------------------------------
# Use local data directory in the project
DATA_DIR      = pathlib.Path(__file__).parent.parent.parent / "data"
DL_DIR        = DATA_DIR / "pubchem"
DB_PATH       = DATA_DIR / "iupac2smiles.db"

BASE = "https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/"
FILES = {
    "CID-IUPAC.gz"           : "cid_iupac.gz",
    "CID-SMILES.gz"          : "cid_smiles.gz",
    "CID-Synonym-filtered.gz": "cid_synonym.gz",   # NEW
}

# ---------------------------------------------------------------------------
# 1.  Download
# ---------------------------------------------------------------------------
def download_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DL_DIR.mkdir(parents=True, exist_ok=True)
    for remote, local_name in FILES.items():
        local = DL_DIR / local_name
        if not local.exists():
            print(f"Downloading {remote}")
            urllib.request.urlretrieve(BASE + remote, local)
        else:
            print(f"[OK] {local_name} already present")

# ---------------------------------------------------------------------------
# 2.  Build DB (streaming, memory-safe)
# ---------------------------------------------------------------------------
def build_sqlite() -> None:
    db = sqlite3.connect(DB_PATH)
    c  = db.cursor()
    c.executescript("""
        PRAGMA journal_mode = OFF;
        PRAGMA synchronous   = OFF;
        CREATE TABLE IF NOT EXISTS x(
            name   TEXT PRIMARY KEY,   -- lower-case
            smiles TEXT NOT NULL
        );
    """)

    # 2a.  SMILES lookup dict  (CID -> SMILES)   ~1.3 GB -> <1 GB RAM
    print("Loading SMILES...")
    cid2smiles: dict[str, str] = {}
    with gzip.open(DL_DIR / "cid_smiles.gz", "rt", encoding="utf-8") as f:
        for line in f:
            cid, smiles = line.rstrip("\n").split("\t")
            cid2smiles[cid] = smiles

    # helper to flush batches
    batch: list[tuple[str, str]] = []
    def canonicalize(name: str) -> str:
        """Canonicalize name: lowercase, strip, collapse spaces"""
        return ' '.join(name.lower().split())
    
    def flush():
        if batch:
            c.executemany("INSERT OR IGNORE INTO x VALUES(?,?)", batch)
            db.commit()
            batch.clear()

    # 2b.  IUPAC table
    print("Merging IUPAC...")
    with gzip.open(DL_DIR / "cid_iupac.gz", "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            cid, iupac = line.rstrip("\n").split("\t")
            smiles = cid2smiles.get(cid)
            if smiles:
                batch.append((canonicalize(iupac), smiles))
            if len(batch) == 100_000:
                flush()
                print(f"   ... {n:,} IUPAC rows", end="\r")
    flush()

    # 2c.  Synonyms table  **NEW**
    print("\nAdding synonyms...")
    with gzip.open(DL_DIR / "cid_synonym.gz", "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            cid, syn = line.rstrip("\n").split("\t")
            smiles = cid2smiles.get(cid)
            if smiles:
                batch.append((canonicalize(syn), smiles))
            if len(batch) == 100_000:
                flush()
                if n % 1_000_000 == 0:
                    print(f"   ... {n:,} synonym rows", end="\r")
    flush()

    c.execute("CREATE INDEX IF NOT EXISTS idx_name ON x(name);")
    db.commit()
    print("Build complete")
    db.close()

# ---------------------------------------------------------------------------
# 3.  Lookup helpers
# ---------------------------------------------------------------------------
def locate_db(explicit: Optional[str] = None) -> pathlib.Path:
    """Return path to SQLite DB, or raise FileNotFoundError."""
    for p in (
        pathlib.Path(explicit) if explicit else None,
        DB_PATH,  # Primary location in project data folder
        pathlib.Path.cwd() / "data" / "iupac2smiles.db",
        pathlib.Path.home() / ".iupac2smiles.db",
    ):
        if p and p.exists():
            return p
    raise FileNotFoundError("iupac2smiles.db not found; run build_db.py")

def sqlite_lookup(name: str, db_path: pathlib.Path | str = DB_PATH) -> Optional[str]:
    # Canonicalize: lowercase, strip, collapse multiple spaces
    canonical = ' '.join(name.lower().split())
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT smiles FROM x WHERE name = ?", (canonical,)).fetchone()
        return row[0] if row else None

# ---------------------------------------------------------------------------
# 4.  OPSIN fallback  **NEW**
# ---------------------------------------------------------------------------
def check_opsin_available() -> bool:
    return shutil.which("opsin") is not None    # expects 'opsin' on PATH

def opsin_lookup(name: str) -> Optional[str]:
    """
    Convert an IUPAC name to SMILES via OPSIN CLI.
    Install with:  brew install opsin   (macOS) or
                   conda install -c conda-forge opsin or
                   download JAR: https://opsin.ch.cam.ac.uk
    """
    if not check_opsin_available():
        return None
    try:
        # OPSIN reads from stdin and outputs SMILES by default
        res = subprocess.run(
            ["opsin"],
            input=name,
            capture_output=True, text=True, check=True, timeout=10,
        )
        smiles = res.stdout.strip()
        return smiles or None
    except subprocess.SubprocessError:
        return None

def iupac_to_smiles(name: str, db_path: pathlib.Path | str | None = None) -> Optional[str]:
    db_path = locate_db(db_path) if db_path else locate_db()
    smi = sqlite_lookup(name, db_path)
    if smi:
        return smi
    # try OPSIN
    return opsin_lookup(name)

# ---------------------------------------------------------------------------
# 5.  CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage:")
        print("  build_db.py download      # fetch PubChem files")
        print("  build_db.py build         # create SQLite")
        print("  python -m i2s NAME        # (see below)")
    elif sys.argv[1] == "download":
        download_all()
    elif sys.argv[1] == "build":
        build_sqlite()
    else:
        # act like a tiny module:  python build_db.py "acetylsalicylic acid"
        q = " ".join(sys.argv[1:])
        print(iupac_to_smiles(q) or "Not found")