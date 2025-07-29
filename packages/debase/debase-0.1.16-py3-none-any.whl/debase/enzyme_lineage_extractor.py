"""enzyme_lineage_extractor.py

Single-file, maintainable CLI tool that pulls an enzyme "family tree" and
associated sequences from one or two PDFs (manuscript + SI) using Google
Gemini (or compatible) LLM.

Navigate by searching for the numbered section headers:

    # === 1. CONFIG & CONSTANTS ===
    # === 2. DOMAIN MODELS ===
    # === 3. LOGGING HELPERS ===
    # === 4. PDF HELPERS ===
    # === 5. LLM (GEMINI) HELPERS ===
    # === 6. LINEAGE EXTRACTION ===
    # === 7. SEQUENCE EXTRACTION ===
    # === 8. VALIDATION & MERGE ===
    # === 9. PIPELINE ORCHESTRATOR ===
    # === 10. CLI ENTRYPOINT ===
"""

# === 1. CONFIG & CONSTANTS ===
from __future__ import annotations
import pandas as pd
import networkx as nx  # light dependency, used only for generation inference

import os
import re
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple

MODEL_NAME: str = "gemini-2.5-flash"
MAX_CHARS: int = 150_000           # Max characters sent to LLM
SEQ_CHUNK: int = 10                # Batch size when prompting for sequences
MAX_RETRIES: int = 4               # LLM retry loop
CACHE_DIR: Path = Path.home() / ".cache" / "enzyme_extractor"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# === 2. DOMAIN MODELS ===
@dataclass
class Campaign:
    """Representation of a directed evolution campaign."""
    campaign_id: str
    campaign_name: str
    description: str
    model_substrate: Optional[str] = None
    model_product: Optional[str] = None
    substrate_id: Optional[str] = None
    product_id: Optional[str] = None
    data_locations: List[str] = field(default_factory=list)
    reaction_conditions: dict = field(default_factory=dict)
    notes: str = ""

@dataclass
class Variant:
    """Representation of a variant in the evolutionary lineage."""
    variant_id: str
    parent_id: Optional[str]
    mutations: List[str]
    generation: int
    campaign_id: Optional[str] = None  # Links variant to campaign
    notes: str = ""

@dataclass
class SequenceBlock:
    """Protein and/or DNA sequence associated with a variant."""
    variant_id: str
    aa_seq: Optional[str] = None
    dna_seq: Optional[str] = None
    confidence: Optional[float] = None
    truncated: bool = False
    metadata: dict = field(default_factory=dict)

# === 3. LOGGING HELPERS ===

# --- Debug dump helper ----------------------------------------------------
def _dump(text: str | bytes, path: Path | str) -> None:
    """Write `text` / `bytes` to `path`, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(text, (bytes, bytearray)) else "w"
    with p.open(mode) as fh:
        fh.write(text)

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

# === 4. PDF HELPERS (incl. caption scraper & figure extraction) ===
try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required for PDF parsing. Install with `pip install pymupdf`."
    ) from exc

_DOI_REGEX = re.compile(r"10\.[0-9]{4,9}/[-._;()/:A-Z0-9]+", re.I)

# PDB ID regex - matches 4-character PDB codes
_PDB_REGEX = re.compile(r"\b[1-9][A-Z0-9]{3}\b")

# Improved caption prefix regex - captures most journal variants
_CAPTION_PREFIX_RE = re.compile(
    r"""
    ^\s*
    (?:Fig(?:ure)?|Extended\s+Data\s+Fig|ED\s+Fig|Scheme|Chart|
       Table|Supp(?:lementary|l|\.?)\s+(?:Fig(?:ure)?|Table))  # label part
    \s*(?:S?\d+[A-Za-z]?|[IVX]+)                               # figure number
    [.:]?\s*                                                   # trailing punctuation/space
    """,
    re.I | re.X,
)


def _open_doc(pdf_path: str | Path | bytes):
    if isinstance(pdf_path, (str, Path)):
        return fitz.open(pdf_path)  # type: ignore[arg-type]
    return fitz.open(stream=pdf_path, filetype="pdf")  # type: ignore[arg-type]


def extract_text(pdf_path: str | Path | bytes) -> str:
    """Extract raw text from a PDF file (all blocks)."""

    doc = _open_doc(pdf_path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def extract_captions(pdf_path: str | Path | bytes, max_chars: int = MAX_CHARS) -> str:
    """Extract figure/table captions using the improved regex.

    The function scans every text line on every page and keeps lines whose first
    token matches `_CAPTION_PREFIX_RE`. This covers labels such as:
      * Fig. 1, Figure 2A, Extended Data Fig 3
      * Table S1, Table 4, Scheme 2, Chart 1B
      * Supplementary Fig. S5, Supp Table 2
    """

    doc = _open_doc(pdf_path)
    captions: list[str] = []
    try:
        for page in doc:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                # Get all lines in this block
                block_lines = []
                for line in block.get("lines", []):
                    text_line = "".join(span["text"] for span in line.get("spans", []))
                    block_lines.append(text_line.strip())
                
                # Check if any line starts with a caption prefix
                for i, line in enumerate(block_lines):
                    if _CAPTION_PREFIX_RE.match(line):
                        # Found a caption start - collect this line and subsequent lines
                        # until we hit an empty line or the end of the block
                        caption_parts = [line]
                        for j in range(i + 1, len(block_lines)):
                            next_line = block_lines[j]
                            if not next_line:  # Empty line signals end of caption
                                break
                            # Check if next line is a new caption
                            if _CAPTION_PREFIX_RE.match(next_line):
                                break
                            caption_parts.append(next_line)
                        
                        # Join the parts with spaces
                        full_caption = " ".join(caption_parts)
                        captions.append(full_caption)
    finally:
        doc.close()

    joined = "\n".join(captions)
    return joined[:max_chars]


def extract_doi(pdf_path: str | Path | bytes) -> Optional[str]:
    """Attempt to locate a DOI inside the PDF."""

    m = _DOI_REGEX.search(extract_text(pdf_path))
    return m.group(0) if m else None


def extract_pdb_ids(pdf_path: str | Path | bytes) -> List[str]:
    """Extract all PDB IDs from the PDF."""
    text = extract_text(pdf_path)
    
    # Find all potential PDB IDs
    pdb_ids = []
    for match in _PDB_REGEX.finditer(text):
        pdb_id = match.group(0).upper()
        # Additional validation - check context for "PDB" mention
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].upper()
        
        # Only include if "PDB" appears in context or it's a known pattern
        if "PDB" in context or "PROTEIN DATA BANK" in context:
            if pdb_id not in pdb_ids:
                pdb_ids.append(pdb_id)
                log.info(f"Found PDB ID: {pdb_id}")
    
    return pdb_ids


def limited_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate **all text** from PDFs, trimmed to `max_chars`."""

    total = 0
    chunks: list[str] = []
    for p in pdf_paths:
        t = extract_text(p)
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        chunks.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def limited_caption_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate only caption text from PDFs, trimmed to `max_chars`."""

    total = 0
    chunks: list[str] = []
    for p in pdf_paths:
        t = extract_captions(p)
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        chunks.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def extract_figure(pdf_path: Union[str, Path], figure_id: str, debug_dir: Optional[Union[str, Path]] = None) -> Optional[bytes]:
    """Extract a specific figure from a PDF by finding its caption.
    
    Returns the figure as PNG bytes if found, None otherwise.
    """
    doc = _open_doc(pdf_path)
    figure_bytes = None
    
    try:
        # Search for the exact figure caption text
        search_text = figure_id.strip()
        
        for page_num, page in enumerate(doc):
            # Search for the caption text on this page
            text_instances = page.search_for(search_text)
            
            if text_instances:
                log.info(f"Found caption '{figure_id}' on page {page_num + 1}")
                
                # Get the position of the first instance
                caption_rect = text_instances[0]
                
                # Get all images on this page
                image_list = page.get_images()
                
                if image_list:
                    # Find the image closest to and above the caption
                    best_img = None
                    best_distance = float('inf')
                    
                    for img_index, img in enumerate(image_list):
                        # Get image position
                        xref = img[0]
                        img_rects = page.get_image_rects(xref)
                        
                        if img_rects:
                            img_rect = img_rects[0]
                            
                            # Check if image is above the caption and calculate distance
                            if img_rect.y1 <= caption_rect.y0:  # Image bottom is above caption top
                                distance = caption_rect.y0 - img_rect.y1
                                if distance < best_distance and distance < 100:  # Within reasonable distance
                                    best_distance = distance
                                    best_img = xref
                    
                    if best_img is not None:
                        # Extract the identified image
                        pix = fitz.Pixmap(doc, best_img)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            figure_bytes = pix.tobytes("png")
                        else:  # Convert CMYK to RGB
                            pix2 = fitz.Pixmap(fitz.csRGB, pix)
                            figure_bytes = pix2.tobytes("png")
                            pix2 = None
                        pix = None
                        
                        # Save to debug directory if provided
                        if debug_dir and figure_bytes:
                            debug_path = Path(debug_dir)
                            debug_path.mkdir(parents=True, exist_ok=True)
                            fig_file = debug_path / f"figure_{figure_id.replace(' ', '_').replace('.', '')}_{int(time.time())}.png"
                            with open(fig_file, 'wb') as f:
                                f.write(figure_bytes)
                            log.info(f"Saved figure to: {fig_file}")
                        
                        break
                
    finally:
        doc.close()
    
    return figure_bytes


def is_figure_reference(location: str) -> bool:
    """Check if a location string refers to a figure."""
    # Check for common figure patterns
    figure_patterns = [
        r'Fig(?:ure)?\.?\s+',      # Fig. 2B, Figure 3
        r'Extended\s+Data\s+Fig',   # Extended Data Fig
        r'ED\s+Fig',                # ED Fig
        r'Scheme\s+',               # Scheme 1
        r'Chart\s+',                # Chart 2
    ]
    
    location_str = str(location).strip()
    for pattern in figure_patterns:
        if re.search(pattern, location_str, re.I):
            return True
    return False

# === 5. LLM (Gemini) HELPERS === ---------------------------------------------
from typing import Tuple, Any

_BACKOFF_BASE = 2.0  # exponential back-off base (seconds)

# -- 5.1  Import whichever SDK is installed -----------------------------------

def _import_gemini_sdk() -> Tuple[str, Any]:
    """Return (flavor, module) where flavor in {"new", "legacy"}."""
    try:
        import google.generativeai as genai  # official SDK >= 1.0
        return "new", genai
    except ImportError:
        try:
            import google_generativeai as genai  # legacy prerelease name
            return "legacy", genai
        except ImportError as exc:
            raise ImportError(
                "Neither 'google-generativeai' (>=1.0) nor 'google_generativeai'\n"
                "is installed.  Run:  pip install --upgrade google-generativeai"
            ) from exc

_SDK_FLAVOR, _genai = _import_gemini_sdk()

# -- 5.2  Model factory --------------------------------------------------------

def get_model():
    """Configure API key and return a `GenerativeModel` instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    _genai.configure(api_key=api_key)
    # Positional constructor arg works for both SDK flavors
    return _genai.GenerativeModel(MODEL_NAME)

