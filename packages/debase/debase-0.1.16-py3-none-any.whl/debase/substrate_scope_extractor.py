"""substrate_scope_extractor.py

Single-file, maintainable CLI tool that extracts the *substrate scope* table
from one or two PDFs (manuscript + SI) using Google Gemini (or compatible).

The file mirrors the *section layout* and logging/debug philosophy of
`enzyme_lineage_extractor.py` so that both tools share a consistent developer
experience and can even live in the same package.

Navigate quickly by jumping to the numbered headers:

    # === 1. CONFIG & CONSTANTS ===
    # === 2. DOMAIN MODELS ===
    # === 3. LOGGING HELPERS ===
    # === 4. PDF HELPERS ===
    # === 5. LLM (GEMINI) HELPERS ===
    # === 6. SCOPE EXTRACTION ===
    # === 7. VALIDATION & MERGE ===
    # === 8. PIPELINE ORCHESTRATOR ===
    # === 9. CLI ENTRYPOINT ===
"""

# === 1. CONFIG & CONSTANTS ===
from __future__ import annotations

import os
import re
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

MODEL_NAME: str = "gemini-2.5-flash"
MAX_CHARS: int = 150_000           # Max characters sent to LLM
BATCH_SIZE: int = 10               # Batch size when extracting reactions
MAX_RETRIES: int = 4               # LLM retry loop
CACHE_DIR: Path = Path.home() / ".cache" / "substrate_scope"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# === 2. DOMAIN MODELS ===
@dataclass
class SubstrateProduct:
    """Chemical entity in a substrate scope reaction."""
    name: str
    iupac_name: Optional[str] = None

@dataclass
class Cofactor:
    """Cofactor with optional IUPAC name and role."""
    name: str
    iupac_name: Optional[str] = None
    role: Optional[str] = None

@dataclass
class ReactionConditions:
    """Reaction conditions for substrate scope."""
    temperature: Optional[str] = None
    ph: Optional[str] = None
    substrate_concentration: Optional[str] = None
    buffer: Optional[str] = None
    other_conditions: Optional[str] = None

@dataclass
class ScopeEntry:
    """Single substrate scope reaction data point."""
    enzyme_id: str
    substrates: List[SubstrateProduct] = field(default_factory=list)
    products: List[SubstrateProduct] = field(default_factory=list)
    cofactors: List[Cofactor] = field(default_factory=list)
    
    # Performance metrics
    yield_percent: Optional[float] = None
    ttn: Optional[float] = None
    ee: Optional[float] = None
    
    # Reaction conditions
    conditions: ReactionConditions = field(default_factory=ReactionConditions)
    
    # Metadata
    data_location: Optional[str] = None
    data_source_type: Dict[str, str] = field(default_factory=dict)
    
    # Lineage information (populated during merge)
    parent_id: Optional[str] = None
    mutations: Optional[str] = None
    generation: Optional[int] = None
    aa_seq: Optional[str] = None
    dna_seq: Optional[str] = None
    confidence: Optional[float] = None
    notes: str = ""

@dataclass
class CompoundMapping:
    """Mapping between compound identifiers and IUPAC names."""
    identifiers: List[str]
    iupac_name: str
    common_names: List[str] = field(default_factory=list)
    compound_type: str = "unknown"
    source_location: Optional[str] = None

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

# === 4. PDF HELPERS ===
try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required for PDF parsing. Install with `pip install pymupdf`."
    ) from exc

from base64 import b64encode

