"""reaction_info_extractor_clean.py

Single-file, maintainable CLI tool that pulls **enzyme-reaction performance data**
from chemistry PDFs using Google Gemini (text-only *and* vision) - now with
**true figure-image extraction** mirroring the enzyme-lineage workflow.

Key June 2025 additions
=======================
1. **Figure image helper** - locates the figure caption, then exports the first
   image **above** that caption using PyMuPDF (fitz). This PNG is sent to
   Gemini Vision for metric extraction.
2. **GeminiClient.generate()** now accepts an optional `image_b64` arg and
   automatically switches to a *vision* invocation when provided.
3. **extract_metrics_for_enzyme()** chooses between three tiers:

      * *Table* -> caption + following rows (text-only)
      * *Figure* -> image bytes (vision) *or* caption fallback
      * *Other* -> page-level text

   If the vision route fails (no JSON), it gracefully falls back to caption
   text so the pipeline never crashes.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from base64 import b64encode, b64decode
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF - for image extraction
import google.generativeai as genai  # type: ignore
import pandas as pd
from PyPDF2 import PdfReader
import PIL.Image
import io

###############################################################################
# 1 - CONFIG & CONSTANTS
###############################################################################

@dataclass
class Config:
    """Centralised tunables so tests can override them easily."""

    model_name: str = "gemini-1.5-pro-latest"
    location_temperature: float = 0.2
    extract_temperature: float = 0.0
    model_reaction_temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 4096
    pdf_cache_size: int = 8
    retries: int = 2

@dataclass
class CompoundMapping:
    """Mapping between compound identifiers and IUPAC names."""
    identifiers: List[str]
    iupac_name: str
    common_names: List[str] = field(default_factory=list)
    compound_type: str = "unknown"
    source_location: Optional[str] = None

###############################################################################
# 2 - LOGGING
###############################################################################

LOGGER = logging.getLogger("reaction_info_extractor")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

# --- Debug dump helper ----------------------------------------------------
def _dump(text: str | bytes, path: Path | str) -> None:
    """Write `text` / `bytes` to `path`, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(text, (bytes, bytearray)) else "w"
    with p.open(mode) as fh:
        fh.write(text)

###############################################################################
# 3 - PDF UTILITIES
###############################################################################

def extract_text_by_page(path: Optional[Path]) -> List[str]:
    if path is None:
        return []
    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("PyPDF2 failed on a page: %s", exc)
            pages.append("")
    return pages

###############################################################################
# 4 - GEMINI WRAPPER (text & vision)
###############################################################################

def get_model(cfg: Config):
    """Configure API key and return a `GenerativeModel` instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(cfg.model_name)

def generate_json_with_retry(
    model,
    prompt: str,
    schema_hint: str | None = None,
    *,
    max_retries: int = 2,
    temperature: float = 0.0,
    debug_dir: str | Path | None = None,
    tag: str = 'gemini',
    image_b64: Optional[str] = None,
):
    """Call Gemini with retries & exponential back-off, returning parsed JSON."""
    # Log prompt details
    LOGGER.info("=== GEMINI API CALL: %s ===", tag.upper())
    LOGGER.info("Prompt length: %d characters", len(prompt))
    LOGGER.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        _dump(f"=== PROMPT FOR {tag.upper()} ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\n{'='*80}\n\n{prompt}",
              prompt_file)
        LOGGER.info("Full prompt saved to: %s", prompt_file)
    
    fence_re = re.compile(r"```json|```", re.I)
    for attempt in range(1, max_retries + 1):
        try:
            LOGGER.info("Calling Gemini API (attempt %d/%d)...", attempt, max_retries)
            
            # Handle image if provided
            if image_b64:
                parts = [prompt, {"mime_type": "image/png", "data": image_b64}]
            else:
                parts = [prompt]
            
            resp = model.generate_content(
                parts,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 4096,
                }
            )
            raw = resp.text.strip()
            
            # Log response
            LOGGER.info("Gemini response length: %d characters", len(raw))
            LOGGER.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
            
            # Save full response to debug directory
            if debug_dir:
                response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
                _dump(f"=== RESPONSE FOR {tag.upper()} ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(raw)} characters\n{'='*80}\n\n{raw}",
                      response_file)
                LOGGER.info("Full response saved to: %s", response_file)

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
            LOGGER.info("Successfully parsed JSON response")
            return parsed
        except Exception as exc:
            LOGGER.warning(
                "Gemini call failed (attempt %d/%d): %s",
                attempt, max_retries, exc,
            )
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)


###############################################################################
# 5 - PROMPTS (unchanged except for brevity)
###############################################################################

PROMPT_FIND_LOCATIONS = dedent("""
You are an expert reader of protein engineering manuscripts.
Given the following article captions and section titles, identify ALL locations
(tables or figures) that contain reaction performance data (yield, TON, TTN, ee, 
activity, etc.) for enzyme variants.

IMPORTANT: Some papers have multiple enzyme lineages/campaigns with different 
performance data locations. Pay careful attention to:
- The caption text to identify which campaign/lineage the data is for
- Enzyme name prefixes (e.g., PYS vs INS) that indicate different campaigns
- Different substrate/product types mentioned in captions

Respond with a JSON array where each element contains:
- "location": the identifier (e.g. "Table S1", "Figure 3", "Table 2")
- "type": one of "table", "figure"
- "confidence": your confidence score (0-100)
- "caption": the exact caption text for this location
- "reason": brief explanation (including if this is for a specific lineage/campaign)
- "lineage_hint": any indication of which enzyme group this data is for (or null)
- "campaign_clues": specific text in the caption that indicates the campaign (enzyme names, substrate types, etc.)

Tables are preferred over figures when both contain the same data.

Respond ONLY with **minified JSON**. NO markdown fences.

Example:
[{"location": "Table S1", "type": "table", "confidence": 95, "caption": "Table S1. Detailed information...", "reason": "Complete performance metrics", "lineage_hint": "first enzyme family", "campaign_clues": "PYS lineage, pyrrolidine synthesis"}]
""")

PROMPT_EXTRACT_METRICS = dedent("""
You are given either (a) the PNG image of a figure panel, or (b) the caption /
text excerpt that contains numeric reaction performance data for an enzyme.

Extract ONLY the performance metrics, NOT substrate/product names or reaction conditions.
Return a JSON object with the following keys (use **null** if not found):
  * "yield"              - yield as percentage with ONE decimal place precision
  * "ttn"               - turnover number (total turnovers)
  * "ton"               - turnover number if TTN not available
  * "selectivity"       - ee or er value with unit (e.g., "98% ee", ">99:1 er")
  * "conversion"        - conversion percentage if different from yield
  * "tof"               - turnover frequency (turnovers per time unit) if provided
  * "activity"          - specific activity if provided (with unit)
  * "other_metrics"     - dictionary of any other performance metrics with their units
  * "notes"             - any performance-related notes

IMPORTANT: 
- Extract ALL performance metrics provided, even if they use different units.
- Do NOT extract substrate/product names - these will come from SI
- Do NOT extract reaction conditions (temperature, pH, time, solvent)
- If the table shows different reactions (e.g., pyrrolidine vs indoline), note this in "notes"

Respond ONLY with **minified JSON**. NO markdown fences, no commentary.
""")

PROMPT_EXTRACT_FIGURE_METRICS_BATCH = dedent("""
You are analyzing a figure showing enzyme reaction performance data for multiple variants.

Extract performance metrics for ALL the following enzyme variants:
{enzyme_names}

Steps:
1. CHECK THE Y-AXIS SCALE: What is the maximum value? (e.g., 10%, 30%, 50%, 100%)
2. For each enzyme variant listed above:
   - Find its position on the X-axis
   - Read the bar height or data point value
   - Calculate the actual value based on the Y-axis scale
3. Compare all bars to understand relative performance

Return a JSON object with enzyme names as keys, each containing:
  * "yield" - yield with ONE decimal place precision
  * "ttn" - turnover number if shown
  * "ton" - turnover number if TTN not available
  * "selectivity" - ee or er value with unit
  * "conversion" - conversion percentage if different from yield
  * "tof" - turnover frequency if provided
  * "activity" - specific activity if provided
  * "other_metrics" - dictionary of any other metrics
  * "notes" - any relevant notes (including reaction type if different reactions are shown)

CRITICAL: 
- Read ALL pages provided in the image
- If different enzymes are tested for different reactions (e.g., pyrrolidine vs indoline synthesis), note this in "notes"
- For tables, check if data continues beyond what's shown
- Read the Y-axis scale carefully for figures

Example format:
{{"ApePgb LVQ": {{"yield": 0.0, "ttn": null, "notes": "pyrrolidine synthesis", ...}}, ...}}

Respond ONLY with **minified JSON**. NO markdown fences, no commentary.
""")

# Removed substrate scope IUPAC extraction - now handled in model reaction only

PROMPT_FIND_MODEL_REACTION_LOCATION = dedent("""
You are an expert reader of chemistry manuscripts.
Given the following text sections, identify where the MODEL REACTION information is located.

The model reaction is the STANDARD reaction used to evaluate all enzyme variants 
(not the substrate scope). Look for:

- Sections titled "Model Reaction", "Standard Reaction", "General Procedure"
- Text describing the reaction conditions used for enzyme evolution/screening
- Sections describing which substrates were used as the benchmark
- Compound numbers (e.g., "6a", "7a") used in the model reaction

Also identify where the IUPAC names for these specific compounds are listed.

Respond with a JSON object containing:
{
  "model_reaction_location": {
    "location": "section name or description",
    "confidence": 0-100,
    "reason": "why this contains the model reaction",
    "compound_ids": ["list", "of", "compound", "IDs", "if", "found"]
  },
  "conditions_location": {
    "location": "where reaction conditions are described",
    "confidence": 0-100
  },
  "iupac_location": {
    "location": "where IUPAC names are listed (usually SI compound characterization)",
    "confidence": 0-100,
    "compound_section_hint": "specific section to look for compound IDs"
  }
}

Respond ONLY with **minified JSON**. NO markdown fences, no commentary.
""")

PROMPT_MODEL_REACTION = dedent("""
Extract the model/standard reaction used to evaluate enzyme variants in this paper.

This is the reaction used for directed evolution screening, NOT the substrate scope.
Look for terms like "model reaction", "standard substrate", "benchmark reaction", 
or the specific reaction mentioned in enzyme screening/evolution sections.

CRITICAL STEPS FOR IUPAC NAMES:
1. First identify the compound IDs used in the model reaction (e.g., "6a", "7a")
2. Then search the provided context for these compound IDs to find their IUPAC names
3. Look for sections with "Compound 6a", "Product 7a", or similar patterns
4. The IUPAC names are usually given after the compound ID in parentheses or after a colon