# === 5.3  Unified call helper ----------------------------------------------

def _extract_text(resp) -> str:
    """
    Pull the *first* textual part out of a GenerativeAI response, handling both
    the old prerelease SDK and the >=1.0 SDK.

    Returns an empty string if no textual content is found.
    """
    # 1) Legacy SDK (<= 0.4) - still has nice `.text`
    if getattr(resp, "text", None):
        return resp.text

    # 2) >= 1.0 SDK
    if getattr(resp, "candidates", None):
        cand = resp.candidates[0]

        # 2a) Some beta builds still expose `.text`
        if getattr(cand, "text", None):
            return cand.text

        # 2b) Official path: candidate.content.parts[*].text
        if getattr(cand, "content", None):
            parts = [
                part.text                     # Part objects have .text
                for part in cand.content.parts
                if getattr(part, "text", None)
            ]
            if parts:
                return "".join(parts)

    # 3) As a last resort fall back to str()
    return str(resp)


def generate_json_with_retry(
    model,
    prompt: str,
    schema_hint: str | None = None,
    *,
    max_retries: int = MAX_RETRIES,
    debug_dir:str | Path | None = None,
    tag: str = 'gemini',
):
    """
    Call Gemini with retries & exponential back-off, returning parsed JSON.

    Also strips Markdown fences that the model may wrap around its JSON.
    """
    # Log prompt details
    log.info("=== GEMINI API CALL: %s ===", tag.upper())
    log.info("Prompt length: %d characters", len(prompt))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(prompt)} characters\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
        log.info("Full prompt saved to: %s", prompt_file)
    
    fence_re = re.compile(r"```json|```", re.I)
    for attempt in range(1, max_retries + 1):
        try:
            log.info("Calling Gemini API (attempt %d/%d)...", attempt, max_retries)
            resp = model.generate_content(prompt)
            raw = _extract_text(resp).strip()
            
            # Log response
            log.info("Gemini response length: %d characters", len(raw))
            log.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
            
            # Save full response to debug directory
            if debug_dir:
                response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw)
                log.info("Full response saved to: %s", response_file)

            # Remove common Markdown fences
            if raw.startswith("```"):
                raw = fence_re.sub("", raw).strip()
            
            # Try to find JSON in the response
            # First, try to parse as-is
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # If that fails, look for JSON array or object
                # Find the first '[' or '{' and the matching closing bracket
                json_start = -1
                json_end = -1
                bracket_stack = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(raw):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char in '[{':
                        if json_start == -1:
                            json_start = i
                        bracket_stack.append(char)
                    elif char in ']}':
                        if bracket_stack:
                            opening = bracket_stack.pop()
                            if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                                if not bracket_stack:  # Found complete JSON
                                    json_end = i + 1
                                    break
                
                if json_start >= 0 and json_end > json_start:
                    # Extract the JSON portion
                    json_str = raw[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    # Look for simple [] in the response
                    if '[]' in raw:
                        parsed = []
                    else:
                        # No JSON structure found, re-raise the original error
                        raise json.JSONDecodeError("No JSON structure found in response", raw, 0)
            log.info("Successfully parsed JSON response")
            return parsed
        except Exception as exc:                                 # broad except OK here
            log.warning(
                "Gemini call failed (attempt %d/%d): %s",
                attempt, max_retries, exc,
            )
            if attempt == max_retries:
                raise
            time.sleep(_BACKOFF_BASE ** attempt)
# -------------------------------------------------------------------- end 5 ---


# === 6. LINEAGE EXTRACTION (WITH CAMPAIGN SUPPORT) ===
"""
Variant lineage extractor with campaign identification.

Asks Gemini to produce a JSON representation of the evolutionary lineage of
enzyme variants described in a manuscript.  The heavy lifting is done by the
LLM; this section crafts robust prompts, parses the reply, validates it, and
exposes a convenient high-level `get_lineage()` helper for the pipeline.

June 2025: updated for Google Generative AI SDK >= 1.0 and added rich debug
hooks (`--debug-dir` dumps prompts, replies, and raw captions).

December 2025: Added campaign identification to support multiple directed
evolution campaigns within a single paper.
"""

from pathlib import Path
from typing import List, Dict, Any

# ---- 6.0  Campaign identification prompts -----------------------------------

_CAMPAIGN_IDENTIFICATION_PROMPT = """
You are an expert reader of protein engineering manuscripts.
Analyze the following manuscript text to identify ALL distinct directed evolution campaigns.

Each campaign represents a separate evolutionary lineage targeting different:
- Model reactions (e.g., different chemical transformations)
- Substrate scopes
- Activities (e.g., different enzymatic reactions)

Look for:
1. Different model substrates/products mentioned (e.g., different substrate/product pairs)
2. Distinct enzyme lineage names (e.g., different variant naming patterns)
3. Separate evolution trees or lineage tables
4. Different reaction schemes or transformations

Return a JSON array of campaigns:
[
  {{
    "campaign_id": "unique_id",
    "campaign_name": "descriptive name",
    "description": "what this campaign evolved for",
    "model_substrate": "substrate name/id",
    "model_product": "product name/id", 
    "substrate_id": "id from paper (e.g., 1a)",
    "product_id": "id from paper (e.g., 2a)",
    "data_locations": ["Table S1", "Figure 1"],
    "lineage_hint": "enzyme name pattern",
    "notes": "additional context"
  }}
]

TEXT:
{text}
""".strip()

_CAMPAIGN_BEST_LOCATION_PROMPT = """
Given this specific campaign and the available data locations, select the BEST location to extract the complete lineage data for this campaign.

Campaign:
- ID: {campaign_id}
- Name: {campaign_name}
- Description: {description}
- Lineage identifiers: {identifiers}

Available locations with context:
{locations_with_context}

Select the location that most likely contains the COMPLETE lineage data (all variants, mutations, and parent relationships) for THIS SPECIFIC campaign.

Consider:
1. Tables are usually more structured and complete than figures
2. Look for locations that mention this campaign's specific identifiers or enzyme names
3. Some locations may contain data for multiple campaigns - that's fine, we can filter later
4. Prioritize completeness over visual clarity

Return a JSON object with:
{{"location": "selected location identifier", "confidence": 0-100, "reason": "explanation"}}
""".strip()

# ---- 6.1  Prompt templates -------------------------------------------------

_LINEAGE_LOC_PROMPT = """
You are an expert reader of protein engineering manuscripts.
Given the following article text, list up to {max_results} *locations* (page
numbers, figure/table IDs, or section headings) that you would review first to
find the COMPLETE evolutionary lineage of enzyme variants (i.e. which variant
came from which parent and what mutations were introduced).

Respond with a JSON array of objects, each containing:
- "location": the identifier (e.g. "Table S1", "Figure 2B", "p. 6")
- "type": one of "table", "figure", "text", "section"  
- "confidence": your confidence score (0-100) that this location contains lineage data
- "reason": brief explanation of why this location likely contains lineage

Order by confidence score (highest first). Tables showing complete variant lineages or 
mutation lists should be ranked higher than figure showing complete variant lineages.
Text sections is used when no suitable tables/figurews exist.

Don't include oligonucleotide results or result from only one round.

Example output:
[
  {{"location": "Table S1", "type": "table", "confidence": 95, "reason": "Variant lineage table"}},
  {{"location": "Figure 2B", "type": "figure", "confidence": 70, "reason": "Phylogenetic tree diagram"}},
  {{"location": "Section 3.2", "type": "section", "confidence": 60, "reason": "Evolution description"}}
]
""".strip()

_LINEAGE_SCHEMA_HINT = """
{
  "variants": [
    {
      "variant_id": "string",
      "parent_id": "string | null",
      "mutations": ["string"],
      "generation": "int",
      "campaign_id": "string (optional)",
      "notes": "string (optional)"
    }
  ]
}
""".strip()

_LINEAGE_EXTRACT_PROMPT = """
Below is the (optionally truncated) text of a protein-engineering manuscript.
Your task is to output the **complete evolutionary lineage** as JSON conforming
exactly to the schema provided below.

{campaign_context}

Schema:
```json
{schema}
```

Guidelines:
  * Include every named variant that appears in the lineage (WT, libraries,
    hits, final variant, etc.).
  * If a variant appears multiple times, keep the earliest generation.
  * `mutations` must be a list of human-readable point mutations *relative to
    its immediate parent* (e.g. ["L34V", "S152G"]). If no mutations are listed,
    use an empty list.
  * Generation = 0 for the starting template (WT or first variant supplied by
    the authors). Increment by 1 for each subsequent round.
  * If you are uncertain about any field, add an explanatory string to `notes`.
  * IMPORTANT: Only include variants that belong to the campaign context provided above.

Return **ONLY** minified JSON, no markdown fences, no commentary.

TEXT:
```
{text}
```
""".strip()

_LINEAGE_FIGURE_PROMPT = """
You are looking at a figure from a protein-engineering manuscript that shows
the evolutionary lineage of enzyme variants.

{campaign_context}

Your task is to output the **complete evolutionary lineage** as JSON conforming
exactly to the schema provided below.

Schema:
```json
{schema}
```

Guidelines:
  * Include every named variant that appears in the lineage diagram/tree
  * Extract parent-child relationships from the visual connections (arrows, lines, etc.)
  * `mutations` must be a list of human-readable point mutations *relative to
    its immediate parent* (e.g. ["L34V", "S152G"]) if shown
  * Generation = 0 for the starting template (WT or first variant). Increment by 1 
    for each subsequent round/generation shown in the figure
  * If you are uncertain about any field, add an explanatory string to `notes`
  * IMPORTANT: Only include variants that belong to the campaign context provided above.

Return **ONLY** minified JSON, no markdown fences, no commentary.
""".strip()

# ---- 6.2  Helper functions -------------------------------------------------

def identify_campaigns(
    text: str,
    model,
    *,
    debug_dir: str | Path | None = None,
) -> List[Campaign]:
    """Identify distinct directed evolution campaigns in the manuscript."""
    prompt = _CAMPAIGN_IDENTIFICATION_PROMPT.format(text=text[:30_000])
    campaigns_data: List[dict] = []
    try:
        campaigns_data = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="campaigns",
        )
    except Exception as exc:
        log.warning("identify_campaigns(): %s", exc)
    
    # Convert to Campaign objects
    campaigns = []
    for data in campaigns_data:
        try:
            campaign = Campaign(
                campaign_id=data.get("campaign_id", ""),
                campaign_name=data.get("campaign_name", ""),
                description=data.get("description", ""),
                model_substrate=data.get("model_substrate"),
                model_product=data.get("model_product"),
                substrate_id=data.get("substrate_id"),
                product_id=data.get("product_id"),
                data_locations=data.get("data_locations", []),
                reaction_conditions=data.get("reaction_conditions", {}),
                notes=data.get("notes", "")
            )
            campaigns.append(campaign)
            log.info(f"Identified campaign: {campaign.campaign_name} ({campaign.campaign_id})")
        except Exception as exc:
            log.warning(f"Failed to parse campaign data: {exc}")
    
    return campaigns