# Improved caption prefix regex - captures most journal variants
# Simplified pattern: match any line starting with Table, Figure, Scheme, Chart, etc.
# This catches all variations including "Table S 2", "Figure.", etc.
_CAPTION_PREFIX_RE = re.compile(
    r"^(Table|Figure|Fig|Scheme|Chart|Extended\s+Data\s+Fig|ED\s+Fig|Supplementary\s+(?:Table|Figure)).*",
    re.I | re.M
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
    """Extract figure/table captions using the improved regex."""
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
                        # Found a caption start - collect lines
                        caption_parts = [line]
                        for j in range(i + 1, len(block_lines)):
                            next_line = block_lines[j]
                            if not next_line:  # Empty line signals end
                                break
                            if _CAPTION_PREFIX_RE.match(next_line):
                                break
                            caption_parts.append(next_line)
                        
                        full_caption = " ".join(caption_parts)
                        captions.append(full_caption)
    finally:
        doc.close()
    
    joined = "\n".join(captions)
    return joined[:max_chars]

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
    """Concatenate caption text and SI table of contents from PDFs, trimmed to `max_chars`."""
    total = 0
    chunks: list[str] = []
    
    for idx, p in enumerate(pdf_paths):
        # For SI (second PDF), first extract table of contents pages
        if idx == 1:  # SI document
            doc = _open_doc(p)
            try:
                # Extract first few pages which typically contain TOC
                toc_text = []
                for page_num in range(min(5, doc.page_count)):
                    if total >= max_chars:
                        break
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    
                    # Look for TOC indicators
                    if any(indicator in page_text.lower() for indicator in 
                           ['table of contents', 'supporting information', 'contents', 'page']):
                        toc_text.append(f"\n[SI TOC Page {page_num + 1}]\n{page_text}")
                        total += len(page_text)
                
                if toc_text:
                    chunks.extend(toc_text)
            finally:
                doc.close()
        
        # Extract captions
        if total < max_chars:
            t = extract_captions(p)
            if total + len(t) > max_chars:
                t = t[: max_chars - total]
            chunks.append(t)
            total += len(t)
            if total >= max_chars:
                break
    
    return "\n".join(chunks)

def extract_figure_image(pdf_paths: List[Path], figure_ref: str) -> Optional[str]:
    """Extract figure as a page region when embedded images aren't available.
    
    Args:
        pdf_paths: List of PDF paths to search
        figure_ref: Figure reference to search for (e.g., "Figure 3" or "Figure 3(a)")
        
    Returns:
        Base64-encoded PNG string or None if not found
    """
    if not pdf_paths:
        return None
    
    # Always extract the base figure number, removing sub-letters like (a), (b), c, etc.
    import re
    # Match patterns like "Figure 1", "Figure 1c", "Figure 1(c)", "Fig. 1", etc.
    base_figure_match = re.match(r'((?:Figure|Fig\.?)\s*\d+)', figure_ref, re.IGNORECASE)
    if base_figure_match:
        base_figure_ref = base_figure_match.group(1)
        log.info("Extracting entire figure '%s' from reference '%s'", base_figure_ref, figure_ref)
    else:
        base_figure_ref = figure_ref
        
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Check if this page contains the figure caption
                found = False
                caption_instances = None
                
                # Look for figure caption
                variations = [
                    f"{base_figure_ref}.",  # "Figure 1." - most reliable
                    f"{base_figure_ref} ",  # "Figure 1 "
                    base_figure_ref,
                ]
                
                for variation in variations:
                    caption_instances = page.search_for(variation, quads=False)
                    if caption_instances:
                        # Check if this is likely a caption (not a reference in text)
                        for rect in caption_instances:
                            # Get text around this location
                            x0, y0, x1, y1 = rect
                            text_around = page.get_textbox(fitz.Rect(x0-50, y0-5, x1+300, y1+20))
                            # Check if it looks like a figure caption
                            if any(keyword in text_around.lower() for keyword in 
                                   ['directed evolution', 'substrate scope', '(a)', '(b)', '(c)']):
                                found = True
                                caption_rect = rect
                                break
                        if found:
                            break
                
                if not found:
                    continue
                
                log.info("Found figure caption on page %d at y=%.0f", page_num + 1, caption_rect.y0)
                
                # Extract a region of the page above the caption
                # The figure should be between the top of the viewable area and the caption
                page_rect = page.rect
                
                # Define the region to extract
                # Extract everything above the caption
                top_margin = 0  # Start from the very top of the page
                bottom_margin = 5  # Small margin above caption
                left_margin = 0  # Use full page width
                right_margin = 0
                
                # Calculate the figure region - everything from top to caption
                fig_top = top_margin
                fig_bottom = caption_rect.y0 - bottom_margin
                fig_left = left_margin
                fig_right = page_rect.width - right_margin
                
                # Create the clip rectangle
                clip_rect = fitz.Rect(fig_left, fig_top, fig_right, fig_bottom)
                
                # Extract the region as an image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                pix = page.get_pixmap(clip=clip_rect, matrix=mat)
                
                # Convert to PNG
                img_bytes = pix.tobytes("png")
                log.info("Extracted figure region: %.0fx%.0f pixels from page %d", 
                         clip_rect.width * 2, clip_rect.height * 2, page_num + 1)
                
                return b64encode(img_bytes).decode()
                
        finally:
            doc.close()
    
    log.warning("Could not find figure caption for '%s'", figure_ref)
    return None

def extract_scheme_image(pdf_paths: List[Path], scheme_ref: str) -> Optional[str]:
    """Extract scheme as a page region, similar to figures.
    
    Args:
        pdf_paths: List of PDF paths to search
        scheme_ref: Scheme reference to search for (e.g., "Scheme 2" or "Scheme S2")
        
    Returns:
        Base64-encoded PNG string or None if not found
    """
    if not pdf_paths:
        return None
    
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Check if this page contains the scheme
                found = False
                scheme_instances = None
                
                # Look for scheme reference with various patterns
                variations = [
                    f"{scheme_ref}.",  # "Scheme 2."
                    f"{scheme_ref}:",  # "Scheme 2:"
                    f"{scheme_ref} ",  # "Scheme 2 "
                    scheme_ref,
                ]
                
                for variation in variations:
                    scheme_instances = page.search_for(variation, quads=False)
                    if scheme_instances:
                        # Check if this is likely a scheme title (not a reference in text)
                        for rect in scheme_instances:
                            # Get text around this location
                            x0, y0, x1, y1 = rect
                            text_around = page.get_textbox(fitz.Rect(x0-50, y0-5, x1+400, y1+20))
                            # Check if it looks like a scheme title
                            if any(keyword in text_around.lower() for keyword in 
                                   ['substrate scope', 'reaction', 'synthesis', 'procedure', 'explored']):
                                found = True
                                scheme_rect = rect
                                break
                        if found:
                            break
                
                if not found:
                    continue
                
                log.info("Found scheme on page %d at y=%.0f", page_num + 1, scheme_rect.y0)
                
                # For schemes, we often want to capture more of the page
                # since they can be large and include multiple reactions
                page_rect = page.rect
                
                # Define the region to extract
                # For schemes, we want to capture everything below the title
                # until we hit significant text (which would be the next section)
                top_margin = max(0, scheme_rect.y1 + 5)  # Start just below the scheme title
                
                # Look for the next major text block that might indicate end of scheme
                # This is a simple heuristic - look for blocks of text below the scheme
                text_blocks = page.get_text("blocks")
                bottom_y = page_rect.height  # Default to full page
                
                for block in text_blocks:
                    block_y = block[1]  # y-coordinate of block
                    block_text = block[4]  # text content
                    # If we find a substantial text block below the scheme title
                    if block_y > scheme_rect.y1 + 50 and len(block_text) > 100:
                        # This might be the next section
                        bottom_y = block_y - 10
                        break
                
                # Create the clip rectangle
                clip_rect = fitz.Rect(0, top_margin, page_rect.width, bottom_y)
                
                # Extract the region as an image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                pix = page.get_pixmap(clip=clip_rect, matrix=mat)
                
                # Convert to PNG
                img_bytes = pix.tobytes("png")
                log.info("Extracted scheme region: %.0fx%.0f pixels from page %d", 
                         clip_rect.width * 2, clip_rect.height * 2, page_num + 1)
                
                return b64encode(img_bytes).decode()
                
        finally:
            doc.close()
    
    log.warning("Could not find scheme '%s'", scheme_ref)
    return None


def _extract_text_around_reference(pdf_paths: List[Path], ref: str, context_chars: int = 2000) -> str:
    """Extract text around a specific reference (e.g., 'Figure 3')."""
    import re
    extracted_sections = []
    
    # Try to extract base figure/table reference
    base_ref_match = re.match(r'((?:Figure|Fig|Table)\s*\d+)', ref, re.IGNORECASE)
    base_ref = base_ref_match.group(1) if base_ref_match else ref
    
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Try different variations of the reference
                ref_variations = [
                    ref,  # Original (e.g., "Figure 3(a)")
                    base_ref,  # Base reference (e.g., "Figure 3")
                    ref.replace("(", " ").replace(")", ""),  # "Figure 3 a"
                    ref.replace("(", "").replace(")", ""),    # "Figure 3a"
                    ref.replace("Figure", "Fig"),  # "Fig 3(a)"
                    base_ref.replace("Figure", "Fig"),  # "Fig 3"
                ]
                
                # Find the reference in the page
                found = False
                pos = -1
                used_ref = ref
                
                for ref_var in ref_variations:
                    if ref_var.lower() in page_text.lower():
                        pos = page_text.lower().find(ref_var.lower())
                        used_ref = ref_var
                        found = True
                        break
                
                if found and pos >= 0:
                    # Extract context around it
                    start = max(0, pos - context_chars)
                    end = min(len(page_text), pos + len(used_ref) + context_chars)
                    
                    section = page_text[start:end]
                    extracted_sections.append(
                        f"\n=== Context around '{ref}' (found as '{used_ref}') in {pdf_path.name}, page {page_num + 1} ===\n{section}"
                    )
                    log.debug("Found '%s' as '%s' on page %d of %s", ref, used_ref, page_num + 1, pdf_path.name)
        finally:
            doc.close()
    
    if not extracted_sections:
        log.warning("Could not find reference '%s' or base reference '%s' in any PDF", ref, base_ref)
    
    return "\n".join(extracted_sections)

def _extract_sections_by_title(pdf_paths: List[Path], section_titles: List[str], max_chars_per_section: int = 10000) -> str:
    """Extract sections by their titles from PDFs."""
    import re
    extracted_sections = []
    
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            # Build full text with page markers
            pages_text = []
            for i, page in enumerate(doc):
                page_text = page.get_text()
                pages_text.append(f"\n[PAGE {i+1}]\n{page_text}")
            full_text = "".join(pages_text)
            
            for title in section_titles:
                # Find section start
                title_pattern = re.escape(title)
                match = re.search(rf'{title_pattern}', full_text, re.IGNORECASE)
                
                if match:
                    start_pos = match.start()
                    
                    # Find the page number
                    page_match = re.search(r'\[PAGE (\d+)\]', full_text[:start_pos][::-1])
                    page_num = "unknown"
                    if page_match:
                        page_num = page_match.group(1)[::-1]
                    
                    # Try to find the next section header
                    next_section_patterns = [
                        r'\n[A-Z][A-Za-z\s]+:\s*\n',  # "Section Title:\n"
                        r'\n\d+\.\s+[A-Z]',  # "1. Next Section"
                        r'\n[A-Z]{2,}[A-Z\s]*\n',  # "SECTION HEADER\n"
                        r'\nReferences\s*\n',
                        r'\nAcknowledg',
                        r'\n\[PAGE \d+\]',  # Next page
                    ]
                    
                    end_pos = len(full_text)
                    for pattern in next_section_patterns:
                        next_match = re.search(pattern, full_text[start_pos + 100:], re.IGNORECASE)
                        if next_match:
                            end_pos = min(end_pos, start_pos + 100 + next_match.start())
                    
                    # Extract section with size limit
                    section_text = full_text[start_pos:min(start_pos + max_chars_per_section, end_pos)]
                    
                    # Clean up page markers
                    section_text = re.sub(r'\[PAGE \d+\]', '', section_text)
                    
                    extracted_sections.append(
                        f"\n=== Section: '{title}' from {pdf_path.name} (starting page {page_num}) ===\n{section_text}"
                    )
                    log.info("Extracted section '%s' (%d chars) from %s", 
                            title, len(section_text), pdf_path.name)
        finally:
            doc.close()
    
    return "\n".join(extracted_sections)

def _extract_text_from_page(pdf_paths: List[Path], page_num: Union[str, int]) -> str:
    """Extract text from a specific page number in the PDFs."""
    # Convert page number to int and handle S-prefix
    page_str = str(page_num).strip().upper()
    if page_str.startswith('S'):
        # Supplementary page - look in the SI PDF (second PDF)
        actual_page = int(page_str[1:]) - 1  # 0-indexed
        pdf_index = 1 if len(pdf_paths) > 1 else 0
    else:
        # Regular page - look in the main PDF
        actual_page = int(page_str) - 1  # 0-indexed
        pdf_index = 0
    
    if pdf_index >= len(pdf_paths):
        log.warning("Page %s requested but not enough PDFs provided", page_str)
        return ""
    
    try:
        doc = _open_doc(pdf_paths[pdf_index])
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

def _extract_text_from_pages(pdf_paths: List[Path], page_nums: List[Union[str, int]], max_pages: int = 10) -> str:
    """Extract text from multiple page numbers."""
    all_text = []
    pages_extracted = 0
    
    for page_num in page_nums[:max_pages]:
        page_text = _extract_text_from_page(pdf_paths, page_num)
        if page_text:
            all_text.append(f"\n[PAGE {page_num}]\n{page_text}")
            pages_extracted += 1
    
    if pages_extracted == 0:
        log.warning("No pages extracted from requested pages: %s", page_nums[:5])
    else:
        log.info("Extracted text from %d pages", pages_extracted)
    return "\n".join(all_text)

# === 5. LLM (GEMINI) HELPERS === ---------------------------------------------
from typing import Tuple

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
    debug_dir: str | Path | None = None,
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

# === 6. SCOPE EXTRACTION ===
"""
Substrate scope extraction with compound mapping, enzyme-substrate pairing,
and individual reaction extraction.
"""

# ---- 6.1  Prompt templates -------------------------------------------------

_SCOPE_LOC_PROMPT = """
You are an expert reader of biocatalysis manuscripts.
Analyze this paper and identify all locations containing substrate scope data.

Your task is to:
1. Identify all locations (tables, figures, text) containing substrate scope reaction data
2. Distinguish substrate scope studies from model reactions used for evolution
3. Determine which enzyme variants were tested in substrate scope studies
4. Note if multiple substrates are tested with the same enzyme variant

Return your analysis as JSON array (max {max_results} locations):
[
  {{
    "location": "e.g., SI Table 4, Figure 3, etc.",
    "type": "table/figure/text",
    "confidence": 0-100,
    "reason": "why this contains substrate scope",
    "enzyme_variants_tested": ["list", "of", "enzyme", "variants"],
    "number_of_substrates": "approximate number"
  }}
]
""".strip()

_IUPAC_SECTION_PROMPT = """
Analyze the provided Supporting Information table of contents pages to identify sections containing compound IUPAC names.

Look for sections that contain:
1. "Synthesis" of compounds with numbered identifiers
2. "Characterization" data for compounds
3. "General procedure" sections listing compounds
4. "NMR spectra" or "MS data" sections

IMPORTANT:
- Return the EXACT page range where compounds are characterized
- Use S prefix for supplementary pages (e.g., "S22-S30" not "22-30")
- Include both starting AND ending page numbers

Return JSON:
{
  "iupac_sections": [
    {
      "section": "exact section title as written",
      "page_range": "page range (e.g., 'S22-S45')",
      "description": "what compounds are described"
    }
  ]
}
""".strip()

_COMPOUND_MAPPING_PROMPT = """
Extract compound identifiers and their chemical names from the provided text and any scheme images.

TASK:
1. First, extract all compound IDs and names that are explicitly written in the text
2. Then, analyze any provided scheme images to identify compound labeling patterns
3. Look for relationships between compounds (e.g., when multiple variants share a base structure)
4. Note any systematic naming conventions used in the schemes

ANALYSIS GUIDELINES:
- Some papers define a base compound and use letter suffixes for variants
- Schemes often show relationships that aren't explicitly stated in text
- Pay attention to how compounds are grouped or connected in schemes
- Identify any patterns in how compounds are numbered/lettered

For each compound:
- identifier: The exact compound ID as written
- iupac_name: The chemical name if found in text
- common_names: Any alternative names
- compound_type: substrate/product/reagent/catalyst/other
- source_location: Where found (text excerpt or "Scheme X")
- related_compounds: List of related compound IDs if a pattern is detected
- pattern_notes: Description of any labeling pattern observed

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "string",
      "iupac_name": "string or null", 
      "common_names": ["array of strings"],
      "compound_type": "string",
      "source_location": "string",
      "related_compounds": ["array of related IDs"],
      "pattern_notes": "string or null"
    }
  ]
}
""".strip()

_SUBSTRATE_SCOPE_PROMPT = """
Extract ALL substrate scope data from the primary sources in one complete extraction.
{extraction_hints}

For EACH reaction, extract:
1. Enzyme variant ID
2. Substrate identifiers (e.g., "6a", "5") - ONLY if explicitly shown
3. Product identifiers (e.g., "7a", "7b", "7d", "7e") - ALWAYS include even if no yield
4. Performance metrics (yield%, ee%, dr, TTN)
5. Reaction conditions (temperature, pH, buffer, substrate concentrations - NOT dithionite/reducing agents)
6. Data location (which figure/table this comes from)

CRITICAL - NO HALLUCINATION OR INFERENCE OF IDENTIFIERS:
- SUBSTRATE IDS: Only extract substrate identifiers that are EXPLICITLY WRITTEN in the source
- DO NOT INFER substrate IDs from patterns (e.g., if you see product "4a", DO NOT assume substrate is "3a")
- If substrate ID is not explicitly shown, use null for substrate_ids
- Product IDs should be extracted as shown (since they are usually labeled in schemes)
- Extract values EXACTLY as written in the primary source - NO CHANGES WHATSOEVER
- DO NOT round, estimate, convert, or modify any numbers
- If the text shows "53%", report 53.0, not 53 or 53.00
- If the text shows "<5%", report exactly "<5" as a string in notes, yield_percent=null
- If the text shows "trace", report exactly "trace" in notes, yield_percent=null
- If the text shows "n.d.", report exactly "n.d." in notes, yield_percent=null
- If the text shows "80:20 er", calculate ee as 60.0 (|80-20|)
- If the text shows "91% ee", report ee_percent as 91.0
- If no value is shown, return null, not 0 or empty string
- Extract ALL reactions from ALL identified locations
- Use compound identifiers EXACTLY as shown (not IUPAC names)
- Extract reaction conditions EXACTLY as written - NO PARAPHRASING
- IMPORTANT: Substrate concentration refers to the concentration of the actual chemical substrates being transformed in the reaction, NOT reducing agents (e.g., dithionite, NADH) or other additives

IMPORTANT: 
- Substrate IDs must be EXPLICITLY visible in the source - DO NOT INFER FROM PATTERNS
- Product IDs should be extracted as labeled in the scheme/figure
- If only product ID is shown with yields/ee data, substrate_ids should be null

Return as JSON:
{{
  "substrate_scope_data": [
    {{
      "enzyme_id": "enzyme variant name",
      "substrate_ids": null or ["list of EXPLICITLY shown substrate identifiers"],
      "product_ids": ["list of product identifiers"],
      "yield_percent": null or number,
      "ee_percent": null or number,
      "dr": "ratio if reported",
      "ttn": null or number,
      "reaction_conditions": {{
        "temperature": "",
        "ph": "",
        "buffer": "",
        "substrate_concentration": "concentration of actual substrates/reagents, NOT reducing agents like dithionite",
        "other_conditions": "including enzyme loading, reducing agents (e.g., dithionite), time, etc."
      }},
      "data_location": "specific figure/table",
      "notes": "any special notes (e.g., 'no product detected')"
    }}
  ]
}}
""".strip()


# ---- 6.2  Helper functions -------------------------------------------------

def identify_scope_locations(
    text: str,
    model,
    *,
    max_results: int = 5,
    debug_dir: str | Path | None = None,
) -> List[dict]:
    """Ask Gemini where substrate scope data is located."""
    prompt = _SCOPE_LOC_PROMPT.format(max_results=max_results) + "\n\nTEXT:\n" + text[:15_000]
    locs: List[dict] = []
    try:
        locs = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="scope_locate",
        )
    except Exception as exc:  # pragma: no cover
        log.warning("identify_scope_locations(): %s", exc)
    return locs if isinstance(locs, list) else []