CRITICAL FOR SUBSTRATE CONCENTRATION:
- Look carefully in FIGURES and figure captions for substrate concentration information
- Figures often show detailed reaction conditions that may not be in the main text
- Identify the ACTUAL SUBSTRATES being transformed (not reducing agents or cofactors)
- Common pattern: "[X] mM [substrate name]" or "[substrate]: [X] mM"
- DO NOT confuse reducing agents (dithionite, NADH, etc.) with actual substrates
- The substrate is the molecule being chemically transformed by the enzyme

Return a JSON object with:
  * "substrate_list" - Array of substrate identifiers as used in the paper (e.g., ["5", "6a"])
  * "substrate_iupac_list" - Array of IUPAC names for ALL substrates/reagents
  * "product_list" - Array of product identifiers as used in the paper (e.g., ["7a"])
  * "product_iupac_list" - Array of IUPAC names for ALL products formed
  * "reaction_substrate_concentration" - Concentration of actual substrate(s) being transformed, NOT reducing agents like dithionite
  * "cofactor" - Any cofactors used (e.g., "NADH", "NADPH", "FAD", "heme", etc.) or null if none
  * "reaction_temperature" - reaction temperature (e.g., "25°C", "room temperature")
  * "reaction_ph" - reaction pH
  * "reaction_buffer" - buffer system (e.g., "50 mM potassium phosphate")
  * "reaction_other_conditions" - other important conditions (enzyme loading, reducing agents like dithionite, time, anaerobic, etc.)

IMPORTANT: 
- Extract the reaction used for ENZYME EVOLUTION/SCREENING (not substrate scope)
- Substrate concentration = concentration of chemicals being transformed, NOT reducing agents (dithionite, NADH, etc.)
- Maintain correspondence: substrate_list[i] should map to substrate_iupac_list[i], same for products
- If a compound ID has no IUPAC name found, still include it in the list with null in the IUPAC list
- For IUPAC names, look for the SYSTEMATIC chemical names, NOT common/trivial names
- Search the provided context for systematic names - they typically:
  * Use numerical locants (e.g., "prop-2-enoate" not "acrylate")
  * Follow IUPAC nomenclature rules
  * May be found in compound characterization sections
- If you find a common name in the reaction description, search the context for its systematic equivalent
- Look for the exact systematic names as written in the compound characterization
- Do NOT include stereochemistry prefixes like (1R,2S) unless they are part of the compound name in the SI

Respond ONLY with **minified JSON**. NO markdown fences, no commentary.
""")

PROMPT_ANALYZE_LINEAGE_GROUPS = dedent("""
You are analyzing enzyme performance data from a protein engineering manuscript.
Based on the performance data locations and enzyme names, determine if there are 
distinct enzyme lineage groups that were evolved for different purposes.

Look for patterns such as:
- Different tables/figures for different enzyme groups
- Enzyme naming patterns that suggest different lineages
- Different reaction types mentioned in notes or captions
- Clear separations in how variants are organized

Return a JSON object with:
{
  "has_multiple_lineages": true/false,
  "lineage_groups": [
    {
      "group_id": "unique identifier you assign",
      "data_location": "where this group's data is found",
      "enzyme_pattern": "naming pattern or list of enzymes",
      "reaction_type": "what reaction this group catalyzes",
      "evidence": "why you grouped these together"
    }
  ],
  "confidence": 0-100
}

If only one lineage exists, return has_multiple_lineages: false with a single group.

Respond ONLY with **minified JSON**.
""")

PROMPT_FIND_LINEAGE_MODEL_REACTION = dedent("""
For the enzyme group with performance data in {location}, identify the specific 
model reaction used to screen/evaluate these variants.

Context about this group:
{group_context}

Look for:
- References to the specific substrate/product used for this enzyme group
- Text near the performance data location describing the reaction
- Connections between the enzyme names and specific substrates
- Any mention of "screened with", "tested against", "substrate X was used"

Return:
{{
  "substrate_ids": ["list of substrate IDs for this group"],
  "product_ids": ["list of product IDs for this group"],
  "confidence": 0-100,
  "evidence": "text supporting this substrate/product assignment"
}}

Respond ONLY with **minified JSON**.
""")

PROMPT_COMPOUND_MAPPING = dedent("""
Extract compound identifiers and their IUPAC names from the provided sections.

Look for ALL compounds mentioned, including:
1. Compounds with explicit IUPAC names in the text
2. Common reagents where you can provide standard IUPAC names
3. Products that may not be explicitly characterized

CRITICAL - NO HALLUCINATION:
- Extract IUPAC names EXACTLY as written in the source
- DO NOT modify, correct, or "improve" any chemical names
- If a name is written as "benzyl-2-phenylcyclopropane-1-carboxylate", keep it exactly
- Only provide standard IUPAC names for common reagents if not found in text
- If no IUPAC name is found for a compound, return null for iupac_name
- Include ALL compounds found or referenced

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "compound identifier",
      "iupac_name": "complete IUPAC name",
      "common_names": ["any alternative names"],
      "compound_type": "substrate/product/reagent/other",
      "source_location": "where found or inferred"
    }
  ]
}
""")

###############################################################################
# 6 - EXTRACTION ENGINE
###############################################################################

class ReactionExtractor:
    _FIG_RE = re.compile(r"fig(?:ure)?\s+s?\d+[a-z]?", re.I)
    _TAB_RE = re.compile(r"tab(?:le)?\s+s?\d+[a-z]?", re.I)

    def __init__(self, manuscript: Path, si: Optional[Path], cfg: Config, debug_dir: Optional[Path] = None, 
                 campaign_filter: Optional[str] = None):
        self.manuscript = manuscript
        self.si = si
        self.cfg = cfg
        self.model = get_model(cfg)
        self.debug_dir = debug_dir
        self.campaign_filter = campaign_filter  # Filter for specific campaign
        
        # Create debug directory if specified
        if self.debug_dir:
            self.debug_dir = Path(self.debug_dir)
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            LOGGER.info("Debug output will be saved to: %s", self.debug_dir)
        
        if self.campaign_filter:
            LOGGER.info("Filtering extraction for campaign: %s", self.campaign_filter)

        # Preload text pages
        LOGGER.info("Reading PDFs…")
        self.ms_pages = extract_text_by_page(manuscript)
        self.si_pages = extract_text_by_page(si)
        self.all_pages = self.ms_pages + self.si_pages

        # Keep open fitz Docs for image extraction
        self.ms_doc = fitz.open(str(manuscript))
        self.si_doc = fitz.open(str(si)) if si else None

    # ------------------------------------------------------------------
    # 6.1 Find locations (unchanged)
    # ------------------------------------------------------------------

    def _collect_captions_and_titles(self) -> str:
        # Simpler pattern: match any line starting with Table or Figure
        # This catches all variations like "Table S 2", "Table.", "Figure S1", etc.
        cap_pattern = re.compile(r"^(Table|Figure).*", re.I | re.M)
        captions: List[str] = []
        
        # Collect from all pages
        all_text = "\n".join(self.all_pages)
        
        # Find all figure/table captions
        for match in cap_pattern.finditer(all_text):
            caption_start = match.start()
            # Get up to 1200 chars or until double newline
            caption_end = all_text.find("\n\n", caption_start)
            if caption_end == -1 or caption_end - caption_start > 1200:
                caption_end = caption_start + 1200
            caption = all_text[caption_start:caption_end].strip()
            captions.append(caption)
            
        # Also look for SI section titles
        si_titles = re.findall(r"^S\d+\s+[A-Z].{3,80}", "\n".join(self.si_pages), re.M)
        
        result = "\n".join(captions + si_titles)
        LOGGER.debug("Collected %d captions/titles, total length: %d chars", 
                    len(captions) + len(si_titles), len(result))
        
        # Log first few captions for debugging
        if captions:
            LOGGER.debug("First few captions: %s", captions[:3])
            
        return result

    def find_reaction_locations(self) -> List[Dict[str, Any]]:
        """Find all locations containing reaction performance data."""
        # Add campaign context if available
        campaign_context = ""
        if self.campaign_filter:
            campaign_context = f"""
IMPORTANT: You are looking for performance data specifically for the {self.campaign_filter} campaign.
Only return locations that contain data for this specific campaign.
Ignore locations that contain data for other campaigns.