def identify_evolution_locations(
    text: str,
    model,
    *,
    max_results: int = 5,
    debug_dir: str | Path | None = None,
    campaigns: Optional[List[Campaign]] = None,
    pdf_paths: Optional[List[Path]] = None,
) -> List[dict]:
    """Ask Gemini where in the paper the lineage is probably described."""
    # Extract table of contents from PDFs if available
    toc_text = ""
    if pdf_paths:
        toc_sections = []
        for pdf_path in pdf_paths:
            # Extract first few pages looking for TOC
            doc = _open_doc(pdf_path)
            try:
                for page_num in range(min(5, len(doc))):
                    page_text = doc[page_num].get_text()
                    if any(indicator in page_text.lower() for indicator in ['table of contents', 'contents', 'summary']):
                        # Found TOC page
                        lines = page_text.split('\n')
                        toc_lines = []
                        for line in lines:
                            line = line.strip()
                            # TOC entries typically have page numbers
                            if (re.search(r'\.{2,}\s*S?\d+\s*$', line) or
                                re.search(r'\s{2,}S?\d+\s*$', line) or
                                re.match(r'^\d+\.\s+\w+', line)):
                                toc_lines.append(line)
                        if toc_lines:
                            pdf_name = pdf_path.name
                            toc_sections.append(f"\n--- Table of Contents from {pdf_name} ---\n" + '\n'.join(toc_lines))
                            break
            finally:
                doc.close()
        
        if toc_sections:
            toc_text = "\n\nTABLE OF CONTENTS SECTIONS:" + ''.join(toc_sections) + "\n\n"
    
    # Include TOC before the main text
    combined_text = toc_text + text if toc_text else text
    prompt = _LINEAGE_LOC_PROMPT.format(max_results=max_results) + "\n\nTEXT:\n" + combined_text[:15_000]
    locs: List[dict] = []
    try:
        locs = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="locate",
        )
    except Exception as exc:  # pragma: no cover
        log.warning("identify_evolution_locations(): %s", exc)
    
    # No longer mapping locations to campaigns here - we'll ask for best location per campaign instead
    
    return locs if isinstance(locs, list) else []



def _parse_variants(data: Dict[str, Any], campaign_id: Optional[str] = None) -> List[Variant]:
    """Convert raw JSON to a list[Variant] with basic validation."""
    variants_json = data.get("variants", []) if isinstance(data, dict) else []
    parsed: List[Variant] = []
    for item in variants_json:
        try:
            variant_id = str(item["variant_id"]).strip()
            parent_id = item.get("parent_id")
            parent_id = str(parent_id).strip() if parent_id else None
            mutations = [str(m).strip() for m in item.get("mutations", [])]
            generation = int(item.get("generation", 0))
            notes = str(item.get("notes", "")).strip()
            
            # Use campaign_id from item if present, otherwise use the passed campaign_id, 
            # otherwise default to "default"
            variant_campaign_id = item.get("campaign_id") or campaign_id or "default"
            
            parsed.append(
                Variant(
                    variant_id=variant_id,
                    parent_id=parent_id,
                    mutations=mutations,
                    generation=generation,
                    campaign_id=variant_campaign_id,
                    notes=notes,
                )
            )
        except Exception as exc:  # pragma: no cover
            log.debug("Skipping malformed variant entry %s: %s", item, exc)
    return parsed



def extract_complete_lineage(
    text: str,
    model,
    *,
    debug_dir: str | Path | None = None,
    campaign_id: Optional[str] = None,
    campaign_info: Optional[Campaign] = None,
    pdf_paths: Optional[List[Path]] = None,
) -> List[Variant]:
    """Prompt Gemini for the full lineage and return a list[Variant]."""
    # Build campaign context
    campaign_context = ""
    if campaign_info:
        campaign_context = f"""
CAMPAIGN CONTEXT:
You are extracting the lineage for the following campaign:
- Campaign ID: {campaign_info.campaign_id}
- Campaign: {campaign_info.campaign_name}
- Description: {campaign_info.description}
- Model reaction: {campaign_info.substrate_id} → {campaign_info.product_id}
- Lineage hint: Variants containing "{campaign_info.notes}" belong to this campaign

IMPORTANT: 
1. Only extract variants that belong to this specific campaign.
2. Include "campaign_id": "{campaign_info.campaign_id}" for each variant in your response.
3. Use the lineage hint pattern above to identify which variants belong to this campaign.
4. Include parent variants only if they are direct ancestors in this campaign's lineage.
"""
    
    # Extract table of contents from PDFs if available  
    toc_text = ""
    if pdf_paths:
        toc_sections = []
        for pdf_path in pdf_paths:
            # Extract first few pages looking for TOC
            doc = _open_doc(pdf_path)
            try:
                for page_num in range(min(5, len(doc))):
                    page_text = doc[page_num].get_text()
                    if any(indicator in page_text.lower() for indicator in ['table of contents', 'contents', 'summary']):
                        # Found TOC page
                        lines = page_text.split('\n')
                        toc_lines = []
                        for line in lines:
                            line = line.strip()
                            # TOC entries typically have page numbers
                            if (re.search(r'\.{2,}\s*S?\d+\s*$', line) or
                                re.search(r'\s{2,}S?\d+\s*$', line) or
                                re.match(r'^\d+\.\s+\w+', line)):
                                toc_lines.append(line)
                        if toc_lines:
                            pdf_name = pdf_path.name
                            toc_sections.append(f"\n--- Table of Contents from {pdf_name} ---\n" + '\n'.join(toc_lines))
                            break
            finally:
                doc.close()
        
        if toc_sections:
            toc_text = "\n\nTABLE OF CONTENTS SECTIONS:" + ''.join(toc_sections) + "\n\n"
    
    # Include TOC in the prompt text
    combined_text = toc_text + text if toc_text else text
    
    prompt = _LINEAGE_EXTRACT_PROMPT.format(
        campaign_context=campaign_context,
        schema=_LINEAGE_SCHEMA_HINT,
        text=combined_text[:MAX_CHARS],
    )
    raw = generate_json_with_retry(
        model,
        prompt,
        schema_hint=_LINEAGE_SCHEMA_HINT,
        debug_dir=debug_dir,
        tag="lineage",
    )
    variants = _parse_variants(raw, campaign_id=campaign_id)
    log.info("Extracted %d lineage entries", len(variants))
    return variants


def extract_lineage_from_figure(
    figure_bytes: bytes,
    model,
    *,
    debug_dir: str | Path | None = None,
    campaign_id: Optional[str] = None,
    campaign_info: Optional[Campaign] = None,
) -> List[Variant]:
    """Extract lineage from a figure image using Gemini's vision capabilities."""
    # Build campaign context
    campaign_context = ""
    if campaign_info:
        campaign_context = f"""
CAMPAIGN CONTEXT:
You are extracting the lineage for the following campaign:
- Campaign: {campaign_info.campaign_name}
- Description: {campaign_info.description}
- Model reaction: {campaign_info.substrate_id} → {campaign_info.product_id}
- Lineage hint: Variants containing "{campaign_info.notes}" belong to this campaign

IMPORTANT: Only extract variants that belong to this specific campaign.
"""
    
    prompt = _LINEAGE_FIGURE_PROMPT.format(
        campaign_context=campaign_context,
        schema=_LINEAGE_SCHEMA_HINT
    )
    
    # Log prompt details
    log.info("=== GEMINI VISION API CALL: FIGURE_LINEAGE ===")
    log.info("Prompt length: %d characters", len(prompt))
    log.info("Image size: %d bytes", len(figure_bytes))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save prompt and image to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        
        # Save prompt
        prompt_file = debug_path / f"figure_lineage_prompt_{int(time.time())}.txt"
        _dump(f"=== PROMPT FOR FIGURE_LINEAGE ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\nImage size: {len(figure_bytes)} bytes\n{'='*80}\n\n{prompt}",
              prompt_file)
        log.info("Full prompt saved to: %s", prompt_file)
        
        # Save image
        image_file = debug_path / f"figure_lineage_image_{int(time.time())}.png"
        _dump(figure_bytes, image_file)
        log.info("Figure image saved to: %s", image_file)
    
    # For Gemini vision API, we need to pass the image differently
    # This will depend on the specific SDK version being used
    try:
        # Create a multimodal prompt with the image
        import PIL.Image
        import io
        
        # Convert bytes to PIL Image
        image = PIL.Image.open(io.BytesIO(figure_bytes))
        
        log.info("Calling Gemini Vision API...")
        # Generate content with image
        response = model.generate_content([prompt, image])
        raw_text = _extract_text(response).strip()
        
        # Log response
        log.info("Gemini figure analysis response length: %d characters", len(raw_text))
        log.info("First 500 chars of response:\n%s\n...(truncated)", raw_text[:500])
        
        # Save response to debug directory if provided
        if debug_dir:
            debug_path = Path(debug_dir)
            debug_path.mkdir(parents=True, exist_ok=True)
            response_file = debug_path / f"figure_lineage_response_{int(time.time())}.txt"
            with open(response_file, 'w') as f:
                f.write(f"=== RESPONSE FOR FIGURE LINEAGE ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(raw_text)} characters\n")
                f.write("="*80 + "\n\n")
                f.write(raw_text)
            log.info("Full response saved to: %s", response_file)
        
        # Parse JSON from response
        fence_re = re.compile(r"```json|```", re.I)
        if raw_text.startswith("```"):
            raw_text = fence_re.sub("", raw_text).strip()
        
        raw = json.loads(raw_text)
        
        # Handle both array and object formats
        if isinstance(raw, list):
            # Direct array format - convert to expected format
            variants_data = {"variants": raw}
        else:
            # Already in object format
            variants_data = raw
            
        variants = _parse_variants(variants_data, campaign_id=campaign_id)
        log.info("Extracted %d lineage entries from figure", len(variants))
        return variants
        
    except Exception as exc:
        log.warning("Failed to extract lineage from figure: %s", exc)
        return []


# ---- 6.3  Helper for location-based extraction -----------------------------

def _is_toc_entry(text: str, position: int, pattern: str) -> bool:
    """Check if a found pattern is likely a table of contents entry."""
    # Find the line containing this position
    line_start = text.rfind('\n', 0, position)
    line_end = text.find('\n', position)
    
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
        
    if line_end == -1:
        line_end = len(text)
        
    line = text[line_start:line_end]
    
    # TOC indicators:
    # 1. Line contains dots (...) followed by page number
    # 2. Line ends with just a page number
    # 3. Line has "Table S12:" or similar followed by title and page
    # 4. Pattern appears at start of line followed by description and page number
    if ('...' in line or 
        re.search(r'\.\s*\d+\s*$', line) or 
        re.search(r':\s*[^:]+\s+\d+\s*$', line) or
        (line.strip().startswith(pattern) and re.search(r'\s+\d+\s*$', line))):
        return True
        
    # Check if this is in a contents/TOC section
    # Look backwards up to 1000 chars for "Contents" or "Table of Contents"
    context_start = max(0, position - 1000)
    context = text[context_start:position].lower()
    if 'contents' in context or 'table of contents' in context:
        return True
    
    # Check if we're in the first ~5000 chars of the document (likely TOC area)
    # This helps catch TOC entries that don't have obvious formatting
    if position < 5000:
        # Be more strict for early document positions
        # Check if line looks like a TOC entry (has page number at end)
        if re.search(r'\s+\d+\s*$', line):
            return True
        
    return False