def identify_iupac_sections(
    text: str,
    model,
    *,
    pdf_paths: List[Path] = None,
    debug_dir: str | Path | None = None,
) -> List[dict]:
    """Identify sections containing IUPAC names from SI table of contents."""
    # Extract only SI TOC pages (first 5 pages of SI)
    si_toc_text = ""
    if pdf_paths and len(pdf_paths) > 1:
        si_pdf = pdf_paths[1]  # Second PDF is SI
        doc = _open_doc(si_pdf)
        try:
            for page_num in range(min(5, doc.page_count)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                si_toc_text += f"\n[SI Page {page_num + 1}]\n{page_text}"
        finally:
            doc.close()
    
    if not si_toc_text:
        # Fallback to caption text
        si_toc_text = text[:15_000]
    
    prompt = _IUPAC_SECTION_PROMPT + "\n\nTEXT:\n" + si_toc_text
    
    try:
        data = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="iupac_sections",
        )
        
        sections = data.get("iupac_sections", []) if isinstance(data, dict) else []
        log.info("Identified %d sections containing IUPAC names", len(sections))
        return sections
        
    except Exception as exc:
        log.warning("Failed to identify IUPAC sections: %s", exc)
        return []

def _extract_compound_mappings_from_text(
    extraction_text: str,
    model,
    compound_ids: List[str] = None,
    debug_dir: str | Path | None = None,
    tag_suffix: str = "",
) -> Dict[str, CompoundMapping]:
    """Helper function to extract compound mappings from provided text."""
    prompt = _COMPOUND_MAPPING_PROMPT
    if compound_ids:
        prompt += "\n\nCOMPOUNDS TO MAP: " + ", ".join(sorted(compound_ids))
    prompt += "\n\nTEXT:\n" + extraction_text
    
    tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
    
    try:
        data = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag=tag,
        )
        
        mappings = {}
        compound_mappings_data = data.get("compound_mappings") or []
        for item in compound_mappings_data:
            # Handle both old format (with identifiers list) and new format (with identifier string)
            identifiers = item.get("identifiers") or []
            if not identifiers and item.get("identifier"):
                identifiers = [item.get("identifier")]
            
            mapping = CompoundMapping(
                identifiers=identifiers,
                iupac_name=item.get("iupac_name", ""),
                common_names=item.get("common_names") or [],
                compound_type=item.get("compound_type", "unknown"),
                source_location=item.get("source_location")
            )
            
            # Store pattern information for post-processing
            mapping._related_compounds = item.get("related_compounds", [])
            mapping._pattern_notes = item.get("pattern_notes", "")
            
            # Create lookup entries for all identifiers and common names
            for identifier in mapping.identifiers + mapping.common_names:
                if identifier:
                    mappings[identifier.lower().strip()] = mapping
        
        return mappings
        
    except Exception as exc:
        log.error("Failed to extract compound mappings: %s", exc)
        return {}

def _extract_json(text: str) -> str:
    """Extract JSON content from raw LLM response text."""
    # Remove common markdown code block markers
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    
    if text.endswith('```'):
        text = text[:-3]
    
    # Find JSON structure
    text = text.strip()
    
    # Look for JSON object or array
    json_start = -1
    json_end = -1
    
    for i, char in enumerate(text):
        if char in '[{' and json_start == -1:
            json_start = i
            break
    
    if json_start >= 0:
        # Find the matching closing bracket
        bracket_stack = []
        in_string = False
        escape_next = False
        
        for i in range(json_start, len(text)):
            char = text[i]
            
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
                bracket_stack.append(char)
            elif char in ']}':
                if bracket_stack:
                    opening = bracket_stack.pop()
                    if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                        if not bracket_stack:  # Found complete JSON
                            json_end = i + 1
                            break
        
        if json_end > json_start:
            return text[json_start:json_end]
    
    # If no JSON found, return the original text
    return text

