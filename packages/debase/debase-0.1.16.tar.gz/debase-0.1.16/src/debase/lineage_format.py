 #!/usr/bin/env python3
"""
lineage_flattener.py
====================
A **complete rewrite** of the original `lineage_format.py`, structured in the
same sectioned style as `enzyme_lineage_extractor.py`, but **without any non-ASCII
characters**. All input and output column names are declared once as top-level
constants to prevent accidental drift.

The tool reads an annotated CSV containing enzyme variant information (lineage,
sequences, reaction data, fitness, etc.) and produces a flat reaction table
(one row per product) suitable for robotic plate builders or downstream ML.

-------------------------------------------------------------------------------
SECTION GUIDE (grep-able):
  # === 1. CONFIG & CONSTANTS ===
  # === 2. DOMAIN MODELS ===
  # === 3. LOGGING HELPERS ===
  # === 4. CACHE & DB HELPERS ===
  # === 5. SEQUENCE / MUTATION HELPERS ===
  # === 6. SMILES CONVERSION HELPERS ===
  # === 7. FLATTENING CORE ===
  # === 8. PIPELINE ORCHESTRATOR ===
  # === 9. CLI ENTRYPOINT ===
-------------------------------------------------------------------------------
"""

# === 1. CONFIG & CONSTANTS ===================================================
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import pickle
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
from tqdm import tqdm

try:
    from rdkit import Chem  # type: ignore
    RDKIT_OK = True
except ImportError:  # pragma: no cover
    RDKIT_OK = False

# Input columns that MUST be present ------------------------------------------------
INPUT_REQUIRED: Tuple[str, ...] = (
    "enzyme_id",
    "substrate_iupac_list",    # preferred source for SMILES lookup
    "product_iupac_list",      # preferred source for SMILES lookup
)

# Alternative column names that can be used instead
COLUMN_ALIASES: Dict[str, str] = {
    "enzyme": "enzyme_id",     # Handle 'enzyme' as an alias for 'enzyme_id'
}

# Optional but recognized input fields ----------------------------------------------
OPTIONAL_INPUT: Tuple[str, ...] = (
    "parent_enzyme_id",
    "generation",
    "protein_sequence",
    "aa_sequence",
    "nucleotide_sequence",
    "nt_sequence",
    "ttn",
    "yield",
    "reaction_temperature",
    "reaction_ph",
    "reaction_other_conditions",
    "reaction_substrate_concentration",
    "cofactor_iupac_list",
    "cofactor_list",
    "ee",
    "data_type",               # either "lineage" or "substrate_scope"
    "substrate",               # fallback names
    "substrate_name",
    "compound",
    "product",
    "product_name",
)

# Output columns --------------------------------------------------------------------
OUTPUT_COLUMNS: Tuple[str, ...] = (
    "id",
    "barcode_plate",
    "plate",
    "well",
    "smiles_string",
    "smiles_reaction",
    "alignment_count",
    "alignment_probability",
    "nucleotide_mutation",
    "amino_acid_substitutions",
    "nt_sequence",
    "aa_sequence",
    "x_coordinate",
    "y_coordinate",
    "fitness_value",
    "cofactor",
    "reaction_condition",
    "ee",
    "additional_information",
)

# Plate layout constants -------------------------------------------------------------
PLATE_SIZE: int = 96
BARCODE_START: int = 1

# Batch / parallelism ----------------------------------------------------------------
MAX_WORKERS: int = min(32, (os.cpu_count() or 4) * 2)
BATCH_SIZE: int = 50

# Cache files ------------------------------------------------------------------------
CACHE_DIR: Path = Path(os.environ.get("LINEAGE_CACHE_DIR", "./.cache"))
SMILES_CACHE_FILE: Path = CACHE_DIR / "smiles_cache.pkl"
SUBSTRATE_CACHE_FILE: Path = CACHE_DIR / "substrate_smiles_cache.pkl"
CANONICAL_CACHE_FILE: Path = CACHE_DIR / "canonical_smiles_cache.pkl"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Local PubChem DB (optional) --------------------------------------------------------
PUBCHEM_DB_PATH: Path = Path(__file__).parent.parent.parent / "data" / "iupac2smiles.db"