def _extract_text_at_locations(text: str, locations: List[Union[str, dict]], context_chars: int = 5000, validate_sequences: bool = False) -> str:
    """Extract text around identified locations."""
    if not locations:
        return text
    
    extracted_sections = []
    text_lower = text.lower()
    
    log.info("Extracting text around %d locations with %d chars context", 
             len(locations), context_chars)
    
    for location in locations:
        # Handle both string locations and dict formats
        if isinstance(location, dict):
            # New format: {location, type, confidence, reason}
            location_str = location.get('location', location.get('section', location.get('text', '')))
            location_type = location.get('type', '')
            
            # Extract page number if present in location string (e.g., "Table S1" might be on a specific page)
            page_num = location.get('page', '')
            search_hint = location.get('search_hint', '')
            
            # Build search patterns in priority order
            page_patterns = []
            
            # 1. Try the exact location string first
            if location_str:
                page_patterns.append(location_str.lower())
            
            # 2. Try page markers if we have a page number
            if page_num:
                # Clean page number (remove "page" prefix if present)
                clean_page = str(page_num).replace('page', '').strip()
                if clean_page.startswith('S') or clean_page.startswith('s'):
                    page_patterns.extend([f"\n{clean_page}\n", f"\n{clean_page} \n"])
                else:
                    page_patterns.extend([f"\ns{clean_page}\n", f"\nS{clean_page}\n", f"\n{clean_page}\n"])
            
            # 3. Try the search hint if provided
            if search_hint:
                page_patterns.append(search_hint.lower())
            
            # 4. Try partial matches for section headers if location looks like a section
            if location_str and '.' in location_str:
                text_parts = location_str.split('.')
                if len(text_parts) > 1:
                    page_patterns.append(text_parts[0].lower() + '.')
                page_patterns.append(location_str.lower())
            
        else:
            # Backward compatibility for string locations
            page_patterns = [str(location).lower()]
            location_str = str(location)
        
        # Try each pattern
        pos = -1
        used_pattern = None
        for pattern in page_patterns:
            search_pos = 0
            while search_pos < len(text_lower):
                temp_pos = text_lower.find(pattern.lower(), search_pos)
                if temp_pos == -1:
                    break
                    
                # Check if this is a TOC entry
                if _is_toc_entry(text, temp_pos, pattern):
                    log.debug("Skipping TOC entry for pattern '%s' at position %d", pattern, temp_pos)
                    search_pos = temp_pos + len(pattern)
                    continue
                    
                # Found non-TOC entry
                pos = temp_pos
                used_pattern = pattern
                log.debug("Found pattern '%s' at position %d (not TOC)", pattern, pos)
                break
                
            if pos != -1:
                break
        
        if pos != -1:
            if validate_sequences:
                # For sequence extraction, find ALL occurrences and test each one
                all_positions = []
                search_pos = pos
                
                # Find all occurrences of this pattern
                while search_pos != -1:
                    all_positions.append(search_pos)
                    search_pos = text_lower.find(used_pattern.lower(), search_pos + 1)
                    if len(all_positions) >= 10:  # Limit to 10 occurrences
                        break
                
                log.info("Found %d occurrences of pattern '%s' for location '%s'", 
                         len(all_positions), used_pattern, location_str)
                
                # Test each position for sequences
                best_position = -1
                best_score = 0
                test_window = 1000  # Test 1000 chars from each position
                
                for test_pos in all_positions:
                    test_end = min(len(text), test_pos + test_window)
                    test_text = text[test_pos:test_end]
                    
                    # Count sequences in this window
                    clean_text = re.sub(r'\s+', '', test_text.upper())
                    aa_matches = len(re.findall(f"[{''.join(_VALID_AA)}]{{50,}}", clean_text))
                    dna_matches = len(re.findall(f"[{''.join(_VALID_DNA)}]{{50,}}", clean_text))
                    score = aa_matches + dna_matches
                    
                    if score > 0:
                        log.info("Position %d: found %d AA and %d DNA sequences (score: %d)", 
                                test_pos, aa_matches, dna_matches, score)
                    
                    if score > best_score:
                        best_score = score
                        best_position = test_pos
                
                if best_position != -1:
                    # Extract from the best position
                    end = min(len(text), best_position + context_chars)
                    section_text = text[best_position:end]
                    extracted_sections.append(section_text)
                    log.info("Selected position %d with %d sequences for '%s', extracted %d chars", 
                             best_position, best_score, location_str, len(section_text))
                else:
                    log.warning("No sequences found in any of %d occurrences of '%s'", 
                               len(all_positions), location_str)
            else:
                # For lineage extraction, find ALL occurrences of the pattern
                all_positions = []
                search_pos = 0
                
                # Find all occurrences of this pattern (not just the first)
                while search_pos < len(text_lower):
                    temp_pos = text_lower.find(used_pattern.lower(), search_pos)
                    if temp_pos == -1:
                        break
                    
                    # Check if this is a TOC entry
                    if _is_toc_entry(text, temp_pos, used_pattern):
                        log.debug("Skipping TOC entry for pattern '%s' at position %d", used_pattern, temp_pos)
                        search_pos = temp_pos + len(used_pattern)
                        continue
                    
                    all_positions.append(temp_pos)
                    search_pos = temp_pos + len(used_pattern)
                    
                    if len(all_positions) >= 10:  # Limit to 10 occurrences
                        break
                
                log.info("Found %d non-TOC occurrences of pattern '%s' for location '%s'", 
                         len(all_positions), used_pattern, location_str)
                
                # Extract context around each occurrence
                for idx, pos in enumerate(all_positions):
                    start = max(0, pos - context_chars)
                    end = min(len(text), pos + len(used_pattern) + context_chars)
                    section_text = text[start:end]
                    extracted_sections.append(section_text)
                    log.info("Occurrence %d/%d: Found '%s' at position %d, extracted %d chars", 
                             idx + 1, len(all_positions), location_str, pos, len(section_text))
        else:
            log.warning("Location '%s' not found in text (tried %d patterns)", location_str, len(page_patterns))
    
    combined = "\n\n[...]\n\n".join(extracted_sections) if extracted_sections else text
    log.info("Combined %d sections into %d total chars", 
             len(extracted_sections), len(combined))
    return combined


# ---- 6.4  Public API -------------------------------------------------------

def get_lineage(
    caption_text: str,
    full_text: str,
    model,
    *,
    pdf_paths: Optional[List[Path]] = None,
    debug_dir: str | Path | None = None,
) -> Tuple[List[Variant], List[Campaign]]:
    """
    High-level wrapper used by the pipeline.

    1. Identify distinct campaigns in the manuscript.
    2. Use captions to ask Gemini where the lineage is likely described (fast & focused).
    3. Map locations to campaigns.
    4. Extract lineage for each campaign separately.
    5. Return both variants and campaigns.
    """
    # First, identify campaigns in the manuscript
    campaigns = identify_campaigns(full_text[:50_000], model, debug_dir=debug_dir)
    
    if campaigns:
        log.info(f"Identified {len(campaigns)} distinct campaigns")
        for camp in campaigns:
            log.info(f"  - {camp.campaign_name}: {camp.description}")
    
    # Use captions for identification - they're concise and focused
    locations = identify_evolution_locations(caption_text, model, debug_dir=debug_dir, campaigns=None, pdf_paths=pdf_paths)
    
    all_variants = []
    
    if locations and campaigns:
        # Log location information
        location_summary = []
        for loc in locations[:5]:
            if isinstance(loc, dict):
                location_summary.append(f"{loc.get('location', 'Unknown')} ({loc.get('type', 'unknown')}, confidence: {loc.get('confidence', 0)})")
            else:
                location_summary.append(str(loc))
        log.info("Gemini identified %d potential lineage locations: %s", 
                 len(locations), ", ".join(location_summary))
        
        # Extract context around each location for better decision making
        locations_with_context = []
        for loc in locations:
            location_str = loc.get('location', '') if isinstance(loc, dict) else str(loc)
            # Extract 1000 chars of context around the location
            context_text = _extract_text_at_locations(full_text, [loc], context_chars=500)
            locations_with_context.append({
                'location': loc,
                'context': context_text[:1000]  # First 1000 chars of extracted context
            })
        
        # For each campaign, ask Gemini to select the best location
        for campaign in campaigns:
            log.info(f"Processing campaign: {campaign.campaign_id}")
            
            # Build locations context string
            locations_str = ""
            for i, loc_ctx in enumerate(locations_with_context):
                loc = loc_ctx['location']
                context = loc_ctx['context']
                location_str = loc.get('location', '') if isinstance(loc, dict) else str(loc)
                location_type = loc.get('type', '') if isinstance(loc, dict) else 'unknown'
                confidence = loc.get('confidence', 0) if isinstance(loc, dict) else 0
                reason = loc.get('reason', '') if isinstance(loc, dict) else ''
                
                locations_str += f"\n{i+1}. {location_str} (Type: {location_type}, Confidence: {confidence})\n"
                locations_str += f"   Reason: {reason}\n"
                locations_str += f"   Context (first 500 chars):\n   {context[:500]}...\n"
            
            # Ask Gemini to select best location for this campaign
            best_location_prompt = _CAMPAIGN_BEST_LOCATION_PROMPT.format(
                campaign_id=campaign.campaign_id,
                campaign_name=campaign.campaign_name,
                description=campaign.description,
                identifiers=campaign.notes or "No specific identifiers provided",
                locations_with_context=locations_str
            )
            
            primary_location = None
            try:
                # Save prompt to debug if provided
                if debug_dir:
                    debug_path = Path(debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    prompt_file = debug_path / f"best_location_{campaign.campaign_id}_{int(time.time())}.txt"
                    _dump(f"=== BEST LOCATION PROMPT ===\nCampaign: {campaign.campaign_id}\n{'='*80}\n\n{best_location_prompt}", prompt_file)
                
                response = model.generate_content(best_location_prompt)
                response_text = _extract_text(response).strip()
                
                # Parse JSON response
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1].strip()
                    if response_text.startswith("json"):
                        response_text = response_text[4:].strip()
                
                best_loc_data = json.loads(response_text)
                selected_location = best_loc_data.get('location', '')
                confidence = best_loc_data.get('confidence', 0)
                reason = best_loc_data.get('reason', '')
                
                # Save response to debug if provided
                if debug_dir:
                    response_file = debug_path / f"best_location_response_{campaign.campaign_id}_{int(time.time())}.txt"
                    _dump(f"=== BEST LOCATION RESPONSE ===\nCampaign: {campaign.campaign_id}\nSelected: {selected_location}\nConfidence: {confidence}\nReason: {reason}\n{'='*80}", response_file)
                
                log.info(f"Selected location for {campaign.campaign_id}: {selected_location} (confidence: {confidence})")
                
                # Find the actual location object
                for loc in locations:
                    loc_str = loc.get('location', '') if isinstance(loc, dict) else str(loc)
                    if loc_str == selected_location:
                        primary_location = loc
                        break
                
                if not primary_location:
                    log.warning(f"Could not find selected location '{selected_location}' in locations list")
                    # Fall back to highest confidence location
                    primary_location = sorted(locations, 
                                            key=lambda x: x.get('confidence', 0) if isinstance(x, dict) else 0, 
                                            reverse=True)[0] if locations else None
                    
            except Exception as e:
                log.warning(f"Failed to select best location for campaign {campaign.campaign_id}: {e}")
                # Fall back to highest confidence location
                primary_location = sorted(locations, 
                                        key=lambda x: x.get('confidence', 0) if isinstance(x, dict) else 0, 
                                        reverse=True)[0] if locations else None
            
            if not primary_location:
                log.warning(f"No location found for campaign {campaign.campaign_id}")
                continue
            
            # Track if we successfully extracted from figure
            extracted_from_figure = False
            
            if isinstance(primary_location, dict):
                location_str = primary_location.get('location', '')
                location_type = primary_location.get('type', '')
                confidence = primary_location.get('confidence', 0)
                reason = primary_location.get('reason', '')
                
                # Only try figure extraction for high-confidence figures
                if location_type == 'figure' and confidence >= 80 and pdf_paths:
                    log.info("Primary lineage source is a high-confidence figure: %s (confidence: %d, reason: %s)", 
                             location_str, confidence, reason)
                    
                    # Try to extract the figure from available PDFs
                    figure_bytes = None
                    for pdf_path in pdf_paths:
                        figure_bytes = extract_figure(pdf_path, location_str, debug_dir=debug_dir)
                        if figure_bytes:
                            log.info("Successfully extracted figure from %s", pdf_path.name)
                            break
                    
                    if figure_bytes:
                        # Save figure to debug directory if provided
                        if debug_dir:
                            debug_path = Path(debug_dir)
                            debug_path.mkdir(parents=True, exist_ok=True)
                            figure_file = debug_path / f"lineage_figure_{location_str.replace(' ', '_')}_{int(time.time())}.png"
                            _dump(figure_bytes, figure_file)
                            log.info("Saved lineage figure to: %s", figure_file)
                        
                        # Extract lineage from the figure
                        variants = extract_lineage_from_figure(
                            figure_bytes, model, 
                            debug_dir=debug_dir, 
                            campaign_id=campaign.campaign_id,
                            campaign_info=campaign
                        )
                        if variants:
                            all_variants.extend(variants)
                            extracted_from_figure = True
                        else:
                            log.warning("Failed to extract lineage from figure, falling back to text extraction")
                    else:
                        log.warning("Could not extract figure '%s', falling back to text extraction", location_str)
                elif location_type == 'table':
                    log.info("Primary lineage source is a table: %s (confidence: %d, reason: %s)", 
                             location_str, confidence, reason)
            
            # Skip text extraction if we already got variants from figure
            if extracted_from_figure:
                continue
                
            # Use text-based extraction (works for tables and text sections)
            # Extract from full text, not caption text - use only primary location
            # Use more context for tables since they often span multiple pages
            context_size = 15000 if location_type == 'table' else 5000
            focused_text = _extract_text_at_locations(full_text, [primary_location], context_chars=context_size)
            log.info("Reduced text from %d to %d chars using primary location %s for campaign %s", 
                     len(full_text), len(focused_text), 
                     primary_location.get('location', 'Unknown') if isinstance(primary_location, dict) else 'Unknown',
                     campaign.campaign_id)
            
            # Extract lineage for this campaign
            campaign_variants = extract_complete_lineage(
                focused_text, model, 
                debug_dir=debug_dir, 
                campaign_id=campaign.campaign_id,
                campaign_info=campaign,
                pdf_paths=pdf_paths
            )
            all_variants.extend(campaign_variants)
        
        return all_variants, campaigns
    else:
        log.info("Gemini did not identify specific lineage locations")
        variants = extract_complete_lineage(full_text, model, debug_dir=debug_dir, pdf_paths=pdf_paths)
        return variants, campaigns