def _resolve_missing_compounds_with_gemini(
    model,
    known_compounds: Dict[str, str],
    missing_compounds: List[str],
    figure_images: Dict[str, str] = None,
    primary_location_text: str = None,
    debug_dir: str | Path | None = None,
) -> Dict[str, str]:
    """Use Gemini to resolve missing compound names based on patterns."""
    
    prompt = """You are an expert chemist analyzing compound naming patterns in a chemistry paper.

KNOWN COMPOUNDS WITH IUPAC NAMES:
"""
    
    # Add known compounds
    for cid, name in sorted(known_compounds.items()):
        prompt += f"- Compound {cid}: {name}\n"
    
    prompt += f"""

MISSING COMPOUNDS (need IUPAC names):
{', '.join(sorted(missing_compounds))}

TASK:
1. Analyze the numbering/lettering pattern used in this paper
2. Look for relationships between compounds (e.g., 3 → 3a, 3b as enantiomers)
3. Determine the IUPAC names for the missing compounds

IMPORTANT PATTERNS TO CONSIDER:
- If compound "X" has a known structure and "Xa", "Xb" are missing, they might be stereoisomers
- Common patterns: 'a' = (S)-enantiomer, 'b' = (R)-enantiomer (but verify from context)
- Some papers use 'a/b' for different stereogenic centers or regioisomers
- Look at the scheme images AND the text to understand relationships

For each missing compound, provide the most likely IUPAC name based on:
- The pattern analysis from text and schemes
- Standard chemical nomenclature rules
- The relationship to known compounds

Return ONLY compounds where you have high confidence in the IUPAC name.
If unsure, return null for that compound.

Return as JSON:
{{
  "resolved_compounds": {{
    "compound_id": "IUPAC name or null"
  }}
}}
"""

    # Add primary location text if available
    if primary_location_text:
        prompt += f"""

PRIMARY SUBSTRATE SCOPE TEXT (from scheme/table):
{primary_location_text[:10000]}  # Limit to prevent token overflow
"""
    
    # Add figure images if available
    content_parts = [prompt]
    if figure_images:
        content_parts.append("\n\nANALYZE THE FOLLOWING SCHEME IMAGES TO UNDERSTAND THE COMPOUND RELATIONSHIPS:")
        import PIL.Image
        import io
        import base64
        
        for fig_ref, fig_base64 in figure_images.items():
            if "scheme" in fig_ref.lower():
                try:
                    img_bytes = base64.b64decode(fig_base64)
                    image = PIL.Image.open(io.BytesIO(img_bytes))
                    content_parts.append(f"\n[{fig_ref}]")
                    content_parts.append(image)
                except Exception as e:
                    log.warning("Failed to add scheme image %s: %s", fig_ref, e)
    
    try:
        # Use multimodal if we have images
        if len(content_parts) > 1:
            log.info("Using multimodal API with scheme images for compound resolution")
            response = model.generate_content(content_parts)
            raw_text = _extract_text(response).strip()
        else:
            # Text-only
            raw_text = generate_json_with_retry(
                model,
                prompt,
                debug_dir=debug_dir,
                tag="resolve_compounds",
                raw_response=True
            )
        
        # Parse response
        data = json.loads(_extract_json(raw_text))
        resolved = data.get("resolved_compounds", {})
        
        # Filter to only return non-null values
        result = {}
        for cid, name in resolved.items():
            if name and cid in missing_compounds:
                result[cid] = name
                log.info("Resolved compound %s: %s", cid, name[:60] + "..." if len(name) > 60 else name)
        
        return result
        
    except Exception as exc:
        log.error("Failed to resolve compounds: %s", exc)
        return {}

def _extract_compound_mappings_with_figures(
    text: str,
    model,
    compound_ids: List[str],
    figure_images: Dict[str, str],
    pdf_paths: List[Path],
    debug_dir: str | Path | None = None,
    tag_suffix: str = "",
) -> Dict[str, CompoundMapping]:
    """Extract compound mappings using multimodal approach with figures."""
    # Enhanced prompt for figure-based extraction
    prompt = """You are an expert chemist analyzing chemical figures and manuscript text to identify compound IUPAC names.

TASK: Find the IUPAC names for these specific compound identifiers: """ + ", ".join(sorted(compound_ids)) + """

APPROACH (in order of preference):
1. First, look for explicitly written IUPAC names in text or captions
2. If not found, look for common/trivial names that you can convert to IUPAC
3. As last resort, carefully analyze chemical structures in figures to derive IUPAC names

CRITICAL ACCURACY REQUIREMENTS:
When deriving IUPAC names from structures:
- Count ALL atoms and bonds carefully - do not miss any substituents
- Verify the COMPLETE structure matches your IUPAC name
- For cyclopropanes: use "cyclopropane-1-carboxylate" NOT "cyclopropanecarboxylate"
- Include stereochemistry only if clearly shown (trans-, cis-, R/S)
- Double-check ring sizes, substituent positions, and functional groups
- If a structure is unclear or ambiguous, return null rather than guess

VALIDATION CHECKLIST before providing an IUPAC name:
□ Have I accounted for EVERY atom in the structure?
□ Have I identified ALL functional groups correctly?
□ Is the parent chain/ring correctly identified?
□ Are substituent positions numbered correctly?
□ Is the name formatted with proper punctuation (hyphens, commas)?
□ Would this IUPAC name regenerate EXACTLY the structure shown?

Common mistakes to avoid:
- Missing substituents (e.g., forgetting a methoxy group)
- Wrong ring size (e.g., calling a benzene ring a cyclohexane)
- Incorrect substituent positions
- Using "benzyl" vs "phenyl" incorrectly
- Missing or incorrect stereochemistry

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "compound identifier", 
      "iupac_name": "valid IUPAC systematic name or null if uncertain",
      "common_names": ["common names found in text"],
      "compound_type": "substrate/product/reagent",
      "source_location": "where found/how determined"
    }
  ]
}

TEXT FROM MANUSCRIPT:
""" + text
    
    # Prepare multimodal content
    content_parts = [prompt]
    
    # Add figure images
    if figure_images:
        import PIL.Image
        import io
        import base64
        
        for fig_ref, fig_base64 in figure_images.items():
            try:
                img_bytes = base64.b64decode(fig_base64)
                image = PIL.Image.open(io.BytesIO(img_bytes))
                content_parts.append(f"\n[Figure: {fig_ref}]")
                content_parts.append(image)
                log.info("Added figure %s to multimodal compound mapping", fig_ref)
            except Exception as e:
                log.warning("Failed to add figure %s: %s", fig_ref, e)
    
    tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
    
    try:
        # Log multimodal call
        log.info("=== GEMINI MULTIMODAL API CALL: COMPOUND_MAPPING_WITH_FIGURES ===")
        log.info("Text prompt length: %d characters", len(prompt))
        log.info("Number of images: %d", len(content_parts) - 1)
        log.info("Compounds to find: %s", ", ".join(sorted(compound_ids)))
        
        # Save debug info
        if debug_dir:
            debug_path = Path(debug_dir)
            prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
            with open(prompt_file, 'w') as f:
                f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Text length: {len(prompt)} characters\n")
                f.write(f"Images included: {len(content_parts) - 1}\n")
                for fig_ref in figure_images.keys():
                    f.write(f"  - {fig_ref}\n")
                f.write("="*80 + "\n\n")
                f.write(prompt)
            log.info("Full prompt saved to: %s", prompt_file)
        
        # Make multimodal API call
        response = model.generate_content(content_parts)
        raw_text = _extract_text(response).strip()
        
        # Log response
        log.info("Gemini multimodal response length: %d characters", len(raw_text))
        
        if debug_dir:
            response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
            with open(response_file, 'w') as f:
                f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(raw_text)} characters\n")
                f.write("="*80 + "\n\n")
                f.write(raw_text)
            log.info("Full response saved to: %s", response_file)
        
        # Parse JSON
        import json
        data = json.loads(raw_text.strip('```json').strip('```').strip())
        
        mappings = {}
        compound_mappings_data = data.get("compound_mappings") or []
        for item in compound_mappings_data:
            identifiers = item.get("identifiers") or []
            if not identifiers and item.get("identifier"):
                identifiers = [item.get("identifier")]
            
            mapping = CompoundMapping(
                identifiers=identifiers,
                iupac_name=item.get("iupac_name", ""),
                common_names=item.get("common_names") or [],
                compound_type=item.get("compound_type", "unknown"),
                source_location=item.get("source_location")
            )
            
            for identifier in mapping.identifiers + mapping.common_names:
                if identifier:
                    mappings[identifier.lower().strip()] = mapping
        
        return mappings
        
    except Exception as exc:
        log.error("Failed to extract compound mappings with figures: %s", exc)
        return {}

