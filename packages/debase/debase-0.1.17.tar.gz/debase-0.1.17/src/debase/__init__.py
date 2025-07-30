"""DEBase - Enzyme lineage analysis and sequence extraction package."""

from ._version import __version__

from .enzyme_lineage_extractor import run_pipeline as extract_lineage
from .cleanup_sequence import main as cleanup_sequences
from .reaction_info_extractor import ReactionExtractor
from .substrate_scope_extractor import run_pipeline as extract_substrate_scope
from .lineage_format import run_pipeline as format_lineage

__all__ = [
    "__version__",
    "extract_lineage",
    "cleanup_sequences",
    "ReactionExtractor",
    "extract_substrate_scope",
    "format_lineage",
]