# === 7. SEQUENCE EXTRACTION === ----------------------------------------------
# Pull every protein and/or DNA sequence for each variant.
#   1. Ask Gemini where sequences live (cheap, quick prompt).
#   2. Ask Gemini to return the sequences in strict JSON.
#   3. Validate and convert to `SequenceBlock` objects.

# --- 7.0  JSON schema hint ----------------------------------------------------
_SEQUENCE_SCHEMA_HINT = """
[
  {
    "variant_id": "string",         // e.g. "IV-G2", "Round4-10"
    "aa_seq":    "string|null",     // uppercase amino acids or null
    "dna_seq":   "string|null"      // uppercase A/C/G/T or null
  }
]
""".strip()

# --- 7.1  Quick scan: where are the sequences? --------------------------------
_SEQ_LOC_PROMPT = """
Find where FULL-LENGTH protein or DNA sequences are located in this document.

PRIORITY: Protein/amino acid sequences are preferred over DNA sequences.

Look for table of contents entries or section listings that mention sequences.
Return a JSON array where each element has:
- "section": the section heading or description
- "page": the page number shown in the table of contents for this section, to your best judgement.

Focus on:
- Table of contents or entries about "Sequence Information" or "Nucleotide and amino acid sequences"
- Return the EXACT notation as shown.
- Prioritize sections that mention "protein" or "amino acid" sequences

Return [] if no sequence sections are found.
Absolutely don't include nucleotides or primer sequences, it is better to return nothing then incomplete sequence, use your best judgement.

TEXT (truncated):
```
{chunk}
```
""".strip()

def identify_sequence_locations(text: str, model, *, debug_dir: str | Path | None = None) -> list[dict]:
    """Ask Gemini for promising places to look for sequences."""
    prompt = _SEQ_LOC_PROMPT.format(chunk=text[:15_000])
    try:
        locs = generate_json_with_retry(model, prompt, debug_dir=debug_dir, tag="seq_locations")
        return locs if isinstance(locs, list) else []
    except Exception as exc:                                              # pylint: disable=broad-except
        log.warning("identify_sequence_locations(): %s", exc)
        return []

# --- 7.2  Page-based extraction helper ---------------------------------------
def _extract_text_from_page(pdf_paths: List[Path], page_num: Union[str, int], skip_si_toc: bool = True) -> str:
    """Extract text from a specific page number in the PDFs.
    
    Args:
        pdf_paths: List of PDF paths
        page_num: Page number (can be "S1", "S2", etc for SI pages)
        skip_si_toc: If True, skip first 2 pages of SI to avoid TOC
    """
    # Convert page number to int and handle S-prefix
    page_str = str(page_num).strip().upper()
    if page_str.startswith('S'):
        # Supplementary page - look in the SI PDF (second PDF)
        actual_page = int(page_str[1:]) - 1  # 0-indexed
        pdf_index = 1 if len(pdf_paths) > 1 else 0
        is_si_page = True
    else:
        # Regular page - look in the main PDF
        actual_page = int(page_str) - 1  # 0-indexed
        pdf_index = 0
        is_si_page = False
    
    # Skip first 2 pages of SI to avoid table of contents
    if skip_si_toc and is_si_page and actual_page < 2:
        log.info("Skipping SI page %s (first 2 pages are typically TOC)", page_str)
        return ""
    
    if pdf_index >= len(pdf_paths):
        log.warning("Page %s requested but not enough PDFs provided", page_str)
        return ""
    
    try:
        doc = fitz.open(pdf_paths[pdf_index])
        if 0 <= actual_page < len(doc):
            page = doc[actual_page]
            page_text = page.get_text()
            doc.close()
            log.info("Extracted %d chars from page %s of %s", 
                     len(page_text), page_str, pdf_paths[pdf_index].name)
            return page_text
        else:
            log.warning("Page %s (index %d) out of range for %s (has %d pages)", 
                       page_str, actual_page, pdf_paths[pdf_index].name, len(doc))
            doc.close()
            return ""
    except Exception as e:
        log.error("Failed to extract page %s: %s", page_str, e)
        return ""

# --- 7.3  Location validation with samples -----------------------------------
_LOC_VALIDATION_PROMPT = """
Which sample contains ACTUAL protein/DNA sequences (long strings of ACDEFGHIKLMNPQRSTVWY or ACGT)?
Not mutation lists, but actual sequences.

{samples}

Reply with ONLY a number: the location_id of the best sample (or -1 if none have sequences).
""".strip()

def validate_sequence_locations(text: str, locations: list, model, *, pdf_paths: List[Path] = None, debug_dir: str | Path | None = None) -> dict:
    """Extract samples from each location and ask Gemini to pick the best one."""
    if not locations:
        return {"best_location_id": -1, "reason": "No locations provided"}
    
    # Extract 500 char samples from each location
    samples = []
    for i, location in enumerate(locations[:5]):  # Limit to 5 locations
        sample_text = ""
        
        # If we have PDFs and location has a page number, use page extraction
        if pdf_paths and isinstance(location, dict) and 'page' in location:
            page_num = location['page']
            page_text = _extract_text_from_page(pdf_paths, page_num)
            
            # Also try to extract from the next page
            next_page_text = ""
            try:
                page_str = str(page_num).strip().upper()
                if page_str.startswith('S'):
                    next_page = f"S{int(page_str[1:]) + 1}"
                else:
                    next_page = str(int(page_str) + 1)
                next_page_text = _extract_text_from_page(pdf_paths, next_page)
            except:
                pass
            
            # Combine both pages
            combined_text = page_text + "\n" + next_page_text if next_page_text else page_text
            
            if combined_text:
                # Find the section within the combined pages if possible
                section = location.get('section', location.get('text', ''))
                if section:
                    # Try to find section in pages
                    section_lower = section.lower()
                    combined_lower = combined_text.lower()
                    pos = combined_lower.find(section_lower)
                    if pos >= 0:
                        # Extract from section start
                        sample_text = combined_text[pos:pos+5000]
                    else:
                        # Section not found, take from beginning
                        sample_text = combined_text[:10000]
                else:
                    # No section, take from beginning
                    sample_text = combined_text[:10000]
        
        # Fallback to text search if page extraction didn't work
        if not sample_text:
            sample_text = _extract_text_at_locations(
                text, [location], context_chars=2000, validate_sequences=False
            )
        
        samples.append({
            "location_id": i,
            "location": str(location),
            "sample": sample_text[:5000] if sample_text else ""
        })
    
    # Ask Gemini to analyze samples
    prompt = _LOC_VALIDATION_PROMPT.format(samples=json.dumps(samples, indent=2))
    
    # Save prompt for debugging
    if debug_dir:
        _dump(f"=== PROMPT FOR LOCATION_VALIDATION ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\n{'='*80}\n\n{prompt}",
              Path(debug_dir) / f"location_validation_prompt_{int(time.time())}.txt")
    
    try:
        # Get simple numeric response from Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Save response for debugging
        if debug_dir:
            _dump(f"=== RESPONSE FOR LOCATION_VALIDATION ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(response_text)} characters\n{'='*80}\n\n{response_text}",
                  Path(debug_dir) / f"location_validation_response_{int(time.time())}.txt")
        
        # Try to extract the number from response
        match = re.search(r'-?\d+', response_text)
        if match:
            best_id = int(match.group())
            return {"best_location_id": best_id, "reason": "Selected by Gemini"}
        else:
            log.warning("Could not parse location ID from response: %s", response_text)
            return {"best_location_id": -1, "reason": "Could not parse response"}
            
    except Exception as exc:
        log.warning("validate_sequence_locations(): %s", exc)
        return {"best_location_id": -1, "reason": str(exc)}