def _extract_text_for_compound_mapping(
    pdf_paths: List[Path],
    iupac_sections: List[dict],
    text_fallback: str,
) -> str:
    """Extract text from identified IUPAC sections for compound mapping."""
    extraction_text = ""
    
    if iupac_sections and pdf_paths:
        log.info("Extracting text from %d identified IUPAC sections", len(iupac_sections))
        
        # Use page-based extraction for each section
        for section in iupac_sections:
            section_title = section.get('section', '')
            page_range = section.get('page_range') or section.get('page', '')
            
            if page_range:
                log.info("Extracting section '%s' from page range %s", section_title, page_range)
                
                # Extract multiple pages starting from the given page
                pages_to_extract = []
                
                if '-' in str(page_range):
                    # Handle ranges like "S22-S45" 
                    parts = page_range.split('-')
                    start_page = parts[0].strip()
                    end_page = parts[1].strip() if len(parts) > 1 else None
                    
                    # Extract all pages in the range
                    if start_page.startswith('S') and end_page and end_page.startswith('S'):
                        try:
                            start_num = int(start_page[1:])
                            end_num = int(end_page[1:])
                            for i in range(start_num, min(end_num + 1, start_num + 15)):  # Max 15 pages
                                pages_to_extract.append(f"S{i}")
                        except:
                            pages_to_extract.append(start_page)
                    else:
                        pages_to_extract.append(start_page)
                else:
                    # Single page - extract it plus next 10 pages
                    start_page = str(page_range).strip()
                    
                    # Ensure S prefix for SI pages
                    if not start_page.startswith('S') and start_page.isdigit():
                        start_page = 'S' + start_page
                    
                    pages_to_extract.append(start_page)
                    
                    # Add next 10 pages
                    try:
                        if start_page.startswith('S'):
                            base_num = int(start_page[1:])
                            for i in range(1, 11):  # Extract 10 more pages
                                pages_to_extract.append(f"S{base_num + i}")
                        else:
                            base_num = int(start_page)
                            for i in range(1, 11):
                                pages_to_extract.append(str(base_num + i))
                    except:
                        pass
                
                # Extract the pages
                page_text = _extract_text_from_pages(pdf_paths, pages_to_extract, max_pages=15)
                if page_text:
                    extraction_text += f"\n\n=== Section: '{section_title}' starting from page {page_range} ===\n{page_text}"
            else:
                # Try title-based extraction as fallback
                section_text = _extract_sections_by_title(pdf_paths, [section_title], max_chars_per_section=10000)
                if section_text:
                    extraction_text += section_text
        
        if not extraction_text:
            log.warning("No text extracted from IUPAC sections, falling back to limited text")
            extraction_text = text_fallback[:30_000]
    else:
        # Fallback to limited text
        extraction_text = text_fallback[:30_000]
    
    return extraction_text

def extract_compound_mappings(
    text: str,
    model,
    *,
    pdf_paths: List[Path] = None,
    iupac_sections: List[dict] = None,
    compound_ids: List[str] = None,
    primary_locations: List[dict] = None,
    debug_dir: str | Path | None = None,
) -> Dict[str, CompoundMapping]:
    """Extract compound ID to IUPAC name mappings from identified sections.
    
    Uses an adaptive strategy:
    1. First attempts extraction from identified IUPAC sections
    2. Checks for missing compounds
    3. Expands search to additional sections if compounds are missing
    """
    # Step 1: Extract text from initially identified sections
    extraction_text = _extract_text_for_compound_mapping(pdf_paths, iupac_sections, text)
    
    # Step 2: First extraction attempt
    mappings = _extract_compound_mappings_from_text(
        extraction_text, model, compound_ids, debug_dir, tag_suffix="initial"
    )
    log.info("Initial extraction found %d compound mappings", len(mappings))
    
    # Step 3: Check for missing compounds
    missing_compounds = []
    if compound_ids:
        for cid in compound_ids:
            mapping = mappings.get(cid.lower().strip())
            if not mapping or not mapping.iupac_name:
                missing_compounds.append(cid)
    
    # Step 4: Adaptive expansion if compounds are missing
    if missing_compounds and pdf_paths:
        log.info("Found %d compounds without IUPAC names: %s", 
                 len(missing_compounds), sorted(missing_compounds))
        log.info("Expanding search to additional sections...")
        
        # Define additional sections that might contain compound definitions
        additional_sections = [
            "Engineering strategy",
            "Screening for benzyl acrylate cyclopropanation",
            "Evolution campaign", 
            "General procedure",
            "Experimental procedures",
            "Materials and methods",
            "Substrate synthesis"
        ]
        
        # Extract text from additional sections
        additional_text = _extract_sections_by_title(
            pdf_paths, additional_sections, max_chars_per_section=5000
        )
        
        if additional_text:
            log.info("Extracted %d chars from additional sections", len(additional_text))
            
            # Second extraction attempt with expanded text
            expanded_mappings = _extract_compound_mappings_from_text(
                additional_text, model, missing_compounds, debug_dir, tag_suffix="expanded"
            )
            
            # Merge new mappings
            new_found = 0
            for key, mapping in expanded_mappings.items():
                if key not in mappings or not mappings[key].iupac_name:
                    if mapping.iupac_name:  # Only add if we found an IUPAC name
                        mappings[key] = mapping
                        new_found += 1
                        log.info("Found IUPAC name for '%s': %s", 
                                key, mapping.iupac_name[:50] + "..." if len(mapping.iupac_name) > 50 else mapping.iupac_name)
            
            log.info("Expanded search found %d additional compound mappings", new_found)
        else:
            log.warning("No additional text found in expanded sections")
        
        # Step 5: Check again for still missing compounds
        still_missing = []
        for cid in missing_compounds:
            mapping = mappings.get(cid.lower().strip())
            if not mapping or not mapping.iupac_name:
                still_missing.append(cid)
        
        # Step 5.5: Use Gemini to resolve compound relationships and missing names
        if still_missing and len(mappings) > 0:
            log.info("Attempting to resolve %d missing compounds using pattern analysis...", len(still_missing))
            
            # Prepare data about known compounds and missing ones
            known_compounds = {}
            for key, mapping in mappings.items():
                if mapping.iupac_name:
                    # Get the primary identifier
                    primary_id = mapping.identifiers[0] if mapping.identifiers else key
                    known_compounds[primary_id] = mapping.iupac_name
            
            # Extract primary location text if available
            primary_location_text = None
            if primary_locations and pdf_paths:
                # Get text from the first primary location (usually the main scheme)
                for loc in primary_locations[:1]:  # Just the first one
                    loc_str = loc.get('location', '')
                    if loc_str:
                        primary_text = _extract_text_around_reference(pdf_paths, loc_str, context_chars=10000)
                        if primary_text:
                            primary_location_text = primary_text
                            log.info("Extracted %d chars from primary location %s for pattern analysis", 
                                    len(primary_text), loc_str)
                            break
            
            # Ask Gemini to analyze patterns and resolve missing compounds
            resolved_mappings = _resolve_missing_compounds_with_gemini(
                model, known_compounds, still_missing, 
                figure_images=getattr(extract_compound_mappings, '_figure_images_cache', {}),
                primary_location_text=primary_location_text,
                debug_dir=debug_dir
            )
            
            # Merge resolved mappings
            resolved_count = 0
            for cid, iupac_name in resolved_mappings.items():
                key = cid.lower().strip()
                if key in mappings:
                    if not mappings[key].iupac_name and iupac_name:
                        mappings[key].iupac_name = iupac_name
                        resolved_count += 1
                else:
                    # Create new mapping
                    new_mapping = CompoundMapping(
                        identifiers=[cid],
                        iupac_name=iupac_name,
                        common_names=[],
                        compound_type="product",
                        source_location="Resolved from pattern analysis"
                    )
                    mappings[key] = new_mapping
                    resolved_count += 1
            
            if resolved_count > 0:
                log.info("Resolved %d compounds using pattern analysis", resolved_count)
        
        # Step 6: Final fallback - use figures and full manuscript if compounds are still missing
        # COMMENTED OUT: Figure-based IUPAC extraction is unreliable
        # Generating IUPAC names from visual structures leads to errors
        # Only use text-based extraction for reliability
        
        # if still_missing:
        #     log.info("Still missing IUPAC names for %d compounds: %s", 
        #              len(still_missing), sorted(still_missing))
        #     log.info("Attempting final extraction using figures and full manuscript...")
        #     
        #     # Extract figure images if available
        #     figure_images = {}
        #     if hasattr(extract_compound_mappings, '_figure_images_cache'):
        #         figure_images = extract_compound_mappings._figure_images_cache
        #     
        #     # Use multimodal approach with figures and manuscript text
        #     final_mappings = _extract_compound_mappings_with_figures(
        #         text[:50_000], model, still_missing, figure_images, 
        #         pdf_paths, debug_dir, tag_suffix="figures"
        #     )
        #     
        #     # Merge final mappings
        #     final_found = 0
        #     for key, mapping in final_mappings.items():
        #         if key not in mappings or not mappings[key].iupac_name:
        #             if mapping.iupac_name:
        #                 mappings[key] = mapping
        #                 final_found += 1
        #                 log.info("Found IUPAC name for '%s' using figures: %s", 
        #                         key, mapping.iupac_name[:50] + "..." if len(mapping.iupac_name) > 50 else mapping.iupac_name)
        #     
        #     log.info("Figure-based search found %d additional compound mappings", final_found)
        
        if still_missing:
            log.info("Still missing IUPAC names for %d compounds: %s", 
                     len(still_missing), sorted(still_missing))
            log.info("Note: Figure-based IUPAC extraction is disabled for reliability")
    
    log.info("Total compound mappings extracted: %d", len(mappings))
    return mappings