# Miscellaneous ----------------------------------------------------------------------
WELL_ROWS: str = "ABCDEFGH"  # 8 rows, 12 cols => 96 wells


# === 2. DOMAIN MODELS ===============================================================
@dataclass
class VariantRecord:
    """Minimal representation of an enzyme variant row from the input CSV."""

    row: Dict[str, str]

    def __post_init__(self) -> None:
        # Apply column aliases
        for alias, canonical in COLUMN_ALIASES.items():
            if alias in self.row and canonical not in self.row:
                self.row[canonical] = self.row[alias]
        
        missing = [c for c in INPUT_REQUIRED if c not in self.row]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Convenience accessors ---------------------------------------------------------
    @property
    def eid(self) -> str:
        return str(self.row["enzyme_id"]).strip()

    @property
    def parent_id(self) -> str:
        return str(self.row.get("parent_enzyme_id", "")).strip()

    @property
    def generation(self) -> str:
        return str(self.row.get("generation", "")).strip()

    @property
    def aa_seq(self) -> str:
        return (
            str(self.row.get("protein_sequence", ""))
            or str(self.row.get("aa_sequence", ""))
        ).strip()

    @property
    def nt_seq(self) -> str:
        # First try to get actual NT sequence
        nt = (
            str(self.row.get("nucleotide_sequence", ""))
            or str(self.row.get("nt_sequence", ""))
        ).strip()
        
        # If no NT sequence but we have AA sequence, reverse translate
        if (not nt or nt == "nan") and self.aa_seq:
            nt = _rev_translate(self.aa_seq)
        
        return nt

    # Reaction-related -------------------------------------------------------------
    def substrate_iupac(self) -> List[str]:
        raw = str(self.row.get("substrate_iupac_list", "")).strip()
        return _split_list(raw)

    def product_iupac(self) -> List[str]:
        raw = str(self.row.get("product_iupac_list", "")).strip()
        return _split_list(raw)


    def ttn_or_yield(self) -> Optional[float]:
        for col in ("ttn", "yield"):
            val = self.row.get(col)
            if val is not None and pd.notna(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    continue
        return None


@dataclass
class FlatRow:
    """Row for the output CSV. Only validated on demand."""

    id: str
    barcode_plate: int
    plate: str
    well: str
    smiles_string: str
    smiles_reaction: str
    alignment_count: int = 1
    alignment_probability: float = 1.0
    nucleotide_mutation: str = ""
    amino_acid_substitutions: str = ""
    nt_sequence: str = ""
    aa_sequence: str = ""
    x_coordinate: str = ""
    y_coordinate: str = ""
    fitness_value: Optional[float] = None
    cofactor: str = ""
    reaction_condition: str = ""
    ee: str = ""
    additional_information: str = ""

    def as_dict(self) -> Dict[str, str]:
        data = {
            "id": self.id,
            "barcode_plate": self.barcode_plate,
            "plate": self.plate,
            "well": self.well,
            "smiles_string": self.smiles_string,
            "smiles_reaction": self.smiles_reaction,
            "alignment_count": self.alignment_count,
            "alignment_probability": self.alignment_probability,
            "nucleotide_mutation": self.nucleotide_mutation,
            "amino_acid_substitutions": self.amino_acid_substitutions,
            "nt_sequence": self.nt_sequence,
            "aa_sequence": self.aa_sequence,
            "x_coordinate": self.x_coordinate,
            "y_coordinate": self.y_coordinate,
            "fitness_value": self.fitness_value,
            "cofactor": self.cofactor,
            "reaction_condition": self.reaction_condition,
            "ee": self.ee,
            "additional_information": self.additional_information,
        }
        # Convert None to empty string for CSV friendliness
        return {k: ("" if v is None else v) for k, v in data.items()}


# === 3. LOGGING HELPERS =============================================================

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

log = get_logger(__name__)


# === 4. CACHE & DB HELPERS ==========================================================

def _load_pickle(path: Path) -> Dict[str, str]:
    if path.exists():
        try:
            with path.open("rb") as fh:
                return pickle.load(fh)
        except Exception as exc:  # pragma: no cover
            log.warning("Could not read cache %s: %s", path, exc)
    return {}


def _save_pickle(obj: Dict[str, str], path: Path) -> None:
    try:
        with path.open("wb") as fh:
            pickle.dump(obj, fh)
    except Exception as exc:  # pragma: no cover
        log.warning("Could not write cache %s: %s", path, exc)


SMILES_CACHE: Dict[str, str] = _load_pickle(SMILES_CACHE_FILE)
SUBSTRATE_CACHE: Dict[str, str] = _load_pickle(SUBSTRATE_CACHE_FILE)
CANONICAL_CACHE: Dict[str, str] = _load_pickle(CANONICAL_CACHE_FILE)


# --- Database lookup ---------------------------------------------------------------
class PubChemDB:
    """Very thin wrapper around a local SQLite mapping IUPAC -> SMILES."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._conn: Optional[sqlite3.Connection] = None
        if not self.path.exists():
            log.warning("Local PubChem DB not found at %s", self.path)

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.path))
        return self._conn

    def lookup(self, name: str) -> Optional[str]:
        if not self.path.exists():
            return None
        sql = "SELECT smiles FROM x WHERE name = ? LIMIT 1"
        try:
            # Create a new connection for thread safety
            conn = sqlite3.connect(str(self.path))
            cur = conn.execute(sql, (name.lower(),))
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception:  # pragma: no cover
            return None


PC_DB = PubChemDB(PUBCHEM_DB_PATH)


# === 5. SEQUENCE / MUTATION HELPERS ================================================

# Genetic code for naive reverse translation --------------------------------
CODON: Dict[str, str] = {
    # One representative codon per amino acid (simplified)
    "A": "GCT", "R": "CGT", "N": "AAT", "D": "GAT", "C": "TGT", "Q": "CAA",
    "E": "GAA", "G": "GGT", "H": "CAT", "I": "ATT", "L": "CTT", "K": "AAA",
    "M": "ATG", "F": "TTT", "P": "CCT", "S": "TCT", "T": "ACT", "W": "TGG",
    "Y": "TAT", "V": "GTT", "*": "TAA",
}


def _rev_translate(aa: str) -> str:
    """Rudimentary AA -> DNA translation (three-letter codon table above)."""
    return "".join(CODON.get(res, "NNN") for res in aa)


def _aa_mut(parent: str, child: str) -> str:
    """Return simple mutation descriptor P12V_P34L ... comparing AA sequences."""
    mutations = []
    for idx, (p, c) in enumerate(zip(parent, child), start=1):
        if p != c:
            mutations.append(f"{p}{idx}{c}")
    return "_".join(mutations)


def _nt_mut(parent_aa: str, child_aa: str, parent_nt: str = "", child_nt: str = "") -> str:
    """Return mutations at nucleotide level (uses reverse translation if needed)."""
    if parent_nt and child_nt and len(parent_nt) > 0 and len(child_nt) > 0:
        # Use actual nucleotide sequences if both are available
        muts = []
        for idx, (p, c) in enumerate(zip(parent_nt, child_nt), start=1):
            if p != c:
                muts.append(f"{p}{idx}{c}")
        return "_".join(muts)
    else:
        # Fall back to reverse translation from protein sequences
        p_seq = _rev_translate(parent_aa) if parent_aa else ""
        c_seq = _rev_translate(child_aa) if child_aa else ""
        muts = []
        for idx, (p, c) in enumerate(zip(p_seq, c_seq), start=1):
            if p != c:
                muts.append(f"{p}{idx}{c}")
        return "_".join(muts)


# === 6. SMILES CONVERSION HELPERS ==================================================

def _split_list(raw: str) -> List[str]:
    if not raw or str(raw).lower() == 'nan':
        return []
    return [s.strip() for s in raw.split(";") if s.strip() and s.strip().lower() != 'nan']


def _canonical_smiles(smiles: str) -> str:
    if not smiles or not RDKIT_OK:
        return smiles
    if smiles in CANONICAL_CACHE:
        return CANONICAL_CACHE[smiles]
    try:
        mol = Chem.MolFromSmiles(smiles)  # type: ignore[attr-defined]
        if mol:
            canon = Chem.MolToSmiles(mol, canonical=True)  # type: ignore[attr-defined]
            CANONICAL_CACHE[smiles] = canon
            return canon
    except Exception:  # pragma: no cover
        pass
    return smiles


def _name_to_smiles(name: str, is_substrate: bool) -> str:
    """Convert IUPAC (preferred) or plain name to SMILES with multi-tier lookup."""
    # NO CACHING - Always try fresh conversion
    
    # Filter out invalid values that shouldn't be converted
    if not name or name.lower() in ['nan', 'none', 'null', 'n/a', 'na', '']:
        return ""
    
    # 1. Local DB (fast, offline)
    db_smiles = PC_DB.lookup(name)
    if db_smiles:
        return db_smiles

    # 2. OPSIN (if installed) ---------------------------------------------------
    try:
        import subprocess

        # Use stdin to avoid shell interpretation issues with special characters
        result = subprocess.run(
            ["opsin", "-osmi"], input=name, capture_output=True, text=True, check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            # OPSIN output may include a header line, so get the last non-empty line
            lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
            if lines:
                opsin_smiles = lines[-1]
                return opsin_smiles
    except FileNotFoundError:
        pass  # OPSIN not installed

    # 3. PubChem PUG REST (online) ---------------------------------------------
    try:
        import requests

        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(name)}/property/IsomericSMILES/TXT"
        )
        resp = requests.get(url, timeout=10)
        if resp.ok:
            pug_smiles = resp.text.strip().split("\n")[0]
            return pug_smiles
    except Exception:  # pragma: no cover
        pass

    # Return empty string if all methods fail
    return ""


def _batch_convert(names: Sequence[str], is_substrate: bool) -> Dict[str, str]:
    """Convert a batch of names to SMILES in parallel."""
    out: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_name_to_smiles, n, is_substrate): n for n in names}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="SMILES"):
            name = futures[fut]
            try:
                result = fut.result()
                # Only store successful conversions
                if result:
                    out[name] = result
                else:
                    log.debug("SMILES conversion failed for %s", name)
            except Exception as exc:  # pragma: no cover
                log.debug("SMILES conversion exception for %s: %s", name, exc)
    return out


# === 7. FLATTENING CORE ============================================================

def _fill_missing_sequences(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing sequences in substrate scope entries from lineage entries."""
    # Create lookup for sequences by enzyme_id
    seq_lookup = {}
    
    # First pass: collect all available sequences from lineage entries
    for _, row in df.iterrows():
        if row.get("data_type") == "lineage" or pd.notna(row.get("protein_sequence")) or pd.notna(row.get("aa_sequence")):
            eid = str(row["enzyme_id"])
            aa_seq = str(row.get("protein_sequence", "")) or str(row.get("aa_sequence", ""))
            nt_seq = str(row.get("nucleotide_sequence", "")) or str(row.get("nt_sequence", ""))
            if aa_seq and aa_seq != "nan":
                seq_lookup[eid] = {
                    "aa_sequence": aa_seq,
                    "nt_sequence": nt_seq if nt_seq != "nan" else ""
                }
    
    # Second pass: fill missing sequences in substrate scope entries
    filled_count = 0
    for idx, row in df.iterrows():
        eid = str(row["enzyme_id"])
        
        # Check if this row needs sequence filling
        aa_seq = str(row.get("protein_sequence", "")) or str(row.get("aa_sequence", ""))
        if (not aa_seq or aa_seq == "nan") and eid in seq_lookup:
            df.at[idx, "protein_sequence"] = seq_lookup[eid]["aa_sequence"]
            df.at[idx, "aa_sequence"] = seq_lookup[eid]["aa_sequence"]
            if seq_lookup[eid]["nt_sequence"]:
                df.at[idx, "nucleotide_sequence"] = seq_lookup[eid]["nt_sequence"]
                df.at[idx, "nt_sequence"] = seq_lookup[eid]["nt_sequence"]
            filled_count += 1
    
    if filled_count > 0:
        log.info(f"Filled sequences for {filled_count} entries")
    
    return df

def _plate_and_well(index: int) -> Tuple[int, str, str]:
    """Return (barcode_plate, plate_name, well) for the given running index."""
    plate_number = index // PLATE_SIZE + BARCODE_START
    idx_in_plate = index % PLATE_SIZE
    row = WELL_ROWS[idx_in_plate // 12]
    col = idx_in_plate % 12 + 1
    well = f"{row}{col:02d}"
    plate_name = f"Plate_{plate_number}"
    return plate_number, plate_name, well


def _root_enzyme_id(eid: str, idmap: Dict[str, Dict[str, str]], lineage_roots: Dict[str, str]) -> str:
    """Get root enzyme id, falling back to generation 0 ancestor or self."""
    if eid in lineage_roots:
        return lineage_roots[eid]
    cur = eid
    seen: set[str] = set()
    while cur and cur not in seen:
        seen.add(cur)
        row = idmap.get(cur, {})
        # Look for generation 0 as the root
        if str(row.get("generation", "")).strip() == "0":
            return cur
        parent = row.get("parent_enzyme_id", "")
        if not parent:
            # If no parent, this is the root
            return cur
        cur = parent
    return eid


def _generate_lineage_roots(df: pd.DataFrame) -> Dict[str, str]:
    """Infer lineage roots using generation numbers and simple sequence similarity."""
    idmap: Dict[str, Dict[str, str]] = {str(r["enzyme_id"]): r for _, r in df.iterrows()}
    roots: Dict[str, str] = {}
    # Look for generation 0 as the root
    gen0 = {r["enzyme_id"] for _, r in df.iterrows() if str(r.get("generation", "")).strip() == "0"}
    # If no gen0 found, fall back to gen1
    if not gen0:
        gen0 = {r["enzyme_id"] for _, r in df.iterrows() if str(r.get("generation", "")).strip() == "1"}

    def _seq_sim(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / max(len(a), len(b))

    for _, row in df.iterrows():
        eid = row["enzyme_id"]
        if eid in gen0:
            roots[eid] = eid
            continue
        cur = eid
        lineage_path: List[str] = []
        while cur and cur not in lineage_path:
            lineage_path.append(cur)
            cur_row = idmap.get(cur, {})
            parent = cur_row.get("parent_enzyme_id", "")
            if not parent:
                break
            cur = parent
        # If we found a gen0 ancestor in the path, use it
        for anc in reversed(lineage_path):
            if anc in gen0:
                roots[eid] = anc
                break
        else:
            # Fall back to closest by sequence similarity among gen0
            aa_seq = (
                str(row.get("protein_sequence", "")) or str(row.get("aa_sequence", ""))
            )
            best_match = None
            best_sim = 0.0
            for g0 in gen0:
                g0_row = idmap[g0]
                g0_seq = (
                    str(g0_row.get("protein_sequence", ""))
                    or str(g0_row.get("aa_sequence", ""))
                )
                sim = _seq_sim(aa_seq, g0_seq)
                if sim > best_sim:
                    best_sim, best_match = sim, g0
            roots[eid] = best_match if best_match else eid
    return roots


def flatten_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Main public API: returns a DataFrame in the flat output format."""
    # Apply column aliases to the dataframe
    for alias, canonical in COLUMN_ALIASES.items():
        if alias in df.columns and canonical not in df.columns:
            df = df.rename(columns={alias: canonical})
    
    # Fill missing sequences in substrate scope entries from lineage data
    df = _fill_missing_sequences(df)
    
    # 1. Generate lineage roots once -----------------------------------------
    lineage_roots = _generate_lineage_roots(df)

    # 2. Precompute SMILES in bulk -------------------------------------------
    all_products: List[str] = []
    all_subs: List[str] = []
    for _, r in df.iterrows():
        rec = VariantRecord(r.to_dict())
        all_products.extend(rec.product_iupac())
        all_subs.extend(rec.substrate_iupac())
    prod_cache = _batch_convert(list(set(all_products)), is_substrate=False)
    sub_cache = _batch_convert(list(set(all_subs)), is_substrate=True)

    # NO CACHING - Comment out cache updates
    # SMILES_CACHE.update(prod_cache)
    # SUBSTRATE_CACHE.update(sub_cache)
    # _save_pickle(SMILES_CACHE, SMILES_CACHE_FILE)
    # _save_pickle(SUBSTRATE_CACHE, SUBSTRATE_CACHE_FILE)

    # 3. Flatten rows ---------------------------------------------------------
    idmap = {str(r["enzyme_id"]): r.to_dict() for _, r in df.iterrows()}
    output_rows: List[Dict[str, str]] = []
    for idx, (_, row) in enumerate(df.iterrows()):
        rec = VariantRecord(row.to_dict())
        eid = rec.eid

        # Reaction data -------------------------------------------------------
        subs = rec.substrate_iupac()
        prods = rec.product_iupac()
        data_type = rec.row.get("data_type", "")
        
        if not subs or not prods:
            # Skip entries without reaction info unless it's marked as lineage only
            if data_type == "lineage":
                subs, prods = [""], [""]  # placeholders
            else:
                log.debug("Skipping %s due to missing reaction data", eid)
                continue

        sub_smiles = [sub_cache.get(s, "") for s in subs]
        prod_smiles = [prod_cache.get(p, "") for p in prods]

        smiles_string = ".".join(prod_smiles)
        smiles_reaction = ".".join(sub_smiles) + " >> " + ".".join(prod_smiles)
        smiles_string = _canonical_smiles(smiles_string)

        # Mutations -----------------------------------------------------------
        root_id = _root_enzyme_id(eid, idmap, lineage_roots)
        root_row = idmap[root_id]
        root_aa = (
            str(root_row.get("protein_sequence", ""))
            or str(root_row.get("aa_sequence", ""))
        )
        root_nt = (
            str(root_row.get("nucleotide_sequence", ""))
            or str(root_row.get("nt_sequence", ""))
        )
        # If root doesn't have NT sequence but has AA sequence, reverse translate
        if (not root_nt or root_nt == "nan") and root_aa:
            root_nt = _rev_translate(root_aa)
        
        aa_muts = _aa_mut(root_aa, rec.aa_seq) if rec.aa_seq and root_aa else ""
        nt_muts = _nt_mut(root_aa, rec.aa_seq, root_nt, rec.nt_seq) if root_aa or root_nt else ""

        # Plate / well --------------------------------------------------------
        barcode_plate, plate_name, well = _plate_and_well(idx)

        # Reaction conditions -------------------------------------------------
        cond_parts = []
        for fld in (
            "reaction_temperature",
            "reaction_ph",
            "reaction_other_conditions",
            "reaction_substrate_concentration",
        ):
            if row.get(fld):
                cond_parts.append(f"{fld}:{row[fld]}")
        reaction_condition = ";".join(cond_parts)

        # Cofactor (IUPAC list preferred, fallback plain list) ---------------
        cof_iupac = str(row.get("cofactor_iupac_list", "")).strip()
        cof_list = str(row.get("cofactor_list", "")).strip()
        cofactor = cof_iupac or cof_list

        # Additional info -----------------------------------------------------
        extra: Dict[str, str] = {
            k: str(v) for k, v in row.items() if k not in INPUT_REQUIRED + OPTIONAL_INPUT
        }
        if rec.ttn_or_yield() is not None:
            ttn_val = row.get("ttn")
            extra["fitness_type"] = "ttn" if (ttn_val is not None and pd.notna(ttn_val)) else "yield"
        additional_information = json.dumps(extra, separators=(",", ":")) if extra else ""

        flat = FlatRow(
            id=eid,
            barcode_plate=barcode_plate,
            plate=plate_name,
            well=well,
            smiles_string=smiles_string,
            smiles_reaction=smiles_reaction,
            nucleotide_mutation=nt_muts,
            amino_acid_substitutions=aa_muts,
            nt_sequence=rec.nt_seq,
            aa_sequence=rec.aa_seq,
            fitness_value=rec.ttn_or_yield(),
            cofactor=cofactor,
            reaction_condition=reaction_condition,
            ee=str(row.get("ee", "")),
            additional_information=additional_information,
        )
        output_rows.append(flat.as_dict())

    out_df = pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS)
    return out_df


# === 8. PIPELINE ORCHESTRATOR ======================================================

def run_pipeline(reaction_csv: str | Path | None = None, 
                substrate_scope_csv: str | Path | None = None,
                output_csv: str | Path | None = None) -> pd.DataFrame:
    """Run the pipeline on reaction and/or substrate scope CSV files.
    
    Args:
        reaction_csv: Path to reaction/lineage data CSV (optional)
        substrate_scope_csv: Path to substrate scope data CSV (optional)
        output_csv: Path to write the formatted output CSV
        
    Returns:
        DataFrame with flattened lineage data
    """
    t0 = time.perf_counter()
    
    dfs = []
    
    # Load reaction data if provided
    if reaction_csv:
        df_reaction = pd.read_csv(reaction_csv)
        df_reaction['data_type'] = 'lineage'
        # Handle column aliasing for reaction data
        if 'enzyme' in df_reaction.columns and 'enzyme_id' not in df_reaction.columns:
            df_reaction['enzyme_id'] = df_reaction['enzyme']
        log.info("Loaded %d reaction entries from %s", len(df_reaction), reaction_csv)
        dfs.append(df_reaction)
    
    # Load substrate scope data if provided
    if substrate_scope_csv:
        df_substrate = pd.read_csv(substrate_scope_csv)
        df_substrate['data_type'] = 'substrate_scope'
        log.info("Loaded %d substrate scope entries from %s", len(df_substrate), substrate_scope_csv)
        dfs.append(df_substrate)
    
    if not dfs:
        raise ValueError("At least one input CSV must be provided")
    
    # Combine dataframes
    if len(dfs) > 1:
        df_in = pd.concat(dfs, ignore_index=True)
        log.info("Combined data: %d total entries", len(df_in))
    else:
        df_in = dfs[0]

    df_out = flatten_dataframe(df_in)
    log.info("Flattened to %d rows", len(df_out))

    if output_csv:
        df_out.to_csv(output_csv, index=False)
        log.info("Wrote output CSV to %s (%.1f kB)", output_csv, Path(output_csv).stat().st_size / 1024)

    log.info("Pipeline finished in %.2f s", time.perf_counter() - t0)
    return df_out


# === 9. CLI ENTRYPOINT =============================================================

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lineage_flattener",
        description="Flatten enzyme lineage CSV into reaction table for automation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-r", "--reaction", help="Reaction/lineage data CSV file")
    p.add_argument("-s", "--substrate-scope", help="Substrate scope data CSV file")
    p.add_argument("-o", "--output", help="Path to write flattened CSV")
    p.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    level = logging.DEBUG if args.verbose and args.verbose > 1 else logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    
    if not args.reaction and not args.substrate_scope:
        log.error("At least one input file must be provided (--reaction or --substrate-scope)")
        sys.exit(1)
    
    run_pipeline(args.reaction, args.substrate_scope, args.output)


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------- END ---