# --- 7.3  Main extraction prompt ---------------------------------------------
_SEQ_EXTRACTION_PROMPT = """
Extract EVERY distinct enzyme-variant sequence you can find in the text.

IMPORTANT: Prioritize amino acid (protein) sequences over DNA sequences:
- If an amino acid sequence exists for a variant, extract ONLY the aa_seq (set dna_seq to null)
- Only extract dna_seq if NO amino acid sequence is available for that variant
- This reduces redundancy since protein sequences are usually more relevant

CRITICAL: Use the EXACT variant identifier as it appears with each sequence:
- Papers often use different naming conventions in different sections
- DO NOT normalize or simplify variant IDs
- Extract the variant_id exactly as written where the sequence appears
- Common patterns include numeric IDs, generation labels, full descriptive names, or combinations

For each variant return:
  * variant_id  - the EXACT label as it appears with the sequence (preserve all formatting)
  * aa_seq      - amino-acid sequence (uppercase), or null
  * dna_seq     - DNA sequence (A/C/G/T), or null (ONLY if no aa_seq exists)

Respond ONLY with **minified JSON** that matches the schema below.
NO markdown, no code fences, no commentary.

Schema:
```json
{schema}
```

TEXT (may be truncated):
```
{text}
```
""".strip()

def extract_sequences(text: str, model, *, debug_dir: str | Path | None = None, lineage_context: str = None) -> list[SequenceBlock]:
    """Prompt Gemini and convert its JSON reply into SequenceBlock objects."""
    base_prompt = _SEQ_EXTRACTION_PROMPT.format(
        schema=_SEQUENCE_SCHEMA_HINT, text=text[:MAX_CHARS]
    )
    
    # Add lineage context if available
    if lineage_context:
        prompt = f"""{base_prompt}

IMPORTANT CONTEXT - Known variants from lineage extraction:
{lineage_context}

Match sequences to these known variants when possible. Variants may be labeled differently in different sections (e.g., "5295" might also appear as "ʟ-G0", "ʟ-ApPgb-αEsA-G0", or "ʟ-ApPgb-αEsA-G0 (5295)").
"""
    else:
        prompt = base_prompt
    
    data = generate_json_with_retry(model, prompt, _SEQUENCE_SCHEMA_HINT, debug_dir=debug_dir, tag="sequences")
    return _parse_sequences(data)

# --- 7.4  JSON -> dataclass helpers -------------------------------------------
_VALID_AA  = set("ACDEFGHIKLMNPQRSTVWY*")  # Include * for stop codon
_VALID_DNA = set("ACGT")

def _contains_sequence(text: str, min_length: int = 50) -> bool:
    """Check if text contains likely protein or DNA sequences."""
    # Remove whitespace for checking
    clean_text = re.sub(r'\s+', '', text.upper())
    
    # Check for continuous stretches of valid amino acids or DNA
    # Look for at least min_length consecutive valid characters
    aa_pattern = f"[{''.join(_VALID_AA)}]{{{min_length},}}"
    dna_pattern = f"[{''.join(_VALID_DNA)}]{{{min_length},}}"
    
    return bool(re.search(aa_pattern, clean_text) or re.search(dna_pattern, clean_text))

def _clean_seq(seq: str | None, alphabet: set[str]) -> str | None:
    if not seq:
        return None
    seq = re.sub(r"\s+", "", seq).upper()
    return seq if seq and all(ch in alphabet for ch in seq) else None

def _parse_sequences(raw: list[dict]) -> list[SequenceBlock]:
    """Validate and convert raw JSON into SequenceBlock instances."""
    blocks: list[SequenceBlock] = []
    for entry in raw:
        vid = (entry.get("variant_id") or entry.get("id") or "").strip()
        if not vid:
            continue
        aa  = _clean_seq(entry.get("aa_seq"),  _VALID_AA)
        dna = _clean_seq(entry.get("dna_seq"), _VALID_DNA)

        conf: float | None = None
        if aa:
            conf = sum(c in _VALID_AA  for c in aa)  / len(aa)
        elif dna:
            conf = sum(c in _VALID_DNA for c in dna) / len(dna)

        blocks.append(
            SequenceBlock(
                variant_id=vid,
                aa_seq=aa,
                dna_seq=dna,
                confidence=conf,
                truncated=False,
            )
        )
    return blocks

# --- 7.5  Convenience wrapper -------------------------------------------------
def get_sequences(text: str, model, *, pdf_paths: List[Path] = None, debug_dir: str | Path | None = None, lineage_variants: List[Variant] = None) -> list[SequenceBlock]:
    # Phase 1: Identify where sequences might be located
    locations = identify_sequence_locations(text, model, debug_dir=debug_dir)
    
    if locations:
        # Format location info for logging
        loc_strs = []
        for loc in locations[:5]:
            if isinstance(loc, dict):
                section = loc.get('section', loc.get('text', ''))
                page = loc.get('page', '')
                loc_strs.append(f"{section} (page {page})")
            else:
                loc_strs.append(str(loc))
        log.info("Gemini identified %d potential sequence locations: %s", 
                 len(locations), ", ".join(loc_strs))
        
        # Phase 2: Validate locations with sample extraction
        validation = validate_sequence_locations(text, locations, model, pdf_paths=pdf_paths, debug_dir=debug_dir)
        best_loc_id = validation.get("best_location_id", -1)
        
        if best_loc_id >= 0 and best_loc_id < len(locations):
            # Use the validated best location
            best_location = locations[best_loc_id]
            log.info("Using validated best location: %s (reason: %s)", 
                     loc_strs[best_loc_id] if best_loc_id < len(loc_strs) else str(best_location),
                     validation.get("reason", ""))
            
            # Extract with suggested strategy
            strategy = validation.get("extraction_strategy", {})
            start_offset = strategy.get("start_offset", 0)
            min_length = strategy.get("min_length", 30000)
            
            # Try page-based extraction first if we have page info
            focused_text = ""
            if pdf_paths and isinstance(best_location, dict) and 'page' in best_location:
                page_num = best_location['page']
                # Extract current page plus next 15 pages
                all_pages = []
                for i in range(16):  # Current + next 15
                    if isinstance(page_num, str) and page_num.upper().startswith('S'):
                        next_page = f"S{int(page_num[1:]) + i}"
                    else:
                        next_page = str(int(page_num) + i)
                    page_text = _extract_text_from_page(pdf_paths, next_page)
                    if page_text:
                        all_pages.append(page_text)
                    else:
                        break
                if all_pages:
                    focused_text = "\n".join(all_pages)
                    log.info("Extracted %d chars from pages %s through %d more pages", 
                             len(focused_text), page_num, len(all_pages) - 1)
            
            # Fallback to text search if page extraction didn't work
            if not focused_text:
                focused_text = _extract_text_at_locations(
                    text, [best_location], 
                    context_chars=max(min_length, 30000), 
                    validate_sequences=True
                )
            
            if focused_text and len(focused_text) < len(text):
                log.info("Reduced text from %d to %d chars using validated location", 
                         len(text), len(focused_text))
                # Build lineage context if available
                lineage_context = None
                if lineage_variants:
                    variant_info = []
                    for v in lineage_variants[:20]:  # Limit to first 20
                        info = f"- {v.variant_id} (Gen {v.generation})"
                        if v.mutations:
                            info += f" [{', '.join(v.mutations[:3])}{'...' if len(v.mutations) > 3 else ''}]"
                        variant_info.append(info)
                    lineage_context = "\n".join(variant_info)
                
                return extract_sequences(focused_text, model, debug_dir=debug_dir, lineage_context=lineage_context)
        else:
            log.warning("Location validation failed or returned invalid location: %s", 
                       validation.get("reason", "Unknown"))
    
    # Fallback to full text
    log.info("Using full text for sequence extraction")
    # Build lineage context if available
    lineage_context = None
    if lineage_variants:
        variant_info = []
        for v in lineage_variants[:20]:  # Limit to first 20
            info = f"- {v.variant_id} (Gen {v.generation})"
            if v.mutations:
                info += f" [{', '.join(v.mutations[:3])}{'...' if len(v.mutations) > 3 else ''}]"
            variant_info.append(info)
        lineage_context = "\n".join(variant_info)
    
    return extract_sequences(text, model, debug_dir=debug_dir, lineage_context=lineage_context)

# === 7.6 PDB SEQUENCE EXTRACTION === -----------------------------------------
"""When no sequences are found in the paper, attempt to fetch them from PDB."""