def extract_all_substrate_scope_data(
    text: str,
    model,
    locations: List[dict],
    *,
    pdf_paths: List[Path] = None,
    figure_images: Dict[str, str] = None,
    debug_dir: str | Path | None = None,
) -> List[dict]:
    """Extract all substrate scope data at once from all primary sources."""
    extraction_hints = ""
    all_refs = []
    
    if locations:
        # Include ALL locations, not just primary
        location_strs = []
        for loc in locations[:3]:  # Up to 3 locations
            loc_str = loc.get('location', '')
            location_strs.append(loc_str)
            all_refs.append(loc_str)
        
        extraction_hints = f"\nSubstrate scope locations: {', '.join(location_strs)}"
        
        # Collect all enzyme variants
        all_variants = []
        for loc in locations:
            variants = loc.get('enzyme_variants_tested', [])
            all_variants.extend(variants)
        
        if all_variants:
            unique_variants = list(set(all_variants))
            extraction_hints += f"\nEnzyme variants: {', '.join(unique_variants)}"
    
    # Extract text from ALL identified locations
    extraction_texts = []
    
    for ref in all_refs:
        if ref and pdf_paths:
            ref_text = _extract_text_around_reference(pdf_paths, ref, context_chars=5000)
            if ref_text:
                # Add figure image notation if available
                if figure_images and ref in figure_images:
                    ref_text = f"[FIGURE IMAGE EXTRACTED: {ref}]\n\n{ref_text}"
                extraction_texts.append(f"\n=== Data from {ref} ===\n{ref_text}")
    
    if not extraction_texts:
        extraction_texts = [text[:50_000]]
    
    extraction_text = "\n\n".join(extraction_texts)
    
    prompt = _SUBSTRATE_SCOPE_PROMPT.format(extraction_hints=extraction_hints)
    prompt += "\n\nTEXT:\n" + extraction_text
    
    # Prepare multimodal content with images
    content_parts = [prompt]
    
    # Add figure images to the prompt
    if figure_images:
        import PIL.Image
        import io
        import base64
        
        for fig_ref, fig_base64 in figure_images.items():
            try:
                # Convert base64 to PIL Image
                img_bytes = base64.b64decode(fig_base64)
                image = PIL.Image.open(io.BytesIO(img_bytes))
                content_parts.append(f"\n[Figure: {fig_ref}]")
                content_parts.append(image)
                log.info("Added figure %s to multimodal prompt", fig_ref)
            except Exception as e:
                log.warning("Failed to add figure %s: %s", fig_ref, e)
    
    try:
        # Use multimodal content if we have images
        if len(content_parts) > 1:
            # Log multimodal API call
            log.info("=== GEMINI MULTIMODAL API CALL: SUBSTRATE_SCOPE_WITH_FIGURES ===")
            log.info("Text prompt length: %d characters", len(prompt))
            log.info("Number of images: %d", len(content_parts) - 1)
            log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
            
            # Save prompt and image info to debug directory
            if debug_dir:
                debug_path = Path(debug_dir)
                debug_path.mkdir(parents=True, exist_ok=True)
                prompt_file = debug_path / f"substrate_scope_multimodal_prompt_{int(time.time())}.txt"
                
                # Build prompt info including image references
                prompt_info = f"=== PROMPT FOR SUBSTRATE_SCOPE_MULTIMODAL ===\n"
                prompt_info += f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                prompt_info += f"Text length: {len(prompt)} characters\n"
                prompt_info += f"Images included: {len(content_parts) - 1}\n"
                for fig_ref in figure_images.keys():
                    prompt_info += f"  - {fig_ref}\n"
                prompt_info += "="*80 + "\n\n"
                prompt_info += prompt
                
                _dump(prompt_info, prompt_file)
                log.info("Full prompt saved to: %s", prompt_file)
            
            log.info("Calling Gemini Multimodal API...")
            response = model.generate_content(content_parts)
            raw_text = _extract_text(response).strip()
            
            # Log and save response
            log.info("Gemini multimodal response length: %d characters", len(raw_text))
            log.info("First 500 chars of response:\n%s\n...(truncated)", raw_text[:500])
            
            if debug_dir:
                debug_path = Path(debug_dir)
                response_file = debug_path / f"substrate_scope_multimodal_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR SUBSTRATE_SCOPE_MULTIMODAL ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw_text)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw_text)
                log.info("Full response saved to: %s", response_file)
            
            # Parse JSON from response
            import json
            data = json.loads(raw_text.strip('```json').strip('```').strip())
        else:
            data = generate_json_with_retry(
                model,
                prompt,
                debug_dir=debug_dir,
                tag="substrate_scope",
            )
        
        scope_data = data.get("substrate_scope_data", [])
        log.info("Extracted %d substrate scope entries", len(scope_data))
        return scope_data
        
    except Exception as exc:
        log.error("Failed to extract substrate scope data: %s", exc)
        return []

def _extract_single_reaction(
    text: str,
    model,
    enzyme_id: str,
    substrate_name: str,
    data_location: str,
    context_pairs: List[Tuple[str, str, str]] = None,
    *,
    pdf_paths: List[Path] = None,
    debug_dir: str | Path | None = None,
) -> Optional[dict]:
    """Extract data for a single enzyme-substrate pair."""
    # Build context
    context_info = ""
    if context_pairs:
        context_info = "\nCONTEXT - NEIGHBORING ENTRIES:\n"
        for ctx_enzyme, ctx_substrate, _ in context_pairs[:4]:
            if ctx_enzyme == enzyme_id and ctx_substrate != substrate_name:
                context_info += f"- {ctx_substrate} (same enzyme, different substrate)\n"
    
    # Extract focused text for this specific reaction
    if data_location and pdf_paths:
        # Extract text around the data location and reaction conditions
        extraction_text = _extract_text_around_reference(pdf_paths, data_location, context_chars=2000)
        
        # Also extract reaction conditions section if available
        conditions_sections = ["General procedure", "Reaction conditions", "Standard conditions"]
        conditions_text = _extract_sections_by_title(pdf_paths, conditions_sections, max_chars_per_section=2000)
        
        if conditions_text:
            extraction_text += "\n\n=== REACTION CONDITIONS ===\n" + conditions_text
    else:
        extraction_text = text[:20_000]
    
    prompt = _SINGLE_REACTION_PROMPT.format(
        enzyme_id=enzyme_id,
        substrate_name=substrate_name,
        data_location=data_location,
        context_info=context_info
    )
    prompt += "\n\nTEXT:\n" + extraction_text
    
    try:
        return generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag=f"reaction_{enzyme_id[:10]}_{substrate_name[:10]}",
        )
    except Exception as exc:
        log.error("Failed to extract reaction %s-%s: %s", enzyme_id, substrate_name, exc)
        return None

def _parse_scope_entries(data: List[dict], compound_mappings: Dict[str, CompoundMapping]) -> List[ScopeEntry]:
    """Convert raw JSON to ScopeEntry objects with IUPAC enhancement."""
    entries: List[ScopeEntry] = []
    
    for item in data:
        try:
            # Parse substrate IDs
            substrates = []
            substrate_ids = item.get("substrate_ids")
            
            # Handle null substrate_ids
            if substrate_ids is None:
                # Leave substrates empty if substrate_ids is explicitly null
                pass
            else:
                # Also handle old format
                if not substrate_ids and item.get("substrates"):
                    substrates_data = item.get("substrates") or []
                    for s in substrates_data:
                        if isinstance(s, dict):
                            substrate_ids.append(s.get("identifier") or s.get("name", ""))
                        else:
                            substrate_ids.append(str(s))
                
                for sid in substrate_ids:
                    # Look up IUPAC name
                    iupac_name = None
                    mapping = compound_mappings.get(str(sid).lower())
                    if mapping:
                        iupac_name = mapping.iupac_name
                    
                    substrates.append(SubstrateProduct(name=str(sid), iupac_name=iupac_name))
            
            # Parse product IDs
            products = []
            product_ids = item.get("product_ids") or []
            # Also handle old format
            if not product_ids and item.get("products"):
                products_data = item.get("products") or []
                for p in products_data:
                    if isinstance(p, dict):
                        product_ids.append(p.get("identifier") or p.get("name", ""))
                    else:
                        product_ids.append(str(p))
            
            for pid in product_ids:
                # Look up IUPAC name
                iupac_name = None
                mapping = compound_mappings.get(str(pid).lower())
                if mapping:
                    iupac_name = mapping.iupac_name
                
                products.append(SubstrateProduct(name=str(pid), iupac_name=iupac_name))
            
            # Parse cofactors
            cofactors = []
            cofactors_data = item.get("cofactors") or []
            for c in cofactors_data:
                if isinstance(c, dict):
                    cofactors.append(Cofactor(
                        name=c.get("name", ""),
                        iupac_name=c.get("iupac_name"),
                        role=c.get("role")
                    ))
            
            # Parse conditions
            cond_data = item.get("reaction_conditions", {})
            conditions = ReactionConditions(
                temperature=cond_data.get("temperature"),
                ph=cond_data.get("ph"),
                substrate_concentration=cond_data.get("substrate_concentration"),
                buffer=cond_data.get("buffer"),
                other_conditions=cond_data.get("other_conditions")
            )
            
            # Parse numeric values
            def parse_numeric(val):
                if not val or val in ["", "n.d.", "N/A", None]:
                    return None
                try:
                    # Extract numeric part
                    match = re.search(r'(\d+\.?\d*)', str(val))
                    return float(match.group(1)) if match else None
                except:
                    return None
            
            # Parse ee - handle both percentage and ratio formats
            ee_value = item.get("ee_percent")
            if ee_value is None and item.get("ee"):
                # Try to extract from ratio format like "80:20 er"
                ee_str = str(item.get("ee"))
                match = re.search(r'(\d+):(\d+)', ee_str)
                if match:
                    major = float(match.group(1))
                    minor = float(match.group(2))
                    # Convert ratio to ee%
                    ee_value = abs(major - minor)
            
            entry = ScopeEntry(
                enzyme_id=item.get("enzyme_id", ""),
                substrates=substrates,
                products=products,
                cofactors=cofactors,
                yield_percent=parse_numeric(item.get("yield_percent")),
                ttn=parse_numeric(item.get("ttn")),
                ee=parse_numeric(ee_value),
                conditions=conditions,
                data_location=item.get("data_location", ""),
                data_source_type={"all": "text/figure"},
                notes=item.get("notes", "")
            )
            
            entries.append(entry)
            
        except Exception as exc:  # pragma: no cover
            log.debug("Skipping malformed scope entry %s: %s", item, exc)
    
    return entries