"""
        
        prompt = campaign_context + PROMPT_FIND_LOCATIONS + "\n\n" + self._collect_captions_and_titles()
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.location_temperature,
                debug_dir=self.debug_dir,
                tag="find_locations"
            )
            # Handle both single dict (backwards compatibility) and list
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                LOGGER.error("Expected list or dict from Gemini, got: %s", type(data))
                return []
        except Exception as e:
            LOGGER.error("Failed to find reaction locations: %s", e)
            return []

    def _get_base_location(self, location: str) -> str:
        """Extract the base location identifier (e.g., 'Table S1' from 'Table S1' or 'S41-S47').
        
        This helps group related locations that likely share the same model reaction.
        """
        # Common patterns for locations
        patterns = [
            (r'Table\s+S\d+', 'table'),
            (r'Figure\s+S\d+', 'figure'),
            (r'Table\s+\d+', 'table'),
            (r'Figure\s+\d+', 'figure'),
            (r'S\d+(?:-S\d+)?', 'supp'),  # Supplementary pages like S41-S47
        ]
        
        for pattern, loc_type in patterns:
            match = re.search(pattern, location, re.I)
            if match:
                return match.group(0)
        
        # Default: use the location as-is
        return location

    def analyze_lineage_groups(self, locations: List[Dict[str, Any]], enzyme_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze if there are distinct lineage groups based on different locations.
        
        Key principle: Different locations (tables/figures) indicate different model reactions.
        """
        # Group locations by their base identifier
        location_groups = {}
        
        for loc in locations:
            location_id = loc['location']
            base_location = self._get_base_location(location_id)
            
            if base_location not in location_groups:
                location_groups[base_location] = []
            location_groups[base_location].append(loc)
        
        # Each unique base location represents a potential lineage group
        lineage_groups = []
        
        for base_loc, locs in location_groups.items():
            # Use the location with highest confidence as primary
            primary_loc = max(locs, key=lambda x: x.get('confidence', 0))
            
            # Create a group for this location
            group = {
                'group_id': base_loc,
                'data_location': primary_loc['location'],
                'all_locations': [l['location'] for l in locs],
                'lineage_hint': primary_loc.get('lineage_hint', ''),
                'caption': primary_loc.get('caption', ''),
                'confidence': primary_loc.get('confidence', 0)
            }
            lineage_groups.append(group)
        
        # Multiple distinct base locations = multiple model reactions
        has_multiple = len(location_groups) > 1
        
        LOGGER.info("Location-based lineage analysis: %d distinct base locations found", 
                   len(location_groups))
        for group in lineage_groups:
            LOGGER.info("  - %s: %s", group['group_id'], group['data_location'])
        
        return {
            'has_multiple_lineages': has_multiple,
            'lineage_groups': lineage_groups,
            'confidence': 95
        }
    
    def find_lineage_model_reaction(self, location: str, group_context: str, model_reaction_locations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Find the model reaction for a specific lineage group."""
        # Gather relevant text near this location
        page_text = self._page_with_reference(location) or ""
        
        # Also check manuscript introduction for model reaction info
        intro_text = "\n\n".join(self.ms_pages[:3]) if self.ms_pages else ""
        
        # Build the prompt with location and context
        prompt = PROMPT_FIND_LINEAGE_MODEL_REACTION.format(
            location=location,
            group_context=group_context
        )
        prompt += f"\n\nText near {location}:\n{page_text[:3000]}"
        prompt += f"\n\nManuscript introduction:\n{intro_text[:3000]}"
        
        # If we have model reaction locations, include text from those locations too
        if model_reaction_locations:
            # Add text from model reaction location
            if model_reaction_locations.get("model_reaction_location", {}).get("location"):
                model_loc = model_reaction_locations["model_reaction_location"]["location"]
                model_text = self._get_text_around_location(model_loc)
                if model_text:
                    prompt += f"\n\nText from {model_loc} (potential model reaction location):\n{model_text[:3000]}"
            
            # Add text from conditions location (often contains reaction details)
            if model_reaction_locations.get("conditions_location", {}).get("location"):
                cond_loc = model_reaction_locations["conditions_location"]["location"]
                cond_text = self._get_text_around_location(cond_loc)
                if cond_text:
                    prompt += f"\n\nText from {cond_loc} (reaction conditions):\n{cond_text[:3000]}"
        
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.model_reaction_temperature,
                debug_dir=self.debug_dir,
                tag=f"lineage_model_reaction_{location.replace(' ', '_')}"
            )
            return data if isinstance(data, dict) else {}
        except Exception as e:
            LOGGER.error("Failed to find model reaction for lineage at %s: %s", location, e)
            return {}

    # ------------------------------------------------------------------
    # 6.2 Figure / Table context helpers
    # ------------------------------------------------------------------

    def _page_with_reference(self, ref_id: str) -> Optional[str]:
        for page in self.all_pages:
            if ref_id.lower() in page.lower():
                return page
        return None

    # ---- Table text helper - now returns full page ----
    def _extract_table_context(self, ref: str) -> str:
        page = self._page_with_reference(ref)
        if not page:
            return ""
        # Return the entire page content for better table extraction
        return page

    # ---- Figure caption helper (text fallback) ----
    def _extract_figure_caption(self, ref: str) -> str:
        page = self._page_with_reference(ref)
        if not page:
            return ""
        m = re.search(rf"({re.escape(ref)}[\s\S]{{0,800}}?\.)", page, re.I)
        if m:
            return m.group(1)
        for line in page.split("\n"):
            if ref.lower() in line.lower():
                return line
        return page[:800]

    # ---- NEW: Page image helper for both figures and tables ----
    def _extract_page_png(self, ref: str, extract_figure_only: bool = True) -> Optional[str]:
        """Export the page containing the reference as PNG.
        If extract_figure_only=True, extracts just the figure above the caption.
        If False, extracts the entire page (useful for tables).
        Returns a base64-encoded PNG or None."""
        
        # For table extraction, use multi-page approach
        if not extract_figure_only:
            pages_with_ref = self._find_pages_with_reference(ref)
            if pages_with_ref:
                LOGGER.debug(f"Found {len(pages_with_ref)} pages containing {ref}")
                return self._extract_multiple_pages_png(pages_with_ref)
            return None

        # For figure extraction, search both documents
        for doc in filter(None, [self.ms_doc, self.si_doc]):
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                page_text = page.get_text()
                if ref.lower() not in page_text.lower():
                    continue
                # Get caption bbox
                text_instances = page.search_for(ref, quads=False)
                if not text_instances:
                    continue
                cap_rect = text_instances[0]  # first match
                
                if extract_figure_only:
                    # Sort images by y0 (top) coordinate ascending
                    images = sorted(page.get_images(full=True), key=lambda im: im[7])
                    # Find first image whose bottom y is **above** caption top y
                    for img in images:
                        xref = img[0]
                        # Get image rectangles to find position
                        img_rects = page.get_image_rects(xref)
                        if img_rects:
                            img_rect = img_rects[0]  # First rectangle
                            if img_rect.y1 < cap_rect.y0:  # fully above caption
                                # Extract image bytes
                                pix = fitz.Pixmap(doc, xref)
                                if pix.alpha:  # RGBA -> RGB
                                    pix = fitz.Pixmap(fitz.csRGB, pix)
                                img_bytes = pix.tobytes("png")
                                return b64encode(img_bytes).decode()
                else:
                    # Extract the entire page as an image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                    return b64encode(img_bytes).decode()
        return None
    
    def _find_pages_with_reference(self, ref: str) -> List[Tuple[fitz.Document, int]]:
        """Find all pages containing the reference across documents.
        Returns list of (document, page_number) tuples."""
        pages_found = []
        
        for doc in filter(None, [self.ms_doc, self.si_doc]):
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                page_text = page.get_text()
                if ref.lower() in page_text.lower():
                    pages_found.append((doc, page_number))
                    
        return pages_found
    
    def _extract_multiple_pages_png(self, pages: List[Tuple[fitz.Document, int]]) -> Optional[str]:
        """Extract multiple pages as a combined PNG image."""
        if not pages:
            return None
            
        # Sort pages by document and page number
        pages.sort(key=lambda x: (id(x[0]), x[1]))
        
        # Extract the range of pages including one page after
        all_images = []
        for i, (doc, page_num) in enumerate(pages):
            # Add the current page
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = doc.load_page(page_num).get_pixmap(matrix=mat)
            all_images.append(pix)
            
            # If this is the last page with the reference, also add the next page
            if i == len(pages) - 1 and page_num + 1 < doc.page_count:
                next_pix = doc.load_page(page_num + 1).get_pixmap(matrix=mat)
                all_images.append(next_pix)
                LOGGER.info(f"Added next page: page {page_num + 2}")  # +2 because page numbers are 1-based for users
        
        if not all_images:
            return None
            
        # If only one page, return it directly
        if len(all_images) == 1:
            return b64encode(all_images[0].tobytes("png")).decode()
            
        # Combine multiple pages vertically
        if not all_images:
            return None
            
        if len(all_images) == 1:
            return b64encode(all_images[0].tobytes("png")).decode()
            
        # Calculate dimensions for combined image
        total_height = sum(pix.height for pix in all_images)
        max_width = max(pix.width for pix in all_images)
        
        LOGGER.info(f"Combining {len(all_images)} pages into single image ({max_width}x{total_height})")
        
        # Create a new document with a single page that can hold all images
        output_doc = fitz.open()
        
        # Create a page with the combined dimensions
        # Note: PDF pages have a max size, so we scale if needed
        max_pdf_dimension = 14400  # PDF max is ~200 inches at 72 DPI
        scale = 1.0
        if total_height > max_pdf_dimension or max_width > max_pdf_dimension:
            scale = min(max_pdf_dimension / total_height, max_pdf_dimension / max_width)
            total_height = int(total_height * scale)
            max_width = int(max_width * scale)
            LOGGER.warning(f"Scaling down by {scale:.2f} to fit PDF limits")
        
        page = output_doc.new_page(width=max_width, height=total_height)
        
        # Insert each image into the page
        y_offset = 0
        for i, pix in enumerate(all_images):
            # Center each image horizontally
            x_offset = (max_width - pix.width * scale) / 2
            
            # Create rect for image placement
            rect = fitz.Rect(x_offset, y_offset, 
                           x_offset + pix.width * scale, 
                           y_offset + pix.height * scale)
            
            # Insert the image
            page.insert_image(rect, pixmap=pix)
            y_offset += pix.height * scale
            
        # Convert the page to a pixmap
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for quality
        combined_pix = page.get_pixmap(matrix=mat)
        
        # Convert to PNG and return
        img_bytes = combined_pix.tobytes("png")
        output_doc.close()
        
        return b64encode(img_bytes).decode()

    # ------------------------------------------------------------------
    # 6.3 Extract metrics in batch
    # ------------------------------------------------------------------

    def extract_metrics_batch(self, enzyme_list: List[str], ref: str) -> List[Dict[str, Any]]:
        """Extract performance metrics for multiple enzymes from the identified location in batch."""
        ref_lc = ref.lower()
        image_b64: Optional[str] = None
        
        # Add campaign context if available
        campaign_context = ""
        if self.campaign_filter:
            campaign_context = f"\n\nIMPORTANT: You are extracting data for the {self.campaign_filter} campaign.\nOnly extract data that is relevant to this specific campaign.\n"
        
        if self._TAB_RE.search(ref_lc):
            # For tables, try to extract the page as an image first
            image_b64 = self._extract_page_png(ref, extract_figure_only=False)
            if not image_b64:
                LOGGER.debug("No page image found for %s - using full page text", ref)
                snippet = self._extract_table_context(ref)
        elif self._FIG_RE.search(ref_lc):
            # For figures, extract just the figure image
            image_b64 = self._extract_page_png(ref, extract_figure_only=True)
            if not image_b64:
                LOGGER.debug("No figure image found for %s - using caption text", ref)
                snippet = self._extract_figure_caption(ref)
        else:
            snippet = self._page_with_reference(ref) or ""

        enzyme_names = "\n".join([f"- {enzyme}" for enzyme in enzyme_list])
        
        if image_b64:
            # Use batch extraction prompt for image analysis
            prompt = campaign_context + PROMPT_EXTRACT_FIGURE_METRICS_BATCH.format(enzyme_names=enzyme_names)
            LOGGER.info("Gemini Vision: extracting metrics for %d enzymes from %s…", len(enzyme_list), ref)
            tag = f"extract_metrics_batch_vision"
        else:
            # Add enzyme names to prompt for batch extraction
            prompt = campaign_context + PROMPT_EXTRACT_METRICS + f"\n\nExtract performance data for ALL these enzyme variants:\n{enzyme_names}\n\n=== CONTEXT ===\n" + snippet[:4000]
            LOGGER.info("Gemini: extracting metrics for %d enzymes from %s…", len(enzyme_list), ref)
            tag = f"extract_metrics_batch"

        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.extract_temperature,
                debug_dir=self.debug_dir,
                tag=tag,
                image_b64=image_b64
            )
            
            # Handle the response format - expecting a dict with enzyme names as keys
            results = []
            if isinstance(data, dict):
                for enzyme in enzyme_list:
                    enzyme_data = data.get(enzyme, {})
                    if not isinstance(enzyme_data, dict):
                        enzyme_data = {"error": "No data found"}
                    
                    # Normalize keys
                    # No need to rename - we now use "yield" directly
                    if "TTN" in enzyme_data and "ttn" not in enzyme_data:
                        enzyme_data["ttn"] = enzyme_data.pop("TTN")
                    
                    # Add metadata
                    enzyme_data["enzyme"] = enzyme
                    enzyme_data["location_ref"] = ref
                    enzyme_data["used_image"] = bool(image_b64)
                    results.append(enzyme_data)
            else:
                # Fallback if response format is unexpected
                LOGGER.warning("Unexpected response format from batch extraction")
                for enzyme in enzyme_list:
                    results.append({
                        "enzyme": enzyme,
                        "location_ref": ref,
                        "used_image": bool(image_b64),
                        "error": "Invalid response format"
                    })
                    
        except Exception as e:
            LOGGER.warning("Failed to extract metrics batch: %s", e)
            results = []
            for enzyme in enzyme_list:
                results.append({
                    "enzyme": enzyme,
                    "location_ref": ref,
                    "used_image": bool(image_b64),
                    "error": str(e)
                })
        
        return results

    # Removed extract_iupac_names - substrate scope IUPAC extraction no longer needed

    # ------------------------------------------------------------------
    # 6.4 Model reaction with location finding
    # ------------------------------------------------------------------

    def find_model_reaction_locations(self, enzyme_variants: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Find locations for model reaction scheme, conditions, and IUPAC names."""
        # Collect all text including section titles, captions, and schemes
        all_text = self._collect_captions_and_titles()
        
        # Also add first few pages of main text and SI
        ms_preview = "\n".join(self.ms_pages[:5])[:5000]
        si_preview = "\n".join(self.si_pages[:10])[:5000] if self.si_pages else ""
        
        # Add enzyme context if provided
        enzyme_context = ""
        if enzyme_variants and self.campaign_filter:
            enzyme_context = f"""
IMPORTANT CONTEXT:
You are looking for the model reaction used specifically for these enzyme variants:
{', '.join(enzyme_variants[:10])}{'...' if len(enzyme_variants) > 10 else ''}

These variants belong to campaign: {self.campaign_filter}

Focus on finding the model reaction that was used to evaluate THESE specific variants.
Different campaigns may use different model reactions.
"""
        
        prompt = enzyme_context + PROMPT_FIND_MODEL_REACTION_LOCATION + "\n\n=== CAPTIONS AND SECTIONS ===\n" + all_text + "\n\n=== MANUSCRIPT TEXT PREVIEW ===\n" + ms_preview + "\n\n=== SI TEXT PREVIEW ===\n" + si_preview
        
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.location_temperature,
                debug_dir=self.debug_dir,
                tag="find_model_reaction_locations"
            )
            if not isinstance(data, dict):
                LOGGER.error("Expected dict from Gemini, got: %s", type(data))
                return None
            return data
        except Exception as e:
            LOGGER.error("Failed to find model reaction locations: %s", e)
            return None

    def _get_text_around_location(self, location: str) -> Optional[str]:
        """Extract text around a given location identifier."""
        location_lower = location.lower()
        
        # Handle compound locations like "Figure 2 caption and Section I"
        # Extract the first figure/table/scheme reference
        figure_match = re.search(r"(figure|scheme|table)\s*\d+", location_lower)
        if figure_match:
            primary_location = figure_match.group(0)
            # Try to find this primary location first
            for page_text in self.all_pages:
                if primary_location in page_text.lower():
                    idx = page_text.lower().index(primary_location)
                    start = max(0, idx - 500)
                    end = min(len(page_text), idx + 3000)
                    return page_text[start:end]
        
        # Search in all pages for exact match
        for page_text in self.all_pages:
            if location_lower in page_text.lower():
                # Find the location and extract context around it
                idx = page_text.lower().index(location_lower)
                start = max(0, idx - 500)
                end = min(len(page_text), idx + 3000)
                return page_text[start:end]
        
        # If not found in exact form, try pattern matching
        # For scheme/figure references
        if re.search(r"(scheme|figure|table)\s*\d+", location_lower):
            pattern = re.compile(location.replace(" ", r"\s*"), re.I)
            for page_text in self.all_pages:
                match = pattern.search(page_text)
                if match:
                    start = max(0, match.start() - 500)
                    end = min(len(page_text), match.end() + 3000)
                    return page_text[start:end]
        
        return None

    def _get_extended_text_around_location(self, location: str, before: int = 2000, after: int = 10000) -> Optional[str]:
        """Extract extended text around a given location identifier."""
        location_lower = location.lower()
        
        # Search in all pages
        for i, page_text in enumerate(self.all_pages):
            if location_lower in page_text.lower():
                # Find the location
                idx = page_text.lower().index(location_lower)
                
                # Collect text from multiple pages if needed
                result = []
                
                # Start from current page
                start = max(0, idx - before)
                result.append(page_text[start:])
                
                # Add subsequent pages up to 'after' characters
                chars_collected = len(page_text) - start
                page_idx = i + 1
                
                while chars_collected < after + before and page_idx < len(self.all_pages):
                    next_page = self.all_pages[page_idx]
                    chars_to_take = min(len(next_page), after + before - chars_collected)
                    result.append(next_page[:chars_to_take])
                    chars_collected += chars_to_take
                    page_idx += 1
                
                return "\n".join(result)
        
        return None

    def _extract_sections_by_title(self, sections: List[str], max_chars_per_section: int = 5000) -> str:
        """Extract text from sections with specific titles."""
        extracted_text = []
        
        for section_title in sections:
            pattern = re.compile(rf"{re.escape(section_title)}.*?(?=\n\n[A-Z]|\Z)", re.I | re.S)
            
            # Search in all pages
            for page in self.all_pages:
                match = pattern.search(page)
                if match:
                    section_text = match.group(0)[:max_chars_per_section]
                    extracted_text.append(f"=== {section_title} ===\n{section_text}")
                    break
        
        return "\n\n".join(extracted_text)

    def _extract_compound_mappings_from_text(
        self,
        extraction_text: str,
        compound_ids: List[str] = None,
        tag_suffix: str = "",
    ) -> Dict[str, CompoundMapping]:
        """Helper function to extract compound mappings from provided text."""
        prompt = PROMPT_COMPOUND_MAPPING
        if compound_ids:
            prompt += "\n\nCOMPOUNDS TO MAP: " + ", ".join(sorted(compound_ids))
        prompt += "\n\nTEXT:\n" + extraction_text
        
        tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
        
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.model_reaction_temperature,
                debug_dir=self.debug_dir,
                tag=tag,
            )
            
            mappings = {}
            for item in data.get("compound_mappings", []):
                # Handle both old format (with identifiers list) and new format (with identifier string)
                identifiers = item.get("identifiers", [])
                if not identifiers and item.get("identifier"):
                    identifiers = [item.get("identifier")]
                
                mapping = CompoundMapping(
                    identifiers=identifiers,
                    iupac_name=item.get("iupac_name", ""),
                    common_names=item.get("common_names", []),
                    compound_type=item.get("compound_type", "unknown"),
                    source_location=item.get("source_location")
                )
                
                # Create lookup entries for all identifiers and common names
                for identifier in mapping.identifiers + mapping.common_names:
                    if identifier:
                        mappings[identifier.lower().strip()] = mapping
            
            return mappings
            
        except Exception as exc:
            LOGGER.error("Failed to extract compound mappings: %s", exc)
            return {}

    def _extract_compound_mappings_with_figures(
        self,
        text: str,
        compound_ids: List[str],
        figure_images: Dict[str, str],
        tag_suffix: str = "",
    ) -> Dict[str, CompoundMapping]:
        """Extract compound mappings using multimodal approach with figures."""
        # Enhanced prompt for figure-based extraction
        prompt = """You are analyzing chemical figures and manuscript text to identify compound IUPAC names.

TASK: Find the IUPAC names for these specific compound identifiers: """ + ", ".join(sorted(compound_ids)) + """

Use your best knowledge, Look carefully in:
1. The chemical structures shown in figures - infer IUPAC names from drawn structures
2. Figure captions that may define compounds
3. Text that refers to these compound numbers
4. Reaction schemes showing transformations


IMPORTANT:
- Only provide IUPAC names you can determine from the figures or text
- If a structure is clearly shown in a figure, derive the IUPAC name from it

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "compound identifier", 
      "iupac_name": "IUPAC name",
      "common_names": ["common names if any"],
      "compound_type": "substrate/product/reagent",
      "source_location": "where found (e.g., Figure 3, manuscript text)"
    }
  ]
}

TEXT FROM MANUSCRIPT:
""" + text
        
        # Prepare multimodal content
        content_parts = [prompt]
        
        # Add figure images
        if figure_images:
            for fig_ref, fig_base64 in figure_images.items():
                try:
                    img_bytes = b64decode(fig_base64)
                    image = PIL.Image.open(io.BytesIO(img_bytes))
                    content_parts.append(f"\n[Figure: {fig_ref}]")
                    content_parts.append(image)
                    LOGGER.info("Added figure %s to multimodal compound mapping", fig_ref)
                except Exception as e:
                    LOGGER.warning("Failed to add figure %s: %s", fig_ref, e)
        
        tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
        
        try:
            # Log multimodal call
            LOGGER.info("=== GEMINI MULTIMODAL API CALL: COMPOUND_MAPPING_WITH_FIGURES ===")
            LOGGER.info("Text prompt length: %d characters", len(prompt))
            LOGGER.info("Number of images: %d", len(content_parts) - 1)
            LOGGER.info("Compounds to find: %s", ", ".join(sorted(compound_ids)))
            
            # Save debug info
            if self.debug_dir:
                prompt_file = self.debug_dir / f"{tag}_prompt_{int(time.time())}.txt"
                with open(prompt_file, 'w') as f:
                    f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Text length: {len(prompt)} characters\n")
                    f.write(f"Images included: {len(content_parts) - 1}\n")
                    for fig_ref in figure_images.keys():
                        f.write(f"  - {fig_ref}\n")
                    f.write("="*80 + "\n\n")
                    f.write(prompt)
                LOGGER.info("Full prompt saved to: %s", prompt_file)
            
            # Make multimodal API call
            response = self.model.generate_content(content_parts)
            raw_text = response.text.strip()
            
            # Log response
            LOGGER.info("Gemini multimodal response length: %d characters", len(raw_text))
            
            if self.debug_dir:
                response_file = self.debug_dir / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw_text)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw_text)
                LOGGER.info("Full response saved to: %s", response_file)
            
            # Parse JSON
            data = json.loads(raw_text.strip('```json').strip('```').strip())
            
            mappings = {}
            for item in data.get("compound_mappings", []):
                identifiers = item.get("identifiers", [])
                if not identifiers and item.get("identifier"):
                    identifiers = [item.get("identifier")]
                
                mapping = CompoundMapping(
                    identifiers=identifiers,
                    iupac_name=item.get("iupac_name", ""),
                    common_names=item.get("common_names", []),
                    compound_type=item.get("compound_type", "unknown"),
                    source_location=item.get("source_location")
                )
                
                for identifier in mapping.identifiers + mapping.common_names:
                    if identifier:
                        mappings[identifier.lower().strip()] = mapping
            
            return mappings
            
        except Exception as exc:
            LOGGER.error("Failed to extract compound mappings with figures: %s", exc)
            return {}

    def _extract_compound_mappings_adaptive(
        self,
        compound_ids: List[str],
        initial_sections: List[str] = None,
    ) -> Dict[str, CompoundMapping]:
        """Extract compound ID to IUPAC name mappings using adaptive 3-tier strategy.
        
        1. First attempts extraction from standard sections
        2. Expands search to additional sections if compounds are missing
        3. Uses multimodal figure analysis as final fallback
        """
        if not compound_ids:
            return {}
            
        LOGGER.info("Starting adaptive compound mapping for %d compounds: %s", 
                   len(compound_ids), sorted(compound_ids))
        
        # Tier 1: Standard sections (manuscript + initial SI sections)
        initial_sections = initial_sections or [
            "General procedure", "Compound characterization", 
            "Synthesis", "Experimental", "Materials and methods"
        ]
        
        # Include manuscript pages (first 10) for model reaction context
        manuscript_text = "\n\n".join(self.ms_pages[:10])
        
        # Extract from initial sections
        extraction_text = self._extract_sections_by_title(initial_sections)
        if extraction_text:
            extraction_text = manuscript_text + "\n\n" + extraction_text
        else:
            extraction_text = manuscript_text
        
        # First extraction attempt
        mappings = self._extract_compound_mappings_from_text(
            extraction_text[:50000], compound_ids, tag_suffix="initial"
        )
        LOGGER.info("Tier 1: Found %d compound mappings from standard sections", len(mappings))
        
        # Check for missing compounds
        missing_compounds = []
        for cid in compound_ids:
            mapping = mappings.get(cid.lower().strip())
            if not mapping or not mapping.iupac_name:
                missing_compounds.append(cid)
        
        # Tier 2: Expanded search + multimodal with figures
        if missing_compounds:
            LOGGER.info("Tier 2: %d compounds still missing IUPAC names: %s", 
                       len(missing_compounds), sorted(missing_compounds))
            
            # Additional sections to search
            additional_sections = [
                "Engineering strategy", "Evolution campaign",
                "Screening", "Optimization", "Substrate synthesis",
                "Supporting Information", "Supplementary Methods"
            ]
            
            # Extract from additional sections
            additional_text = self._extract_sections_by_title(additional_sections)
            
            # Also extract any figures that might contain compound structures
            figure_images = {}
            figure_refs = ["Figure 1", "Figure 2", "Figure 3", "Scheme 1", "Scheme 2"]
            for ref in figure_refs:
                img_b64 = self._extract_page_png(ref, extract_figure_only=True)
                if img_b64:
                    figure_images[ref] = img_b64
                    LOGGER.info("Extracted %s for compound mapping", ref)
            
            # Try multimodal approach with figures and expanded text
            if figure_images or additional_text:
                combined_text = additional_text[:30000] if additional_text else ""
                expanded_mappings = self._extract_compound_mappings_with_figures(
                    combined_text, missing_compounds, figure_images, tag_suffix="tier2"
                )
                
                # Merge new mappings
                new_found = 0
                for key, mapping in expanded_mappings.items():
                    if key not in mappings or not mappings[key].iupac_name:
                        if mapping.iupac_name:
                            mappings[key] = mapping
                            new_found += 1
                            LOGGER.info("Found IUPAC name for '%s': %s", 
                                      key, mapping.iupac_name[:50] + "..." if len(mapping.iupac_name) > 50 else mapping.iupac_name)
                
                LOGGER.info("Tier 2: Found %d additional compound mappings", new_found)
        
            # Check again for still missing compounds
            still_missing = []
            for cid in missing_compounds:
                mapping = mappings.get(cid.lower().strip())
                if not mapping or not mapping.iupac_name:
                    still_missing.append(cid)
            
            # Tier 3: Full manuscript search with all available figures
            if still_missing:
                LOGGER.info("Tier 3: %d compounds still missing, trying full manuscript search", 
                           len(still_missing))
                
                # Get all SI figures
                si_figure_refs = []
                for page in self.si_pages[:5]:  # Check first 5 SI pages
                    matches = re.findall(r"Figure S\d+|Scheme S\d+", page)
                    si_figure_refs.extend(matches[:5])  # Limit to 5 figures
                
                # Extract SI figures
                for ref in set(si_figure_refs):
                    if ref not in figure_images:
                        img_b64 = self._extract_page_png(ref, extract_figure_only=True)
                        if img_b64:
                            figure_images[ref] = img_b64
                            LOGGER.info("Extracted %s for final compound mapping", ref)
                
                # Full text search including all pages
                full_text = "\n\n".join(self.all_pages[:30])  # First 30 pages
                
                final_mappings = self._extract_compound_mappings_with_figures(
                    full_text[:50000], still_missing, figure_images, tag_suffix="tier3"
                )
                
                # Merge final mappings
                final_found = 0
                for key, mapping in final_mappings.items():
                    if key not in mappings or not mappings[key].iupac_name:
                        if mapping.iupac_name:
                            mappings[key] = mapping
                            final_found += 1
                            LOGGER.info("Found IUPAC name for '%s' in final search: %s", 
                                      key, mapping.iupac_name[:50] + "..." if len(mapping.iupac_name) > 50 else mapping.iupac_name)
                
                LOGGER.info("Tier 3: Found %d additional compound mappings", final_found)
        
        LOGGER.info("Adaptive compound mapping complete: %d total mappings", len(mappings))
        return mappings

    def gather_model_reaction_info(self, enzyme_variants: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract model reaction information using identified locations and 3-tier compound mapping."""
        # First find the best locations
        locations = self.find_model_reaction_locations(enzyme_variants)
        if not locations:
            LOGGER.warning("Could not find model reaction locations, using fallback approach")
            # Fallback to old approach but include more manuscript text
            pattern = re.compile(r"(model reaction|general procedure|typical .*run|standard conditions|scheme 1|figure 1)", re.I)
            snippets: List[str] = []
            # Search both manuscript and SI
            for page in self.all_pages:
                if pattern.search(page):
                    para_match = re.search(r"(.{0,3000}?\n\n)", page)
                    if para_match:
                        snippets.append(para_match.group(0))
                if len(snippets) >= 5:
                    break
            text_context = "\n---\n".join(snippets)[:10000]
        else:
            # Gather text from identified locations
            text_snippets = []
            
            # Always include manuscript abstract and introduction for context
            if self.ms_pages:
                # First 3 pages typically contain abstract, introduction, and model reaction info
                manuscript_intro = "\n\n".join(self.ms_pages[:3])
                text_snippets.append(f"=== MANUSCRIPT INTRODUCTION ===\n{manuscript_intro}")
            
            # Get model reaction context
            if locations.get("model_reaction_location", {}).get("location"):
                model_loc = locations["model_reaction_location"]["location"]
                LOGGER.info("Looking for model reaction at: %s", model_loc)
                model_text = self._get_text_around_location(model_loc)
                if model_text:
                    text_snippets.append(f"=== {model_loc} ===\n{model_text}")
            
            # Get conditions context  
            if locations.get("conditions_location", {}).get("location"):
                cond_loc = locations["conditions_location"]["location"]
                LOGGER.info("Looking for reaction conditions at: %s", cond_loc)
                cond_text = self._get_text_around_location(cond_loc)
                if cond_text:
                    text_snippets.append(f"=== {cond_loc} ===\n{cond_text}")
            
            # Get IUPAC names context from the specific location identified
            if locations.get("iupac_location", {}).get("location"):
                iupac_loc = locations["iupac_location"]["location"]
                LOGGER.info("Looking for IUPAC names at: %s", iupac_loc)
                
                # If we have compound IDs from the model reaction location, search for them specifically
                compound_ids = locations.get("model_reaction_location", {}).get("compound_ids", [])
                if compound_ids:
                    LOGGER.info("Looking for specific compound IDs: %s", compound_ids)
                    # Search for each compound ID in the SI
                    for compound_id in compound_ids:
                        # Search patterns for compound characterization
                        patterns = [
                            rf"(?:compound\s+)?{re.escape(compound_id)}[:\s]*\([^)]+\)",  # 6a: (IUPAC name)
                            rf"(?:compound\s+)?{re.escape(compound_id)}[.\s]+[A-Z][^.]+",  # 6a. IUPAC name
                            rf"{re.escape(compound_id)}[^:]*:\s*[^.]+",  # Any format with colon
                        ]
                        
                        for page in self.si_pages:
                            for pattern in patterns:
                                match = re.search(pattern, page, re.I)
                                if match:
                                    # Get extended context around the match
                                    start = max(0, match.start() - 200)
                                    end = min(len(page), match.end() + 500)
                                    text_snippets.append(f"=== Compound {compound_id} characterization ===\n{page[start:end]}")
                                    break
                
                # Also search for substrate names mentioned in the reaction to find their IUPAC equivalents
                # Look for common substrate patterns in compound listings
                substrate_patterns = [
                    r"(?:substrate|reactant|reagent)s?\s*:?\s*([^.]+)",
                    r"(?:starting\s+material)s?\s*:?\s*([^.]+)",
                    r"\d+\.\s*([A-Za-z\s\-]+)(?:\s*\([^)]+\))?",  # numbered compound lists
                ]
                
                for pattern in substrate_patterns:
                    for page in self.si_pages[:5]:  # Check first few SI pages
                        matches = re.finditer(pattern, page, re.I)
                        for match in matches:
                            text = match.group(0)
                            if len(text) < 200:  # Reasonable length check
                                start = max(0, match.start() - 100)
                                end = min(len(page), match.end() + 300)
                                snippet = page[start:end]
                                if "prop-2-enoate" in snippet or "diazirin" in snippet:
                                    text_snippets.append(f"=== Substrate characterization ===\n{snippet}")
                                    break
                
                # Also get general IUPAC context
                iupac_text = self._get_text_around_location(iupac_loc)
                if iupac_text:
                    # Get more context around the identified location
                    extended_iupac_text = self._get_extended_text_around_location(iupac_loc, before=2000, after=10000)
                    if extended_iupac_text:
                        text_snippets.append(f"=== {iupac_loc} ===\n{extended_iupac_text}")
                    else:
                        text_snippets.append(f"=== {iupac_loc} ===\n{iupac_text}")
            
            text_context = "\n\n".join(text_snippets)[:35000]  # Increase limit for more context
        
        # Extract figure images for model reaction if identified
        figure_images = {}
        if locations:
            # Extract images from model reaction and conditions locations
            for loc_key in ["model_reaction_location", "conditions_location"]:
                loc_info = locations.get(loc_key, {})
                location = loc_info.get("location", "")
                if location and ("figure" in location.lower() or "fig" in location.lower()):
                    # Extract just the figure reference (e.g., "Figure 2" from "Figure 2. Caption...")
                    fig_match = re.search(r"(Figure\s+\d+|Fig\s+\d+|Scheme\s+\d+)", location, re.I)
                    if fig_match:
                        fig_ref = fig_match.group(1)
                        LOGGER.info("Extracting image for %s from %s", fig_ref, loc_key)
                        img_b64 = self._extract_page_png(fig_ref, extract_figure_only=True)
                        if img_b64:
                            figure_images[fig_ref] = img_b64
                            LOGGER.info("Successfully extracted %s image for model reaction analysis", fig_ref)
        
        # Extract compound IDs from locations
        compound_ids = []
        if locations and locations.get("model_reaction_location", {}).get("compound_ids"):
            compound_ids = locations["model_reaction_location"]["compound_ids"]
            LOGGER.info("Found compound IDs in model reaction: %s", compound_ids)
        
        # Use the 3-tier compound mapping approach if we have compound IDs
        compound_mappings = {}
        if compound_ids:
            LOGGER.info("Using 3-tier compound mapping approach for compounds: %s", compound_ids)
            compound_mappings = self._extract_compound_mappings_adaptive(compound_ids)
            
            # Add the mapped IUPAC names to the context for better extraction
            if compound_mappings:
                mapping_text = "\n\n=== COMPOUND MAPPINGS ===\n"
                for cid in compound_ids:
                    mapping = compound_mappings.get(cid.lower().strip())
                    if mapping and mapping.iupac_name:
                        mapping_text += f"Compound {cid}: {mapping.iupac_name}\n"
                text_context += mapping_text
        
        # Include both manuscript and SI text for better coverage
        prompt = PROMPT_MODEL_REACTION + "\n\n=== CONTEXT ===\n" + text_context
        
        try:
            # Use multimodal extraction if we have figure images
            if figure_images:
                LOGGER.info("Using multimodal extraction with %d figure images", len(figure_images))
                # Prepare multimodal content
                content_parts = [prompt]
                
                # Add figure images
                for fig_ref, fig_base64 in figure_images.items():
                    try:
                        img_bytes = b64decode(fig_base64)
                        image = PIL.Image.open(io.BytesIO(img_bytes))
                        content_parts.append(f"\n[Figure: {fig_ref}]")
                        content_parts.append(image)
                    except Exception as e:
                        LOGGER.warning("Failed to process figure %s: %s", fig_ref, e)
                
                # Use multimodal model if we have valid images
                if len(content_parts) > 1:
                    # Create multimodal request
                    model = genai.GenerativeModel(
                        model_name=self.cfg.model_name,
                        generation_config={
                            "temperature": self.cfg.model_reaction_temperature,
                            "top_p": self.cfg.top_p,
                            "top_k": 1,
                            "max_output_tokens": self.cfg.max_tokens,
                        }
                    )
                    
                    response = model.generate_content(content_parts)
                    
                    # Parse JSON from response
                    if response and response.text:
                        # Save debug output
                        if self.debug_dir:
                            timestamp = int(time.time())
                            _dump(prompt, self.debug_dir / f"model_reaction_multimodal_prompt_{timestamp}.txt")
                            _dump(response.text, self.debug_dir / f"model_reaction_multimodal_response_{timestamp}.txt")
                        
                        # Extract JSON from response
                        text = response.text.strip()
                        if text.startswith("```json"):
                            text = text[7:]
                        if text.endswith("```"):
                            text = text[:-3]
                        data = json.loads(text.strip())
                    else:
                        raise ValueError("Empty response from multimodal model")
                else:
                    # Fall back to text-only extraction
                    data = generate_json_with_retry(
                        self.model,
                        prompt,
                        temperature=self.cfg.model_reaction_temperature,
                        debug_dir=self.debug_dir,
                        tag="model_reaction"
                    )
            else:
                # Standard text-only extraction
                data = generate_json_with_retry(
                    self.model,
                    prompt,
                    temperature=self.cfg.model_reaction_temperature,
                    debug_dir=self.debug_dir,
                    tag="model_reaction"
                )
            
            # Handle the new array format for substrates/products
            if isinstance(data, dict):
                # If we have compound mappings, enhance the IUPAC names
                if compound_ids and compound_mappings:
                    # Try to map substrate/product lists through compound IDs
                    substrate_list = data.get("substrate_iupac_list", [])
                    if isinstance(substrate_list, list):
                        enhanced_substrates = []
                        for item in substrate_list:
                            # Check if it's a compound ID that we can map
                            mapping = compound_mappings.get(str(item).lower().strip())
                            if mapping and mapping.iupac_name:
                                enhanced_substrates.append(mapping.iupac_name)
                            elif item and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', str(item)):
                                # Keep valid IUPAC names
                                enhanced_substrates.append(str(item))
                        data["substrate_iupac_list"] = enhanced_substrates
                    
                    product_list = data.get("product_iupac_list", [])
                    if isinstance(product_list, list):
                        enhanced_products = []
                        for item in product_list:
                            # Check if it's a compound ID that we can map
                            mapping = compound_mappings.get(str(item).lower().strip())
                            if mapping and mapping.iupac_name:
                                enhanced_products.append(mapping.iupac_name)
                            elif item and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', str(item)):
                                # Keep valid IUPAC names
                                enhanced_products.append(str(item))
                        data["product_iupac_list"] = enhanced_products
                
                # Validate and convert arrays to semicolon-separated strings for CSV compatibility
                if "substrate_iupac_list" in data and isinstance(data["substrate_iupac_list"], list):
                    # Filter out non-IUPAC names (abbreviations like "1a", "S1", etc.)
                    valid_substrates = [s for s in data["substrate_iupac_list"] 
                                      if s and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', s)]
                    # Join with semicolons instead of JSON encoding
                    data["substrate_iupac_list"] = "; ".join(valid_substrates) if valid_substrates else ""
                else:
                    data["substrate_iupac_list"] = ""
                    
                if "product_iupac_list" in data and isinstance(data["product_iupac_list"], list):
                    # Filter out non-IUPAC names
                    valid_products = [p for p in data["product_iupac_list"] 
                                    if p and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', p)]
                    # Join with semicolons instead of JSON encoding
                    data["product_iupac_list"] = "; ".join(valid_products) if valid_products else ""
                else:
                    data["product_iupac_list"] = ""
                    
        except Exception as exc:
            LOGGER.error("Failed to extract model reaction: %s", exc)
            data = {
                "substrate_iupac_list": None,
                "product_iupac_list": None,
                "reaction_substrate_concentration": None,
                "cofactor": None,
                "reaction_temperature": None,
                "reaction_ph": None,
                "reaction_buffer": None,
                "reaction_other_conditions": None,
                "error": str(exc)
            }
        
        # Ensure all expected keys are present
        expected_keys = [
            "substrate_list", "substrate_iupac_list", "product_list", "product_iupac_list", 
            "reaction_substrate_concentration", "cofactor", "reaction_temperature", 
            "reaction_ph", "reaction_buffer", "reaction_other_conditions"
        ]
        for key in expected_keys:
            data.setdefault(key, None)
            
        return data

    def _process_single_lineage(self, location: Dict[str, Any], enzyme_df: pd.DataFrame) -> pd.DataFrame:
        """Process a single lineage case - still extract based on location."""
        # Even for single lineage, use location-based extraction
        lineage_analysis = {
            'has_multiple_lineages': False,
            'lineage_groups': [{
                'group_id': self._get_base_location(location['location']),
                'data_location': location['location'],
                'lineage_hint': location.get('lineage_hint', ''),
                'caption': location.get('caption', ''),
                'confidence': location.get('confidence', 0)
            }]
        }
        
        return self._process_multiple_lineages([location], enzyme_df, lineage_analysis)
    
    def _process_multiple_lineages_by_confidence(self, locations: List[Dict[str, Any]], 
                                                 enzyme_df: pd.DataFrame,
                                                 lineage_analysis: Dict[str, Any]) -> pd.DataFrame:
        """Process multiple lineages by confidence, detecting which enzymes belong to which campaign."""
        # Get all enzyme IDs
        all_enzyme_ids = enzyme_df['enzyme_id'].tolist() if 'enzyme_id' in enzyme_df.columns else enzyme_df['enzyme'].tolist()
        all_variants = set(all_enzyme_ids)
        variants_with_data = set()
        all_results = []
        
        # If enzyme_df has campaign_id column, we can use it to filter
        has_campaign_info = 'campaign_id' in enzyme_df.columns
        
        # Process locations in order of confidence
        for location in locations:
            if len(variants_with_data) >= len(all_variants):
                LOGGER.info("All variants have data, stopping extraction")
                break
                
            LOGGER.info("\nProcessing location %s (confidence: %d%%)", 
                       location['location'], location.get('confidence', 0))
            
            # Extract metrics from this location for ALL enzymes
            metrics_rows = self.extract_metrics_batch(all_enzyme_ids, location['location'])
            
            # Filter to valid metrics
            valid_metrics = [m for m in metrics_rows if self._has_valid_metrics(m)]
            
            if not valid_metrics:
                LOGGER.warning("No valid metrics found in %s", location['location'])
                continue
                
            LOGGER.info("Found %d enzymes with data in %s", len(valid_metrics), location['location'])
            
            # Create DataFrame for this location
            df_location = pd.DataFrame(valid_metrics)
            
            # Track which variants we got data for
            new_variants = set(df_location['enzyme'].tolist()) - variants_with_data
            LOGGER.info("Found data for %d new variants in %s", len(new_variants), location['location'])
            variants_with_data.update(new_variants)
            
            # Determine which campaign/lineage this location represents
            # by checking which variants are present
            location_variants = set(df_location['enzyme'].tolist())
            
            # If we have campaign info, determine the campaign for this location
            campaign_id = None
            if has_campaign_info:
                # Find which campaign(s) these variants belong to
                if 'enzyme_id' in enzyme_df.columns:
                    variant_campaigns = enzyme_df[enzyme_df['enzyme_id'].isin(location_variants)]['campaign_id'].unique()
                else:
                    variant_campaigns = enzyme_df[enzyme_df['enzyme'].isin(location_variants)]['campaign_id'].unique()
                if len(variant_campaigns) == 1:
                    campaign_id = variant_campaigns[0]
                    LOGGER.info("Location %s contains variants from campaign: %s", 
                               location['location'], campaign_id)
                elif len(variant_campaigns) > 1:
                    LOGGER.warning("Location %s contains variants from multiple campaigns: %s", 
                                  location['location'], variant_campaigns)
            
            # Extract model reaction specific to this location/campaign
            location_context = f"Location: {location['location']}"
            if location.get('caption'):
                location_context += f"\nCaption: {location['caption']}"
            
            # First find model reaction locations for this campaign/enzyme group
            location_enzymes = df_location['enzyme'].unique().tolist()
            model_reaction_locations = self.find_model_reaction_locations(location_enzymes)
            
            # Try to find model reaction for this specific lineage, passing the locations
            location_model_reaction = self.find_lineage_model_reaction(
                location['location'], 
                location_context,
                model_reaction_locations
            )
            
            # Get full model reaction info with IUPAC names
            if location_model_reaction.get('substrate_ids') or location_model_reaction.get('product_ids'):
                model_info = self._extract_lineage_model_info(location_model_reaction)
            else:
                # Fall back to general model reaction extraction
                # Pass the enzyme variants from this location
                model_info = self.gather_model_reaction_info(location_enzymes)
            
            # Add model reaction info to all enzymes from this location
            for key, value in model_info.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value) if value else None
                df_location[key] = value
            
            # Add location and campaign info
            df_location['data_location'] = location['location']
            df_location['location_type'] = location.get('type', 'unknown')
            df_location['location_confidence'] = location.get('confidence', 0)
            # Remove lineage_group column - not working properly
            # df_location['lineage_group'] = location.get('lineage_hint', campaign_id or 'unknown')
            
            all_results.append(df_location)
            
            # Log progress
            LOGGER.info("Progress: %d/%d variants have data", 
                       len(variants_with_data), len(all_variants))
        
        if all_results:
            # Combine all results
            df_combined = pd.concat(all_results, ignore_index=True)
            
            # If we have duplicates (same variant in multiple locations), keep the one with highest confidence
            if df_combined.duplicated(subset=['enzyme']).any():
                LOGGER.info("Removing duplicates, keeping highest confidence data")
                df_combined = df_combined.sort_values(
                    ['enzyme', 'location_confidence'], 
                    ascending=[True, False]
                ).drop_duplicates(subset=['enzyme'], keep='first')
            
            # Log extraction summary
            LOGGER.info("Extraction complete: %d unique variants from %d locations", 
                       len(df_combined), len(all_results))
            
            if 'data_location' in df_combined.columns:
                for location in df_combined['data_location'].unique():
                    location_enzymes = df_combined[df_combined['data_location'] == location]
                    LOGGER.info("  - %s: %d enzymes", location, len(location_enzymes))
            
            return df_combined
        else:
            LOGGER.warning("No metrics extracted from any location")
            return pd.DataFrame()
    
    def _process_multiple_lineages(self, locations: List[Dict[str, Any]], 
                                  enzyme_df: pd.DataFrame, 
                                  lineage_analysis: Dict[str, Any]) -> pd.DataFrame:
        """Process multiple lineages where each location represents a different model reaction."""
        all_metrics = []
        lineage_groups = lineage_analysis.get('lineage_groups', [])
        
        # Get all enzyme IDs for extraction attempts
        all_enzyme_ids = enzyme_df['enzyme_id'].tolist() if 'enzyme_id' in enzyme_df.columns else []
        
        for group in lineage_groups:
            group_location = group.get('data_location')
            group_id = group.get('group_id')
            
            # Find the location info
            location_info = next((loc for loc in locations if loc['location'] == group_location), None)
            if not location_info:
                LOGGER.warning("No location info found for group %s at %s", group_id, group_location)
                continue
            
            LOGGER.info("Processing location %s (%s)", group_location, group_id)
            
            # Extract metrics from this location for ALL enzymes
            # The extractor will return only those that actually have data
            metrics_rows = self.extract_metrics_batch(all_enzyme_ids, group_location)
            
            # Filter to enzymes that actually had data in this location
            valid_metrics = [m for m in metrics_rows if self._has_valid_metrics(m)]
            
            if not valid_metrics:
                LOGGER.warning("No valid metrics found in %s", group_location)
                continue
                
            LOGGER.info("Found %d enzymes with data in %s", len(valid_metrics), group_location)
            
            # Create DataFrame for this location
            df_location = pd.DataFrame(valid_metrics)
            
            # Extract model reaction specific to this location
            # Different locations = different model reactions
            location_context = f"Location: {group_location}"
            if group.get('caption'):
                location_context += f"\nCaption: {group['caption']}"
            
            # First find model reaction locations for this enzyme group
            location_enzymes = df_location['enzyme'].unique().tolist() if 'enzyme' in df_location.columns else all_enzyme_ids
            model_reaction_locations = self.find_model_reaction_locations(location_enzymes)
            
            # Try to find model reaction for this specific lineage, passing the locations
            location_model_reaction = self.find_lineage_model_reaction(
                group_location, 
                location_context,
                model_reaction_locations
            )
            
            # Get full model reaction info with IUPAC names
            if location_model_reaction.get('substrate_ids') or location_model_reaction.get('product_ids'):
                model_info = self._extract_lineage_model_info(location_model_reaction)
            else:
                # Try to extract model reaction from this specific location
                # Pass the enzyme variants that have data in this location
                model_info = self.gather_model_reaction_info(location_enzymes)
            
            # Add model reaction info to all enzymes from this location
            for key, value in model_info.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value) if value else None
                df_location[key] = value
            
            # Add location identifier
            df_location['data_location'] = group_location
            # Remove lineage_group column - not working properly
            # df_location['lineage_group'] = group.get('lineage_hint', group_id)
            
            all_metrics.append(df_location)
        
        if all_metrics:
            # Combine all metrics
            df_combined = pd.concat(all_metrics, ignore_index=True)
            
            # Log extraction summary
            LOGGER.info("Extraction complete: %d total enzymes from %d locations", 
                       len(df_combined), len(all_metrics))
            
            if 'data_location' in df_combined.columns:
                for location in df_combined['data_location'].unique():
                    location_enzymes = df_combined[df_combined['data_location'] == location]
                    LOGGER.info("  - %s: %d enzymes", location, len(location_enzymes))
            
            return df_combined
        else:
            LOGGER.warning("No metrics extracted from any location")
            return pd.DataFrame()
    
    def _has_valid_metrics(self, metrics_row: Dict[str, Any]) -> bool:
        """Check if a metrics row contains any valid performance data."""
        metric_fields = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
        
        for field in metric_fields:
            if metrics_row.get(field) is not None:
                return True
                
        # Also check other_metrics
        if metrics_row.get('other_metrics') and isinstance(metrics_row['other_metrics'], dict):
            if metrics_row['other_metrics']:  # Non-empty dict
                return True
                
        return False
    
    def _filter_locations_by_campaign(self, locations: List[Dict[str, Any]], 
                                     enzyme_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Filter locations to only those relevant to the current campaign."""
        if not self.campaign_filter or 'campaign_id' not in enzyme_df.columns:
            return locations
        
        # Get enzyme names for this campaign
        campaign_enzymes = enzyme_df[enzyme_df['campaign_id'] == self.campaign_filter]['enzyme_id' if 'enzyme_id' in enzyme_df.columns else 'enzyme'].tolist()
        
        # Extract any common patterns from enzyme names
        enzyme_patterns = set()
        for enzyme in campaign_enzymes:
            # Extract any uppercase abbreviations (e.g., 'PYS', 'INS')
            matches = re.findall(r'[A-Z]{2,}', enzyme)
            enzyme_patterns.update(matches)
        
        LOGGER.info("Campaign %s has enzyme patterns: %s", self.campaign_filter, enzyme_patterns)
        
        # Get campaign description keywords from the campaign data if available
        campaign_keywords = set()
        # Extract keywords from campaign_id (e.g., 'pyrrolidine_synthase_evolution' -> ['pyrrolidine', 'synthase'])
        words = self.campaign_filter.lower().replace('_', ' ').split()
        # Filter out generic words
        generic_words = {'evolution', 'campaign', 'synthase', 'enzyme', 'variant'}
        campaign_keywords.update(word for word in words if word not in generic_words and len(word) > 3)
        
        LOGGER.info("Campaign keywords: %s", campaign_keywords)
        
        # Filter locations based on campaign clues
        filtered = []
        for loc in locations:
            # Check caption and clues for campaign indicators
            caption = (loc.get('caption') or '').lower()
            campaign_clues = (loc.get('campaign_clues') or '').lower()
            lineage_hint = (loc.get('lineage_hint') or '').lower()
            combined_text = caption + ' ' + campaign_clues + ' ' + lineage_hint
            
            # Check if location is relevant to this campaign
            is_relevant = False
            
            # Check for enzyme patterns
            for pattern in enzyme_patterns:
                if pattern.lower() in combined_text:
                    is_relevant = True
                    break
            
            # Check for campaign keywords
            if not is_relevant:
                for keyword in campaign_keywords:
                    if keyword in combined_text:
                        is_relevant = True
                        break
            
            # Check if any campaign enzymes are explicitly mentioned
            if not is_relevant:
                for enzyme in campaign_enzymes[:5]:  # Check first few enzymes
                    if enzyme.lower() in combined_text:
                        is_relevant = True
                        break
            
            if is_relevant:
                filtered.append(loc)
                LOGGER.info("Location %s is relevant to campaign %s", 
                           loc.get('location'), self.campaign_filter)
            else:
                LOGGER.debug("Location %s filtered out for campaign %s", 
                            loc.get('location'), self.campaign_filter)
        
        return filtered
    
    def _extract_lineage_model_info(self, lineage_reaction: Dict[str, Any]) -> Dict[str, Any]:
        """Extract full model reaction info including IUPAC names for a lineage."""
        # Get substrate/product IDs from lineage-specific extraction
        substrate_ids = lineage_reaction.get('substrate_ids', [])
        product_ids = lineage_reaction.get('product_ids', [])
        
        # Get general model reaction info for conditions
        general_info = self.gather_model_reaction_info()
        
        # Override substrate/product lists with lineage-specific ones only if they contain actual compound IDs
        model_info = general_info.copy()
        
        # Check if substrate_ids contain actual compound IDs (not generic terms like "alkyl azide")
        if substrate_ids and any(re.match(r'^[0-9]+[a-z]?$|^[A-Z][0-9]+$', sid) for sid in substrate_ids):
            model_info['substrate_list'] = substrate_ids
        elif not substrate_ids and general_info.get('substrate_list'):
            # Keep the general info if lineage extraction found nothing
            pass
        else:
            model_info['substrate_list'] = substrate_ids
            
        # Check if product_ids contain actual compound IDs (not generic terms like "pyrrolidine")
        if product_ids and any(re.match(r'^[0-9]+[a-z]?$|^[A-Z][0-9]+$', pid) for pid in product_ids):
            model_info['product_list'] = product_ids
        elif not product_ids and general_info.get('product_list'):
            # Keep the general info if lineage extraction found nothing
            pass
        else:
            # If we only have generic terms, try to keep general info if available
            if general_info.get('product_list') and all(len(pid) > 5 for pid in product_ids):
                # Likely generic terms like "pyrrolidine", keep general info
                pass
            else:
                model_info['product_list'] = product_ids
        
        # Extract IUPAC names for the compounds we're actually using
        # Use the IDs from model_info (which may have been preserved from general extraction)
        final_substrate_ids = model_info.get('substrate_list', [])
        final_product_ids = model_info.get('product_list', [])
        all_compound_ids = final_substrate_ids + final_product_ids
        
        if all_compound_ids:
            compound_mappings = self._extract_compound_mappings_adaptive(all_compound_ids)
            
            # Map substrate IUPAC names
            substrate_iupacs = []
            for sid in final_substrate_ids:
                mapping = compound_mappings.get(str(sid).lower().strip())
                if mapping and mapping.iupac_name:
                    substrate_iupacs.append(mapping.iupac_name)
            # Only update if we found IUPAC names
            if substrate_iupacs:
                model_info['substrate_iupac_list'] = substrate_iupacs
            
            # Map product IUPAC names
            product_iupacs = []
            for pid in final_product_ids:
                mapping = compound_mappings.get(str(pid).lower().strip())
                if mapping and mapping.iupac_name:
                    product_iupacs.append(mapping.iupac_name)
            # Only update if we found IUPAC names
            if product_iupacs:
                model_info['product_iupac_list'] = product_iupacs
        
        return model_info
    
    def _process_single_lineage_by_confidence(self, locations: List[Dict[str, Any]], 
                                             enzyme_df: pd.DataFrame) -> pd.DataFrame:
        """Process single lineage by confidence, stopping when all variants have data."""
        # Get list of all variants we need data for
        all_variants = set(enzyme_df['enzyme'].tolist() if 'enzyme' in enzyme_df.columns else 
                          enzyme_df['enzyme_id'].tolist())
        variants_with_data = set()
        all_results = []
        
        # Process locations in order of confidence
        for location in locations:
            if len(variants_with_data) >= len(all_variants):
                LOGGER.info("All variants have data, stopping extraction")
                break
                
            LOGGER.info("\nProcessing location %s (confidence: %d%%)", 
                       location['location'], location.get('confidence', 0))
            
            # Extract metrics from this location
            metrics_rows = self.extract_metrics_batch(list(all_variants), location['location'])
            
            # Filter to valid metrics
            valid_metrics = [m for m in metrics_rows if self._has_valid_metrics(m)]
            
            if not valid_metrics:
                LOGGER.warning("No valid metrics found in %s", location['location'])
                continue
            
            # Create DataFrame for this location
            df_location = pd.DataFrame(valid_metrics)
            
            # Track which variants we got data for
            new_variants = set(df_location['enzyme'].tolist()) - variants_with_data
            LOGGER.info("Found data for %d new variants in %s", len(new_variants), location['location'])
            variants_with_data.update(new_variants)
            
            # Add location info
            df_location['data_location'] = location['location']
            df_location['location_type'] = location.get('type', 'unknown')
            df_location['location_confidence'] = location.get('confidence', 0)
            
            all_results.append(df_location)
            
            # Log progress
            LOGGER.info("Progress: %d/%d variants have data", 
                       len(variants_with_data), len(all_variants))
        
        if all_results:
            # Combine all results
            df_combined = pd.concat(all_results, ignore_index=True)
            
            # If we have duplicates (same variant in multiple locations), keep the one with highest confidence
            if df_combined.duplicated(subset=['enzyme']).any():
                LOGGER.info("Removing duplicates, keeping highest confidence data")
                df_combined = df_combined.sort_values(
                    ['enzyme', 'location_confidence'], 
                    ascending=[True, False]
                ).drop_duplicates(subset=['enzyme'], keep='first')
            
            # Extract model reaction info once
            # Pass the enzyme variants we're processing
            enzyme_list = df_combined['enzyme'].unique().tolist()
            model_info = self.gather_model_reaction_info(enzyme_list)
            
            # Add model reaction info to all rows
            for key, value in model_info.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value) if value else None
                df_combined[key] = value
            
            LOGGER.info("Extraction complete: %d unique variants with data", len(df_combined))
            
            return df_combined
        else:
            LOGGER.warning("No metrics extracted from any location")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # 6.5 Public orchestrator
    # ------------------------------------------------------------------

    def run(self, enzyme_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        # This module should always have enzyme CSV provided
        if enzyme_df is None:
            LOGGER.error("No enzyme DataFrame provided - this module requires enzyme CSV input")
            return pd.DataFrame()
        
        # Check if we have campaign_id column - if so, process each campaign separately
        if 'campaign_id' in enzyme_df.columns and not self.campaign_filter:
            campaigns = enzyme_df['campaign_id'].unique()
            if len(campaigns) > 1:
                LOGGER.info("Detected %d campaigns in enzyme data - processing each separately", len(campaigns))
                all_campaign_results = []
                
                for campaign_id in campaigns:
                    LOGGER.info("\n" + "="*60)
                    LOGGER.info("Processing campaign: %s", campaign_id)
                    LOGGER.info("="*60)
                    
                    # Create a new extractor instance for this campaign
                    campaign_extractor = ReactionExtractor(
                        manuscript=self.manuscript,
                        si=self.si,
                        cfg=self.cfg,
                        debug_dir=self.debug_dir / campaign_id if self.debug_dir else None,
                        campaign_filter=campaign_id
                    )
                    
                    # Run extraction for this campaign
                    campaign_df = campaign_extractor.run(enzyme_df)
                    
                    if not campaign_df.empty:
                        # Add campaign identifier
                        campaign_df['campaign_id'] = campaign_id
                        all_campaign_results.append(campaign_df)
                        LOGGER.info("Extracted %d reactions for campaign %s", len(campaign_df), campaign_id)
                
                # Combine results from all campaigns
                if all_campaign_results:
                    combined_df = pd.concat(all_campaign_results, ignore_index=True)
                    LOGGER.info("\nCombined extraction complete: %d total reactions across %d campaigns", 
                               len(combined_df), len(campaigns))
                    return combined_df
                else:
                    LOGGER.warning("No reactions extracted from any campaign")
                    return pd.DataFrame()
        
        # Filter by campaign if specified
        if self.campaign_filter and 'campaign_id' in enzyme_df.columns:
            LOGGER.info("Filtering enzymes for campaign: %s", self.campaign_filter)
            enzyme_df = enzyme_df[enzyme_df['campaign_id'] == self.campaign_filter].copy()
            LOGGER.info("Found %d enzymes for campaign %s", len(enzyme_df), self.campaign_filter)
            if len(enzyme_df) == 0:
                LOGGER.warning("No enzymes found for campaign %s", self.campaign_filter)
                return pd.DataFrame()
        
        # Find all locations with performance data
        locations = self.find_reaction_locations()
        if not locations:
            LOGGER.error("Failed to find reaction data locations")
            return pd.DataFrame()
        
        # Filter locations by campaign if specified
        if self.campaign_filter:
            filtered_locations = self._filter_locations_by_campaign(locations, enzyme_df)
            if filtered_locations:
                LOGGER.info("Filtered to %d locations for campaign %s", 
                           len(filtered_locations), self.campaign_filter)
                locations = filtered_locations
            else:
                LOGGER.warning("No locations found specifically for campaign %s, using all locations", 
                             self.campaign_filter)
        
        # Sort locations by confidence (highest first) and prefer tables over figures
        locations_sorted = sorted(locations, key=lambda x: (
            x.get('confidence', 0),
            1 if x.get('type') == 'table' else 0  # Prefer tables when confidence is equal
        ), reverse=True)
        
        LOGGER.info("Found %d reaction data location(s), sorted by confidence:", len(locations_sorted))
        for loc in locations_sorted:
            LOGGER.info("  - %s (%s, confidence: %d%%)", 
                       loc.get('location'), 
                       loc.get('type'),
                       loc.get('confidence', 0))
            
        # Analyze if we have multiple lineages
        lineage_analysis = self.analyze_lineage_groups(locations_sorted, enzyme_df)
        has_multiple_lineages = lineage_analysis.get('has_multiple_lineages', False)
        
        if has_multiple_lineages:
            LOGGER.info("Multiple lineage groups detected")
            return self._process_multiple_lineages_by_confidence(locations_sorted, enzyme_df, lineage_analysis)
        else:
            LOGGER.info("Single lineage detected, using confidence-based processing")
            return self._process_single_lineage_by_confidence(locations_sorted, enzyme_df)

###############################################################################
# 7 - MERGE WITH LINEAGE CSV + SAVE
###############################################################################

def merge_with_lineage_data(
    df_lineage: pd.DataFrame, df_metrics: pd.DataFrame
) -> pd.DataFrame:
    """Outer-merge on 'enzyme' column. Left CSV defines desired row order."""
    
    # Handle both 'enzyme' and 'enzyme_id' column names
    if "enzyme_id" in df_lineage.columns and "enzyme" not in df_lineage.columns:
        df_lineage = df_lineage.rename(columns={"enzyme_id": "enzyme"})
    
    if "enzyme" not in df_lineage.columns:
        raise ValueError("Lineage CSV must have an 'enzyme' or 'enzyme_id' column.")
    
    merged = df_lineage.merge(df_metrics, on="enzyme", how="left")
    return merged

###############################################################################
# 8 - CLI ENTRY-POINT
###############################################################################

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract enzyme reaction metrics from chemistry PDFs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, type=Path)
    p.add_argument("--si", type=Path, help="Supporting-information PDF")
    p.add_argument("--lineage-csv", type=Path)
    p.add_argument("--output", type=Path, default=Path("reaction_metrics.csv"))
    p.add_argument("--verbose", action="store_true")
    p.add_argument(
        "--debug-dir",
        metavar="DIR",
        help="Write ALL intermediate artefacts (prompts, raw Gemini replies) to DIR",
    )
    return p

def main() -> None:
    args = build_parser().parse_args()
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    cfg = Config()
    extractor = ReactionExtractor(args.manuscript, args.si, cfg, debug_dir=args.debug_dir)
    
    # Load enzyme data from CSV if provided
    enzyme_df = None
    if args.lineage_csv and args.lineage_csv.exists():
        LOGGER.info("Loading enzyme data from CSV…")
        enzyme_df = pd.read_csv(args.lineage_csv)
    
    # Run extraction with enzyme data
    df_metrics = extractor.run(enzyme_df)

    if args.lineage_csv and args.lineage_csv.exists() and not df_metrics.empty:
        LOGGER.info("Merging with lineage CSV…")
        df_final = merge_with_lineage_data(enzyme_df, df_metrics)
    else:
        df_final = df_metrics

    df_final.to_csv(args.output, index=False)
    LOGGER.info("Saved %d rows -> %s", len(df_final), args.output)

if __name__ == "__main__":
    main()