def fetch_pdb_sequences(pdb_id: str) -> Dict[str, str]:
    """Fetch protein sequences from PDB using RCSB API.
    
    Returns dict mapping chain IDs to sequences.
    """
    # Use the GraphQL API which is more reliable
    url = "https://data.rcsb.org/graphql"
    
    query = """
    query getSequences($pdb_id: String!) {
        entry(entry_id: $pdb_id) {
            polymer_entities {
                entity_poly {
                    pdbx_seq_one_letter_code_can
                }
                rcsb_polymer_entity_container_identifiers {
                    auth_asym_ids
                }
            }
        }
    }
    """
    
    try:
        import requests
        response = requests.post(
            url, 
            json={"query": query, "variables": {"pdb_id": pdb_id.upper()}},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        sequences = {}
        entry_data = data.get('data', {}).get('entry', {})
        
        if entry_data:
            for entity in entry_data.get('polymer_entities', []):
                # Get sequence
                seq_data = entity.get('entity_poly', {})
                sequence = seq_data.get('pdbx_seq_one_letter_code_can', '')
                
                # Get chain IDs
                chain_data = entity.get('rcsb_polymer_entity_container_identifiers', {})
                chain_ids = chain_data.get('auth_asym_ids', [])
                
                if sequence and chain_ids:
                    # Clean sequence - remove newlines and spaces
                    clean_seq = sequence.replace('\n', '').replace(' ', '').upper()
                    
                    # Add sequence for each chain
                    for chain_id in chain_ids:
                        sequences[chain_id] = clean_seq
                        log.info(f"PDB {pdb_id} chain {chain_id}: {len(clean_seq)} residues")
        
        return sequences
        
    except Exception as e:
        log.warning(f"Failed to fetch PDB {pdb_id}: {e}")
        return {}

def match_pdb_to_variants(
    pdb_sequences: Dict[str, str],
    variants: List[Variant],
    lineage_text: str,
    model,
    pdb_id: str = None,
) -> Dict[str, str]:
    """Match PDB chains to variant IDs using LLM analysis of mutations.
    
    Returns a mapping where each variant maps to at most one PDB chain.
    Since all chains from a single PDB typically have the same sequence,
    we match the PDB to a single variant based on context.
    """
    
    if not pdb_sequences or not variants:
        return {}
    
    # Extract context around PDB ID mentions if possible
    context_text = ""
    if pdb_id and lineage_text:
        # Search for PDB ID mentions in the text
        pdb_mentions = []
        text_lower = lineage_text.lower()
        pdb_lower = pdb_id.lower()
        
        # Find all occurrences of the PDB ID
        start = 0
        while True:
            pos = text_lower.find(pdb_lower, start)
            if pos == -1:
                break
            
            # Extract context around the mention (300 chars before, 300 after)
            context_start = max(0, pos - 300)
            context_end = min(len(lineage_text), pos + len(pdb_id) + 300)
            context = lineage_text[context_start:context_end]
            
            # Add ellipsis if truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(lineage_text):
                context = context + "..."
                
            pdb_mentions.append(context)
            start = pos + 1
        
        if pdb_mentions:
            context_text = "\n\n---\n\n".join(pdb_mentions[:3])  # Use up to 3 mentions
            log.info(f"Found {len(pdb_mentions)} mentions of PDB {pdb_id}")
        else:
            # Fallback to general context if no specific mentions found
            context_text = lineage_text[:2000]
    else:
        # Fallback to general context
        context_text = lineage_text[:2000] if lineage_text else ""
    
    # Get the first chain's sequence as representative (usually all chains have same sequence)
    first_chain = list(pdb_sequences.keys())[0]
    seq_preview = pdb_sequences[first_chain]
    seq_preview = f"{seq_preview[:50]}...{seq_preview[-20:]}" if len(seq_preview) > 70 else seq_preview
    
    # Build a prompt for Gemini to match ONE variant to this PDB
    prompt = f"""Given a PDB structure and enzyme variant information, identify which variant corresponds to this PDB structure.

PDB ID: {pdb_id or "Unknown"}
PDB Sequence (from chain {first_chain}):
{seq_preview}

Variant Information:
{json.dumps([{"id": v.variant_id, "mutations": v.mutations, "parent": v.parent_id, "generation": v.generation} for v in variants], indent=2)}

Context from paper mentioning the PDB:
{context_text}

Based on the context, identify which ONE variant this PDB structure represents.
Return ONLY the variant_id as a JSON string, e.g.: "ApePgb GLVRSQL"
"""
    
    try:
        response = model.generate_content(prompt)
        text = _extract_text(response).strip()
        
        # Parse JSON response (expecting a single string)
        if text.startswith("```"):
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        
        # Remove quotes if present
        text = text.strip('"\'')
        
        matched_variant = text
        log.info(f"PDB {pdb_id} matched to variant: {matched_variant}")
        
        # Return mapping with all chains pointing to the same variant
        mapping = {}
        if matched_variant and any(v.variant_id == matched_variant for v in variants):
            for chain_id in pdb_sequences:
                mapping[matched_variant] = chain_id
                break  # Only use the first chain
        
        return mapping
        
    except Exception as e:
        log.warning(f"Failed to match PDB to variant: {e}")
        # No fallback - return empty if we can't match
        return {}

# === 8. MERGE, VALIDATE & SCORE === ------------------------------------------
"""Glue logic to combine lineage records with sequence blocks and produce a
single tidy pandas DataFrame that downstream code (pipeline / CLI) can write
as CSV or further analyse.

Responsibilities
----------------
1. Merge: outer-join on `variant_id`, preserving every lineage row even if a
   sequence is missing.
2. Generation sanity-check: ensure generation numbers are integers >=0; if
   missing, infer by walking the lineage graph.
3. Confidence: propagate `SequenceBlock.confidence` or compute a simple score
   if only raw sequences are present.
4. DOI column: attach the article DOI to every row so the CSV is self-contained.
"""


# --- 8.1  Generation inference -------------------------------------------------

def _infer_generations(variants: List[Variant]) -> None:
    """Fill in missing `generation` fields by walking parent -> child edges.

    We build a directed graph of variant relationships and assign generation
    numbers by distance from the root(s).  If cycles exist (shouldn't!), they
    are broken arbitrarily and a warning is emitted.
    """
    graph = nx.DiGraph()
    for var in variants:
        graph.add_node(var.variant_id, obj=var)
        if var.parent_id:
            graph.add_edge(var.parent_id, var.variant_id)

    # Detect cycles just in case
    try:
        roots = [n for n, d in graph.in_degree() if d == 0]
        for root in roots:
            for node, depth in nx.single_source_shortest_path_length(graph, root).items():
                var: Variant = graph.nodes[node]["obj"]  # type: ignore[assignment]
                var.generation = depth if var.generation is None else var.generation
    except nx.NetworkXUnfeasible:
        log.warning("Cycle detected in lineage, generation inference skipped")

# --- 8.2  Merge helpers --------------------------------------------------------


def _merge_lineage_and_sequences(
    lineage: List[Variant], seqs: List[SequenceBlock], doi: Optional[str], model=None
) -> pd.DataFrame:
    """Return a tidy DataFrame with one row per variant."""

    # 1. Make DataFrames
    df_lin = pd.DataFrame([
        {
            "variant_id": v.variant_id,
            "parent_id": v.parent_id,
            "generation": v.generation,
            "mutations": ";".join(v.mutations) if v.mutations else None,
            "campaign_id": v.campaign_id,
            "notes": v.notes,
        }
        for v in lineage
    ])

    df_seq = pd.DataFrame([
        {
            "variant_id": s.variant_id,
            "aa_seq": s.aa_seq,
            "dna_seq": s.dna_seq,
            "seq_confidence": s.confidence,
            "truncated": s.truncated,
        }
        for s in seqs
    ])
    
    # Log sequence data info
    if len(df_seq) > 0:
        seq_with_aa = (~df_seq['aa_seq'].isna()).sum()
        seq_with_dna = (~df_seq['dna_seq'].isna()).sum()
        log.info(f"Sequence data: {len(df_seq)} entries, {seq_with_aa} with aa_seq, {seq_with_dna} with dna_seq")

    # 2. First try direct merge
    df = pd.merge(df_lin, df_seq, on="variant_id", how="left")
    
    # Log merge results
    merged_aa = (~df['aa_seq'].isna()).sum()
    merged_dna = (~df['dna_seq'].isna()).sum()
    log.info(f"After direct merge: {merged_aa} variants with aa_seq, {merged_dna} with dna_seq")
    
    # 3. If we have unmatched sequences and a model, use Gemini to match
    if model and len(df_seq) > 0 and df['aa_seq'].isna().any():
        # Find unmatched entries - consider entries missing if they lack BOTH aa_seq and dna_seq
        missing_seq = df['aa_seq'].isna() & df['dna_seq'].isna()
        unmatched_lineage_ids = df[missing_seq]['variant_id'].tolist()
        
        # Find unmatched sequences
        matched_seq_ids = df[~missing_seq]['variant_id'].tolist()
        unmatched_seqs = df_seq[~df_seq['variant_id'].isin(matched_seq_ids)]
        
        if unmatched_lineage_ids and len(unmatched_seqs) > 0:
            log.info(f"Found {len(unmatched_lineage_ids)} lineage entries without sequences")
            log.info(f"Found {len(unmatched_seqs)} unmatched sequences")
            log.info("Using Gemini to match variants")
            
            # Build prompt for Gemini
            prompt = f"""Match enzyme variant IDs between two lists from the same paper.

Papers often use different naming conventions for the same variant:
- Lineage sections may use numeric IDs (e.g., "5295") or IDs with parenthetical numbers (e.g., "ᴅ-G0 (5308)")
- Sequence sections may use descriptive names (e.g., "ʟ-ApPgb-αEsA-G0", "ᴅ-ApPgb-αEsA-G0")

Match variants by analyzing generation numbers, prefixes, and patterns.

Lineage variant IDs (need sequences):
{json.dumps(unmatched_lineage_ids)}

Sequence variant IDs (have sequences):
{json.dumps(unmatched_seqs['variant_id'].tolist())}

Return ONLY a JSON object mapping lineage IDs to sequence IDs.
Format: {{"lineage_id": "sequence_id", ...}}
"""
            
            try:
                response = model.generate_content(prompt)
                text = _extract_text(response).strip()
                
                # Parse JSON response
                if text.startswith("```"):
                    text = text.split("```")[1].strip()
                    if text.startswith("json"):
                        text = text[4:].strip()
                
                matches = json.loads(text)
                log.info(f"Gemini returned {len(matches)} matches")
                
                # Create a mapping of sequence IDs to their data for efficient lookup
                seq_data_map = {row['variant_id']: row for idx, row in unmatched_seqs.iterrows()}
                
                # Apply matches and update variant IDs
                for lineage_id, seq_id in matches.items():
                    if lineage_id in unmatched_lineage_ids and seq_id in seq_data_map:
                        # Get the sequence data
                        seq_data = seq_data_map[seq_id]
                        
                        # Update the row with the matched sequence ID and data
                        mask = df['variant_id'] == lineage_id
                        if mask.any():
                            # Update variant_id to use the sequence variant name
                            df.loc[mask, 'variant_id'] = seq_id
                            
                            # Update parent_id if it matches any of the mapped lineage IDs
                            parent_mask = df['parent_id'] == lineage_id
                            if parent_mask.any():
                                df.loc[parent_mask, 'parent_id'] = seq_id
                            
                            # Update sequence data
                            # For pandas Series from iterrows(), use proper indexing
                            aa_seq_val = seq_data['aa_seq'] if 'aa_seq' in seq_data else None
                            dna_seq_val = seq_data['dna_seq'] if 'dna_seq' in seq_data else None
                            
                            # Always update sequence fields to preserve DNA even when aa_seq is null
                            df.loc[mask, 'aa_seq'] = aa_seq_val
                            df.loc[mask, 'dna_seq'] = dna_seq_val
                                
                            df.loc[mask, 'seq_confidence'] = seq_data.get('seq_confidence', None)
                            df.loc[mask, 'truncated'] = seq_data.get('truncated', False)
                            
                            # Log sequence info - check both aa_seq and dna_seq
                            aa_len = len(seq_data['aa_seq']) if pd.notna(seq_data.get('aa_seq')) and seq_data.get('aa_seq') else 0
                            dna_len = len(seq_data['dna_seq']) if pd.notna(seq_data.get('dna_seq')) and seq_data.get('dna_seq') else 0
                            log.info(f"Matched {lineage_id} -> {seq_id} (aa_seq: {aa_len} chars, dna_seq: {dna_len} chars)")
                
                # Update any remaining parent_id references to matched variants
                for lineage_id, seq_id in matches.items():
                    parent_mask = df['parent_id'] == lineage_id
                    if parent_mask.any():
                        df.loc[parent_mask, 'parent_id'] = seq_id
                
                # Log final state - count variants with any sequence (aa or dna)
                aa_count = (~df['aa_seq'].isna()).sum()
                dna_count = (~df['dna_seq'].isna()).sum()
                any_seq_count = (~(df['aa_seq'].isna() & df['dna_seq'].isna())).sum()
                log.info(f"After Gemini matching: {any_seq_count}/{len(df)} variants have sequences (aa: {aa_count}, dna: {dna_count})")
                
            except Exception as e:
                log.warning(f"Failed to match variants using Gemini: {e}")

    # 4. If generation missing, try inference
    if df["generation"].isna().any():
        _infer_generations(lineage)
        # Need to update the generations based on the potentially updated variant IDs
        gen_map = {v.variant_id: v.generation for v in lineage}
        # Also create a map for any variant IDs that were replaced
        for idx, row in df.iterrows():
            variant_id = row['variant_id']
            if variant_id in gen_map:
                df.at[idx, 'generation'] = gen_map[variant_id]

    # 5. Attach DOI column
    df["doi"] = doi

    # 6. Sort by generation, then variant_id
    df = df.sort_values(["generation", "variant_id"], kind="mergesort")

    # 7. Log final state
    aa_count = (~df['aa_seq'].isna()).sum()
    dna_count = (~df['dna_seq'].isna()).sum()
    any_seq_count = (~(df['aa_seq'].isna() & df['dna_seq'].isna())).sum()
    log.info(f"Final result: {len(df)} variants, {any_seq_count} with sequences (aa: {aa_count}, dna: {dna_count})")

    return df

# --- 8.3  Public API -----------------------------------------------------------

def merge_and_score(
    lineage: List[Variant],
    seqs: List[SequenceBlock],
    doi: Optional[str] = None,
    model=None,
) -> pd.DataFrame:
    """Merge lineage and sequence data into a single DataFrame.
    
    Args:
        lineage: List of Variant objects from lineage extraction
        seqs: List of SequenceBlock objects from sequence extraction
        doi: DOI of the paper for provenance
        model: Gemini model for smart matching (optional)
    
    Returns:
        DataFrame with merged lineage and sequence data
    """
    if not lineage:
        raise ValueError("merge_and_score(): `lineage` list is empty; nothing to merge")

    df = _merge_lineage_and_sequences(lineage, seqs, doi, model)

    # Warn if many sequences are missing
    missing_rate = df["aa_seq"].isna().mean() if "aa_seq" in df else 1.0
    if missing_rate > 0.5:
        log.warning(">50%% of variants lack sequences (%d / %d)", df["aa_seq"].isna().sum(), len(df))

    return df

# -------------------------------------------------------------------- end 8 ---

# === 9. PIPELINE ORCHESTRATOR === --------------------------------------------
"""High-level function that ties together PDF parsing, LLM calls, merging, and
CSV export.  This is what both the CLI (Section 10) and other Python callers
should invoke.

**New behaviour (June 2025)** - The lineage table is now written to disk *before*
sequence extraction begins so that users keep partial results even if the
LLM stalls on the longer sequence prompt.  The same `--output` path is used;
we first save the lineage-only CSV, then overwrite it later with the merged
(final) DataFrame.
"""

import time
from pathlib import Path
from typing import Union
import pandas as pd


def _lineage_to_dataframe(lineage: list[Variant]) -> pd.DataFrame:
    """Convert a list[Variant] to a tidy DataFrame (helper for early dump)."""
    return pd.DataFrame(
        {
            "variant_id": [v.variant_id for v in lineage],
            "parent_id":  [v.parent_id for v in lineage],
            "generation": [v.generation for v in lineage],
            "mutations":  [";".join(v.mutations) if v.mutations else None for v in lineage],
            "campaign_id": [v.campaign_id for v in lineage],
            "notes":      [v.notes for v in lineage],
        }
    )


def run_pipeline(
    manuscript: Union[str, Path],
    si: Optional[Union[str, Path]] = None,
    output_csv: Optional[Union[str, Path]] = None,
    *,
    debug_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Execute the end-to-end extraction pipeline.

    Parameters
    ----------
    manuscript : str | Path
        Path to the main PDF file.
    si : str | Path | None, optional
        Path to the Supplementary Information PDF, if available.
    output_csv : str | Path | None, optional
        If provided, **both** the early lineage table *and* the final merged
        table will be written to this location (the final write overwrites
        the first).

    Returns
    -------
    pandas.DataFrame
        One row per variant with lineage, sequences, and provenance.
    """

    t0 = time.perf_counter()
    manuscript = Path(manuscript)
    si_path = Path(si) if si else None

    # 1. Prepare raw text ------------------------------------------------------
    # Always load both caption text (for identification) and full text (for extraction)
    pdf_paths = [p for p in (si_path, manuscript) if p]
    caption_text = limited_caption_concat(*pdf_paths)
    full_text = limited_concat(*pdf_paths)
    
    log.info("Loaded %d chars of captions for identification and %d chars of full text for extraction", 
             len(caption_text), len(full_text))

    # 2. Connect to Gemini -----------------------------------------------------
    model = get_model()

    # 3. Extract lineage (Section 6) ------------------------------------------
    lineage, campaigns = get_lineage(caption_text, full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir)

    if not lineage:
        raise RuntimeError("Pipeline aborted: failed to extract any lineage data")
    
    # Save campaigns info if debug_dir provided
    if debug_dir and campaigns:
        campaigns_file = Path(debug_dir) / "campaigns.json"
        campaigns_data = [
            {
                "campaign_id": c.campaign_id,
                "campaign_name": c.campaign_name,
                "description": c.description,
                "model_substrate": c.model_substrate,
                "model_product": c.model_product,
                "substrate_id": c.substrate_id,
                "product_id": c.product_id,
                "data_locations": c.data_locations,
                "notes": c.notes
            }
            for c in campaigns
        ]
        _dump(json.dumps(campaigns_data, indent=2), campaigns_file)
        log.info(f"Saved {len(campaigns)} campaigns to {campaigns_file}")

    # 3a. EARLY SAVE  -------------------------------------------------------------
    if output_csv:
        early_df = _lineage_to_dataframe(lineage)
        output_csv_path = Path(output_csv)
        # Save lineage-only data with specific filename
        lineage_path = output_csv_path.parent / "enzyme_lineage_data.csv"
        early_df.to_csv(lineage_path, index=False)
        log.info(
            "Saved lineage-only CSV -> %s",
            lineage_path,
        )

    # 4. Extract sequences (Section 7) ----------------------------------------
    sequences = get_sequences(full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir, lineage_variants=lineage)
    
    # 4a. Try PDB extraction if no sequences found -----------------------------
    # Check if we need PDB sequences (no sequences or only partial sequences)
    MIN_PROTEIN_LENGTH = 50  # Most proteins are >50 AA
    needs_pdb = (not sequences or 
                 all(s.aa_seq is None or (s.aa_seq and len(s.aa_seq) < MIN_PROTEIN_LENGTH) 
                     for s in sequences))
    
    if needs_pdb:
        log.info("No full-length sequences found in paper (only partial sequences < %d AA), attempting PDB extraction...", 
                 MIN_PROTEIN_LENGTH)
        
        # Extract PDB IDs from all PDFs
        pdb_ids = []
        for pdf_path in pdf_paths:
            pdb_ids.extend(extract_pdb_ids(pdf_path))
        
        if pdb_ids:
            log.info(f"Found PDB IDs: {pdb_ids}")
            
            # Try each PDB ID until we get sequences
            for pdb_id in pdb_ids:
                pdb_sequences = fetch_pdb_sequences(pdb_id)
                
                if pdb_sequences:
                    # Match PDB chains to variants
                    variant_to_chain = match_pdb_to_variants(
                        pdb_sequences, lineage, full_text, model, pdb_id
                    )
                    
                    # Convert to SequenceBlock objects
                    pdb_seq_blocks = []
                    for variant in lineage:
                        if variant.variant_id in variant_to_chain:
                            chain_id = variant_to_chain[variant.variant_id]
                            if chain_id in pdb_sequences:
                                seq_block = SequenceBlock(
                                    variant_id=variant.variant_id,
                                    aa_seq=pdb_sequences[chain_id],
                                    dna_seq=None,
                                    confidence=1.0,  # High confidence for PDB sequences
                                    truncated=False,
                                    metadata={"source": "PDB", "pdb_id": pdb_id, "chain": chain_id}
                                )
                                pdb_seq_blocks.append(seq_block)
                                log.info(f"Added PDB sequence for {variant.variant_id} from {pdb_id}:{chain_id}")
                    
                    if pdb_seq_blocks:
                        sequences = pdb_seq_blocks
                        log.info(f"Successfully extracted {len(pdb_seq_blocks)} sequences from PDB {pdb_id}")
                        break
                else:
                    log.warning(f"No sequences found in PDB {pdb_id}")
        else:
            log.warning("No PDB IDs found in paper")

    # 5. Merge & score (Section 8) --------------------------------------------
    doi = extract_doi(manuscript)
    df_final = merge_and_score(lineage, sequences, doi, model)

    # 6. Write FINAL CSV -------------------------------------------------------
    if output_csv:
        output_csv_path = Path(output_csv)
        # Save final data with sequences using same filename (overwrites lineage-only)
        sequence_path = output_csv_path.parent / "enzyme_lineage_data.csv"
        
        # Save the final CSV
        df_final.to_csv(sequence_path, index=False)
        
        # Log summary statistics
        seq_count = (~df_final['aa_seq'].isna()).sum() if 'aa_seq' in df_final else 0
        log.info(
            "Saved final CSV -> %s (%.1f kB, %d variants, %d with sequences)",
            sequence_path,
            sequence_path.stat().st_size / 1024,
            len(df_final),
            seq_count
        )

    log.info(
        "Pipeline finished in %.2f s (variants: %d)",
        time.perf_counter() - t0,
        len(df_final),
    )
    return df_final

# -------------------------------------------------------------------- end 9 ---

# === 10. CLI ENTRYPOINT === ----------------------------------------------
"""Simple argparse wrapper so the script can be run from the command line

Example:

    python enzyme_lineage_extractor.py \
        --manuscript paper.pdf \
        --si supp.pdf \
        --output lineage.csv \
        --captions-only -v
"""

import argparse
import logging
from typing import List, Optional


# -- 10.1  Argument parser ----------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="enzyme_lineage_extractor",
        description="Extract enzyme variant lineage and sequences from PDFs using Google Gemini",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, help="Path to main manuscript PDF")
    p.add_argument("--si", help="Path to Supplementary Information PDF")
    p.add_argument("-o", "--output", help="CSV file for extracted data")
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity; repeat (-vv) for DEBUG logging",
    )
    p.add_argument(
    "--debug-dir",
    metavar="DIR",
    help="Write ALL intermediate artefacts (captions, prompts, raw Gemini replies) to DIR",
    )
    return p


# -- 10.2  main() -------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Configure logging early so everything respects the chosen level.
    level = logging.DEBUG if args.verbose >= 2 else logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    run_pipeline(
        manuscript=args.manuscript,
        si=args.si,
        output_csv=args.output,
        debug_dir=args.debug_dir,
    )


if __name__ == "__main__":
    main()

# -------------------------------------------------------------------- end 10 ---