# ---- 6.3  Public API -------------------------------------------------------

def get_substrate_scope(
    caption_text: str,
    full_text: str,
    model,
    *,
    pdf_paths: Optional[List[Path]] = None,
    debug_dir: str | Path | None = None,
) -> List[ScopeEntry]:
    """
    High-level wrapper used by the pipeline.

    1. Use captions to identify substrate scope locations
    2. Identify sections containing IUPAC names
    3. Extract compound mappings from identified sections
    4. Identify enzyme-substrate pairs
    5. Extract individual reactions with context
    """
    # Step 1: Find locations using captions
    locations = identify_scope_locations(caption_text, model, debug_dir=debug_dir)
    if locations:
        location_summary = []
        for loc in locations[:3]:
            location_summary.append(
                f"{loc.get('location', 'Unknown')} ({loc.get('type', 'unknown')}, "
                f"confidence: {loc.get('confidence', 0)})"
            )
        log.info("Identified %d substrate scope locations: %s", 
                 len(locations), ", ".join(location_summary))
    else:
        log.warning("No substrate scope locations identified")
        return []
    
    # Step 2: Extract all substrate scope data first
    # (This gets us the compound IDs we need to map)
    time.sleep(2)  # Rate limiting
    log.info("Extracting all substrate scope data from all identified sources...")
    
    # Extract images for all figure and scheme locations
    figure_images = {}
    for loc in locations:
        location_str = loc.get('location', '')
        location_type = loc.get('type', 'unknown')
        
        # Extract if it's a figure, scheme, or contains those keywords
        should_extract = False
        if pdf_paths:
            if location_type in ['figure', 'scheme']:
                should_extract = True
            elif any(keyword in location_str.lower() for keyword in ['figure', 'fig', 'scheme']):
                should_extract = True
        
        if should_extract:
            figure_ref = location_str
            confidence = loc.get('confidence', 0)
            log.info("Extracting image for %s (confidence: %d%%, type: %s)", figure_ref, confidence, location_type)
            
            # Use appropriate extraction function based on type
            if 'scheme' in location_str.lower() or location_type == 'scheme':
                figure_image = extract_scheme_image(pdf_paths, figure_ref)
            else:
                figure_image = extract_figure_image(pdf_paths, figure_ref)
                
            if figure_image:
                log.info("Successfully extracted %s image for %s (%d bytes)", 
                         location_type, figure_ref, len(figure_image))
                figure_images[figure_ref] = figure_image
                
                # Save figure image if debug_dir is enabled
                if debug_dir:
                    import base64
                    debug_path = Path(debug_dir)
                    image_path = debug_path / f"{location_type}_image_{figure_ref.replace(' ', '_')}.png"
                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(figure_image))
                    log.info("Saved %s image to %s", location_type, image_path)
            else:
                log.warning("Failed to extract %s image for %s", location_type, figure_ref)
    
    # Extract all substrate scope data in one call
    raw_entries = extract_all_substrate_scope_data(
        full_text, model, locations,
        pdf_paths=pdf_paths,
        figure_images=figure_images,
        debug_dir=debug_dir
    )
    
    if not raw_entries:
        log.warning("No substrate scope data found")
        return []
    
    # Step 3: Now identify IUPAC sections using SI TOC pages
    log.info("Identifying sections containing IUPAC names from SI table of contents...")
    iupac_sections = identify_iupac_sections(caption_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir)
    
    # Step 4: Extract compound mappings from identified sections
    # Now we know which compound IDs to look for from the substrate scope data
    log.info("Extracting compound ID to IUPAC mappings...")
    
    # Collect all compound IDs from substrate scope data
    all_compound_ids = set()
    for entry in raw_entries:
        substrate_ids = entry.get('substrate_ids') or []
        for sid in substrate_ids:
            all_compound_ids.add(str(sid))
        product_ids = entry.get('product_ids') or []
        for pid in product_ids:
            all_compound_ids.add(str(pid))
    
    log.info("Found %d unique compound IDs to map: %s", len(all_compound_ids), sorted(all_compound_ids))
    
    # Store figure images in the function for later use
    extract_compound_mappings._figure_images_cache = figure_images
    
    compound_mappings = extract_compound_mappings(full_text, model, 
                                                 pdf_paths=pdf_paths,
                                                 iupac_sections=iupac_sections,
                                                 compound_ids=list(all_compound_ids),
                                                 primary_locations=locations,
                                                 debug_dir=debug_dir)
    
    # Step 5: Parse all entries with compound mappings
    entries = _parse_scope_entries(raw_entries, compound_mappings)
    log.info("Successfully parsed %d substrate scope entries", len(entries))
    
    return entries

# === 7. VALIDATION & MERGE ===
"""Validation, duplicate detection, and merging with lineage data."""

def validate_scope_entries(entries: List[ScopeEntry]) -> List[str]:
    """Validate for suspicious patterns like duplicate values."""
    warnings = []
    
    # Track values
    ttn_values: Dict[float, List[str]] = {}
    yield_values: Dict[float, List[str]] = {}
    ee_values: Dict[float, List[str]] = {}
    
    for entry in entries:
        substrate_name = entry.substrates[0].name if entry.substrates else "Unknown"
        key = f"{entry.enzyme_id}-{substrate_name}"
        
        if entry.ttn is not None:
            if entry.ttn not in ttn_values:
                ttn_values[entry.ttn] = []
            ttn_values[entry.ttn].append(key)
        
        if entry.yield_percent is not None:
            if entry.yield_percent not in yield_values:
                yield_values[entry.yield_percent] = []
            yield_values[entry.yield_percent].append(key)
        
        if entry.ee is not None:
            if entry.ee not in ee_values:
                ee_values[entry.ee] = []
            ee_values[entry.ee].append(key)
    
    # Check for suspicious duplicates
    for value, items in ttn_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have TTN={value}: {', '.join(items[:3])}")
    
    for value, items in yield_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have yield={value}%: {', '.join(items[:3])}")
    
    for value, items in ee_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have ee={value}%: {', '.join(items[:3])}")
    
    if warnings:
        log.warning("Validation warnings found - possible extraction errors")
        for warning in warnings:
            log.warning("  %s", warning)
    
    return warnings

def _match_enzymes_with_gemini(
    scope_enzymes: List[str],
    lineage_enzymes: List[str],
    model,
    debug_dir: Optional[Path] = None
) -> Dict[str, str]:
    """Use Gemini to match enzyme names between substrate scope and lineage data."""
    
    prompt = """You are an expert at matching enzyme variant names that may have Unicode or formatting differences.

ENZYME NAMES FROM SUBSTRATE SCOPE DATA:
""" + "\n".join(f"- {e}" for e in sorted(set(scope_enzymes))) + """

ENZYME NAMES FROM LINEAGE DATA:
""" + "\n".join(f"- {e}" for e in sorted(set(lineage_enzymes))) + """

TASK:
Match each substrate scope enzyme name to its corresponding lineage enzyme name.
These are the SAME enzymes but may have different formatting:
- Unicode vs ASCII characters (e.g., "ʟ" vs "L", "ᴅ" vs "D")
- Different capitalization
- Minor formatting differences

IMPORTANT:
- Only match enzymes that are clearly the same variant
- Look for matching generation numbers (G0, G1, G2, etc.)
- Consider the pattern: [L/D]-ApPgb-αEsA-G[number]
- If no clear match exists, return null for that enzyme

Return as JSON:
{{
  "enzyme_matches": {{
    "substrate_scope_enzyme_name": "matching_lineage_enzyme_name_or_null"
  }}
}}
"""

    try:
        response = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="enzyme_matching"
        )
        
        matches = response.get("enzyme_matches", {})
        log.info("Gemini matched %d enzyme names", len([v for v in matches.values() if v]))
        return matches
        
    except Exception as exc:
        log.error("Failed to match enzymes with Gemini: %s", exc)
        return {}

def merge_with_lineage(
    entries: List[ScopeEntry],
    lineage_csv: Optional[Path],
    model=None
) -> List[ScopeEntry]:
    """Merge substrate scope entries with enzyme lineage data using Gemini for matching."""
    if not lineage_csv or not lineage_csv.exists():
        return entries
    
    try:
        import pandas as pd
        lineage_df = pd.read_csv(lineage_csv)
        log.info("Loading lineage data from %s (%d enzymes)", lineage_csv, len(lineage_df))
        
        # Get unique enzyme names from both sources
        scope_enzymes = list(set(entry.enzyme_id for entry in entries if entry.enzyme_id))
        lineage_enzymes = list(lineage_df['enzyme_id'].dropna().unique())
        
        log.info("Found %d unique enzymes in substrate scope data", len(scope_enzymes))
        log.info("Found %d unique enzymes in lineage data", len(lineage_enzymes))
        
        # Use Gemini to match enzyme names if model is provided
        if model and scope_enzymes and lineage_enzymes:
            log.info("Using Gemini to match enzyme names between datasets...")
            enzyme_matches = _match_enzymes_with_gemini(
                scope_enzymes, 
                lineage_enzymes, 
                model,
                debug_dir=Path("examples/amino_esters_test/substrate_scope_debug_v4") if Path("examples/amino_esters_test/substrate_scope_debug_v4").exists() else None
            )
        else:
            # Fallback to simple case-insensitive matching
            log.info("Using simple case-insensitive matching (no model provided)")
            enzyme_matches = {}
            for scope_enzyme in scope_enzymes:
                for lineage_enzyme in lineage_enzymes:
                    if scope_enzyme.lower() == lineage_enzyme.lower():
                        enzyme_matches[scope_enzyme] = lineage_enzyme
                        break
        
        # Create lookup map with matched names
        lineage_map = {}
        for _, row in lineage_df.iterrows():
            enzyme_id = str(row.get('enzyme_id', ''))
            lineage_map[enzyme_id] = {
                'parent_id': row.get('parent_enzyme_id', ''),  # Note: might be 'parent_enzyme_id' not 'parent_id'
                'mutations': row.get('mutations', ''),
                'generation': row.get('generation'),
                'aa_seq': row.get('protein_sequence', '') or row.get('aa_seq', ''),  # Try both column names
                'dna_seq': row.get('dna_seq', ''),
                'confidence': row.get('seq_confidence', '') or row.get('confidence', '')
            }
        
        # Merge using matched names
        merged_count = 0
        for entry in entries:
            if entry.enzyme_id in enzyme_matches:
                matched_name = enzyme_matches[entry.enzyme_id]
                if matched_name and matched_name in lineage_map:
                    data = lineage_map[matched_name]
                    entry.parent_id = data['parent_id']
                    entry.mutations = data['mutations']
                    entry.generation = data['generation']
                    entry.aa_seq = data['aa_seq']
                    entry.dna_seq = data['dna_seq']
                    entry.confidence = data['confidence']
                    merged_count += 1
                    log.debug("Merged %s -> %s", entry.enzyme_id, matched_name)
        
        log.info("Merged lineage data for %d/%d entries", merged_count, len(entries))
        
    except Exception as exc:
        log.error("Failed to merge with lineage: %s", exc)
    
    return entries

# === 8. PIPELINE ORCHESTRATOR ===
"""High-level function that ties everything together."""

import pandas as pd

def _entries_to_dataframe(entries: List[ScopeEntry]) -> pd.DataFrame:
    """Convert ScopeEntry objects to tidy DataFrame."""
    rows = []
    
    for entry in entries:
        row = {
            'enzyme_id': entry.enzyme_id,
            'parent_enzyme_id': entry.parent_id or '',
            'mutations': entry.mutations or '',
            'generation': entry.generation if entry.generation is not None else '',
            'protein_sequence': entry.aa_seq or '',
            'nucleotide_sequence': entry.dna_seq or '',
            'sequence_confidence': str(entry.confidence) if entry.confidence is not None else '',
            'flag': '',
            
            'substrate_list': '; '.join(s.name for s in entry.substrates if s.name),
            'substrate_iupac_list': '; '.join(s.iupac_name or '' for s in entry.substrates),
            'product_list': '; '.join(p.name for p in entry.products if p.name),
            'product_iupac_list': '; '.join(p.iupac_name or '' for p in entry.products),
            
            'cofactor_list': '; '.join(c.name for c in entry.cofactors if c.name),
            'cofactor_iupac_list': '; '.join(c.iupac_name or '' for c in entry.cofactors),
            'cofactor_roles': '; '.join(c.role or '' for c in entry.cofactors),
            
            'yield': str(entry.yield_percent) if entry.yield_percent is not None else '',
            'ttn': str(entry.ttn) if entry.ttn is not None else '',
            'ee': str(entry.ee) if entry.ee is not None else '',
            
            'reaction_temperature': entry.conditions.temperature or '',
            'reaction_ph': entry.conditions.ph or '',
            'reaction_substrate_concentration': entry.conditions.substrate_concentration or '',
            'reaction_buffer': entry.conditions.buffer or '',
            'reaction_other_conditions': entry.conditions.other_conditions or '',
            
            'data_location': entry.data_location or ''
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Define column order
    column_order = [
        'enzyme_id', 'parent_enzyme_id', 'mutations', 'generation',
        'protein_sequence', 'nucleotide_sequence', 'sequence_confidence', 'flag',
        'substrate_list', 'substrate_iupac_list', 
        'product_list', 'product_iupac_list',
        'cofactor_list', 'cofactor_iupac_list', 'cofactor_roles',
        'yield', 'ttn', 'ee',
        'reaction_temperature', 'reaction_ph', 'reaction_substrate_concentration',
        'reaction_buffer', 'reaction_other_conditions',
        'data_location'
    ]
    
    # Ensure all columns exist
    for col in column_order:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder
    df = df[column_order]
    
    return df

def run_pipeline(
    manuscript: Union[str, Path],
    si: Optional[Union[str, Path]] = None,
    output_csv: Optional[Union[str, Path]] = None,
    *,
    lineage_csv: Optional[Union[str, Path]] = None,
    debug_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Execute the end-to-end substrate scope extraction pipeline.

    Parameters
    ----------
    manuscript : str | Path
        Path to the main PDF file.
    si : str | Path | None, optional
        Path to the Supplementary Information PDF, if available.
    output_csv : str | Path | None, optional
        If provided, the substrate scope table will be written here.
    lineage_csv : str | Path | None, optional
        Path to enzyme lineage CSV for sequence merging.

    Returns
    -------
    pandas.DataFrame
        One row per substrate-enzyme combination with all data.
    """
    t0 = time.perf_counter()
    manuscript = Path(manuscript)
    si_path = Path(si) if si else None

    # 1. Prepare raw text ------------------------------------------------------
    pdf_paths = [p for p in (manuscript, si_path) if p]
    caption_text = limited_caption_concat(*pdf_paths)
    full_text = limited_concat(*pdf_paths)
    
    log.info("Loaded %d chars of captions and %d chars of full text", 
             len(caption_text), len(full_text))

    # 2. Connect to Gemini -----------------------------------------------------
    model = get_model()

    # 3. Extract substrate scope -----------------------------------------------
    entries = get_substrate_scope(caption_text, full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir)

    if not entries:
        raise RuntimeError("Pipeline aborted: failed to extract any substrate scope data")

    # 4. Merge with lineage if available ---------------------------------------
    if lineage_csv:
        entries = merge_with_lineage(entries, Path(lineage_csv), model)

    # 5. Validate entries ------------------------------------------------------
    warnings = validate_scope_entries(entries)
    if warnings:
        log.warning("Found %d validation warnings", len(warnings))

    # 6. Convert to DataFrame --------------------------------------------------
    df_final = _entries_to_dataframe(entries)

    # 7. Write CSV if requested ------------------------------------------------
    if output_csv:
        output_path = Path(output_csv)
        df_final.to_csv(output_path, index=False)
        log.info(
            "Saved substrate scope CSV -> %s (%.1f kB)",
            output_path,
            output_path.stat().st_size / 1024,
        )

    log.info(
        "Pipeline finished in %.2f s (entries: %d)",
        time.perf_counter() - t0,
        len(df_final),
    )
    return df_final

# === 9. CLI ENTRYPOINT ===
"""Simple argparse wrapper matching enzyme_lineage_extractor.py style."""

import argparse

# -- 9.1  Argument parser ----------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="substrate_scope_extractor",
        description="Extract substrate scope data from PDFs using Google Gemini",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, help="Path to main manuscript PDF")
    p.add_argument("--si", help="Path to Supplementary Information PDF")
    p.add_argument("-o", "--output", help="CSV file for extracted data")
    p.add_argument("--lineage-csv", help="Path to enzyme lineage CSV for merging")
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
        help="Write ALL intermediate artefacts (prompts, raw Gemini replies) to DIR",
    )
    return p

# -- 9.2  main() -------------------------------------------------------------

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
        lineage_csv=args.lineage_csv,
        debug_dir=args.debug_dir,
    )

if __name__ == "__main__":
    main()

# -------------------------------------------------------------------- end 9 ---
