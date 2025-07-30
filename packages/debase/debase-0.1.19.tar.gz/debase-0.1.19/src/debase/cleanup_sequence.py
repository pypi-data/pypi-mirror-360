#!/usr/bin/env python3
"""
cleanup_sequence_structured.py - Enhanced protein sequence generator from mutations

This module takes the output from enzyme_lineage_extractor and generates complete
protein sequences by applying mutations throughout the lineage tree.

Usage:
    python cleanup_sequence_structured.py input.csv output.csv
"""

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd


# === 1. CONFIGURATION & CONSTANTS === ----------------------------------------

VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY*")  # Include * for stop codons

# Configure module logger
log = logging.getLogger(__name__)


# === 2. DATA MODELS === ------------------------------------------------------

@dataclass
class Mutation:
    """Represents a single point mutation."""
    original: str
    position: int
    replacement: str
    
    def __str__(self) -> str:
        return f"{self.original}{self.position}{self.replacement}"


@dataclass
class ComplexMutation:
    """Represents complex mutations like C-terminal modifications."""
    replacement_seq: str
    start_pos: int
    end_pos: int
    extension_seq: str = ""
    has_stop: bool = False
    
    def __str__(self) -> str:
        result = f"{self.replacement_seq}({self.start_pos}-{self.end_pos})"
        if self.extension_seq:
            result += self.extension_seq
        if self.has_stop:
            result += "[STOP]"
        return result


@dataclass
class Variant:
    """Enhanced variant representation with sequence information."""
    enzyme_id: str
    parent_enzyme_id: Optional[str]
    mutations: str
    protein_sequence: Optional[str] = None
    generation: Optional[int] = None
    flag: str = ""
    
    @property
    def has_sequence(self) -> bool:
        return bool(self.protein_sequence and self.protein_sequence.strip())
    
    @property
    def has_complex_mutations(self) -> bool:
        return "complex_mutation" in self.flag


@dataclass
class SequenceGenerationResult:
    """Result of sequence generation attempt."""
    sequence: str
    method: str  # "from_parent", "from_child", "from_ancestor", "from_descendant"
    source_id: str
    confidence: float = 1.0
    notes: str = ""


# === 3. MUTATION PARSING === -------------------------------------------------

class MutationParser:
    """Handles parsing of various mutation formats."""
    
    POINT_MUTATION_PATTERN = re.compile(r"^([A-Za-z\*])([0-9]+)([A-Za-z\*])$")
    COMPLEX_C_TERMINAL_PATTERN = re.compile(r'([A-Z]+)\((\d+)-(\d+)\)([A-Z]*)\[STOP\]')
    COMPLEX_C_TERMINAL_NO_STOP = re.compile(r'([A-Z]+)\((\d+)-(\d+)\)([A-Z]+)')
    
    @classmethod
    def parse_mutations(cls, mutation_str: str) -> List[Mutation]:
        """Parse standard point mutations from a mutation string."""
        if not mutation_str or mutation_str.strip() == "":
            return []
        
        mutations = []
        for mut_str in mutation_str.split(','):
            mut_str = mut_str.strip()
            if not mut_str:
                continue
                
            match = cls.POINT_MUTATION_PATTERN.match(mut_str)
            if match:
                try:
                    orig, pos_str, new = match.groups()
                    mutations.append(Mutation(
                        original=orig.upper(),
                        position=int(pos_str),
                        replacement=new.upper()
                    ))
                except ValueError as e:
                    log.warning(f"Failed to parse mutation '{mut_str}': {e}")
        
        return mutations
    
    @classmethod
    def parse_complex_c_terminal(cls, mutation_str: str) -> Optional[ComplexMutation]:
        """Parse complex C-terminal mutations."""
        # Try pattern with [STOP]
        match = cls.COMPLEX_C_TERMINAL_PATTERN.search(mutation_str)
        if match:
            return ComplexMutation(
                replacement_seq=match.group(1),
                start_pos=int(match.group(2)),
                end_pos=int(match.group(3)),
                extension_seq=match.group(4),
                has_stop=True
            )
        
        # Try pattern without [STOP]
        match = cls.COMPLEX_C_TERMINAL_NO_STOP.search(mutation_str)
        if match:
            return ComplexMutation(
                replacement_seq=match.group(1),
                start_pos=int(match.group(2)),
                end_pos=int(match.group(3)),
                extension_seq=match.group(4),
                has_stop=False
            )
        
        return None
    
    @classmethod
    def detect_complex_mutations(cls, mutation_str: str) -> List[str]:
        """Detect non-standard mutations in the mutation string."""
        if not mutation_str or mutation_str.strip() == "":
            return []
        
        all_muts = [m.strip() for m in mutation_str.split(',') if m.strip()]
        std_muts = {str(m) for m in cls.parse_mutations(mutation_str)}
        
        return [m for m in all_muts if m not in std_muts]


# === 4. SEQUENCE MANIPULATION === --------------------------------------------

class SequenceManipulator:
    """Handles application and reversal of mutations on sequences."""
    
    @staticmethod
    def validate_sequence(seq: str) -> bool:
        """Validate that a sequence contains only valid amino acids."""
        return all(aa in VALID_AMINO_ACIDS for aa in seq.upper())
    
    @staticmethod
    def determine_indexing(parent_seq: str, mutations: List[Mutation]) -> int:
        """Determine whether mutations use 0-based or 1-based indexing."""
        if not mutations or not parent_seq:
            return 1  # Default to 1-based
        
        # Count matches for each indexing scheme
        zero_matches = sum(
            1 for m in mutations 
            if 0 <= m.position < len(parent_seq) and 
            parent_seq[m.position].upper() == m.original.upper()
        )
        one_matches = sum(
            1 for m in mutations 
            if 0 <= m.position - 1 < len(parent_seq) and 
            parent_seq[m.position - 1].upper() == m.original.upper()
        )
        
        return 0 if zero_matches >= one_matches else 1
    
    @classmethod
    def apply_mutations(cls, parent_seq: str, mutation_str: str) -> str:
        """Apply mutations to a parent sequence."""
        if not parent_seq:
            return ""
        
        seq = list(parent_seq)
        
        # Apply point mutations
        mutations = MutationParser.parse_mutations(mutation_str)
        if mutations:
            idx_offset = cls.determine_indexing(parent_seq, mutations)
            
            for mut in mutations:
                idx = mut.position - idx_offset
                # Try primary index
                if 0 <= idx < len(seq) and seq[idx].upper() == mut.original.upper():
                    seq[idx] = mut.replacement
                else:
                    # Try alternate index
                    alt_idx = mut.position - (1 - idx_offset)
                    if 0 <= alt_idx < len(seq) and seq[alt_idx].upper() == mut.original.upper():
                        seq[alt_idx] = mut.replacement
                    else:
                        log.warning(
                            f"Mutation {mut} does not match parent sequence at "
                            f"position {mut.position} (tried both 0- and 1-based indexing)"
                        )
        
        # Apply complex C-terminal mutations
        complex_mut = MutationParser.parse_complex_c_terminal(mutation_str)
        if complex_mut:
            log.info(f"Applying complex C-terminal mutation: {complex_mut}")
            
            # Convert to 0-indexed
            start_idx = complex_mut.start_pos - 1
            end_idx = complex_mut.end_pos - 1
            
            if 0 <= start_idx <= end_idx < len(seq):
                # Replace the specified region
                seq[start_idx:end_idx + 1] = list(complex_mut.replacement_seq)
                
                # Handle STOP codon
                if complex_mut.has_stop:
                    seq = seq[:start_idx + len(complex_mut.replacement_seq)]
                
                # Add extension if present
                if complex_mut.extension_seq:
                    seq.extend(list(complex_mut.extension_seq))
            else:
                log.warning(
                    f"Invalid C-terminal mutation positions: {complex_mut.start_pos}-"
                    f"{complex_mut.end_pos} for sequence of length {len(seq)}"
                )
        
        return "".join(seq)
    
    @classmethod
    def reverse_mutations(cls, child_seq: str, mutation_str: str) -> str:
        """Reverse mutations to get parent sequence from child."""
        if not child_seq:
            return ""
        
        seq = list(child_seq)
        mutations = MutationParser.parse_mutations(mutation_str)
        
        if not mutations:
            return child_seq
        
        # Determine indexing by checking which positions have the "new" amino acid
        zero_matches = sum(
            1 for m in mutations 
            if 0 <= m.position < len(child_seq) and 
            child_seq[m.position].upper() == m.replacement.upper()
        )
        one_matches = sum(
            1 for m in mutations 
            if 0 <= m.position - 1 < len(child_seq) and 
            child_seq[m.position - 1].upper() == m.replacement.upper()
        )
        
        idx_offset = 0 if zero_matches >= one_matches else 1
        
        # Reverse mutations (change replacement -> original)
        for mut in mutations:
            idx = mut.position - idx_offset
            if 0 <= idx < len(seq) and seq[idx].upper() == mut.replacement.upper():
                seq[idx] = mut.original
            else:
                alt_idx = mut.position - (1 - idx_offset)
                if 0 <= alt_idx < len(seq) and seq[alt_idx].upper() == mut.replacement.upper():
                    seq[alt_idx] = mut.original
                else:
                    log.warning(
                        f"Cannot reverse mutation {mut}: replacement amino acid "
                        f"not found at expected position"
                    )
        
        return "".join(seq)


# === 5. LINEAGE NAVIGATION === -----------------------------------------------

class LineageNavigator:
    """Handles navigation through the enzyme lineage tree."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._build_relationships()
    
    def _build_relationships(self) -> None:
        """Build parent-child relationship mappings."""
        self.parent_to_children: Dict[str, List[str]] = {}
        self.child_to_parent: Dict[str, str] = {}
        
        for _, row in self.df.iterrows():
            child_id = row["enzyme_id"]
            parent_id = row.get("parent_enzyme_id")
            
            if parent_id:
                self.child_to_parent[child_id] = parent_id
                if parent_id not in self.parent_to_children:
                    self.parent_to_children[parent_id] = []
                self.parent_to_children[parent_id].append(child_id)
    
    def get_ancestors(self, variant_id: str) -> List[str]:
        """Get all ancestors of a variant in order (immediate parent first)."""
        ancestors = []
        current_id = self.child_to_parent.get(variant_id)
        
        while current_id:
            ancestors.append(current_id)
            current_id = self.child_to_parent.get(current_id)
        
        return ancestors
    
    def get_descendants(self, variant_id: str) -> List[str]:
        """Get all descendants of a variant (breadth-first order)."""
        descendants = []
        queue = [variant_id]
        visited = {variant_id}
        
        while queue:
            current_id = queue.pop(0)
            children = self.parent_to_children.get(current_id, [])
            
            for child in children:
                if child not in visited:
                    visited.add(child)
                    descendants.append(child)
                    queue.append(child)
        
        return descendants
    
    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Find path between two variants if one exists."""
        # Check if to_id is descendant of from_id
        descendants = self.get_descendants(from_id)
        if to_id in descendants:
            # Build path forward
            path = [from_id]
            current = from_id
            
            while current != to_id:
                # Find child that leads to to_id
                for child in self.parent_to_children.get(current, []):
                    if child == to_id or to_id in self.get_descendants(child):
                        path.append(child)
                        current = child
                        break
            
            return path
        
        # Check if to_id is ancestor of from_id
        ancestors = self.get_ancestors(from_id)
        if to_id in ancestors:
            # Build path backward
            path = [from_id]
            current = from_id
            
            while current != to_id:
                parent = self.child_to_parent.get(current)
                if parent:
                    path.append(parent)
                    current = parent
                else:
                    break
            
            return path
        
        return None


# === 6. SEQUENCE GENERATOR === -----------------------------------------------

class SequenceGenerator:
    """Main class for generating protein sequences from mutations."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.navigator = LineageNavigator(df)
        self.manipulator = SequenceManipulator()
        self._update_ground_truths()
    
    def _update_ground_truths(self) -> None:
        """Update the set of variants with known sequences."""
        self.ground_truth_ids = set(
            self.df[
                self.df["protein_sequence"].notna() & 
                (self.df["protein_sequence"].str.strip() != "")
            ]["enzyme_id"]
        )
    
    def find_best_ground_truth(
        self, 
        variant_id: str, 
        has_complex_mutation: bool
    ) -> Tuple[str, str]:
        """
        Find the best ground truth sequence to use for generation.
        
        Returns:
            (ground_truth_id, direction) where direction is 'up' or 'down'
        """
        # Get variant info
        variant_row = self.df[self.df["enzyme_id"] == variant_id].iloc[0]
        parent_id = variant_row.get("parent_enzyme_id")
        
        # Check direct parent
        if parent_id in self.ground_truth_ids:
            if not has_complex_mutation:
                return parent_id, "up"
        
        # Check direct children
        direct_children = self.navigator.parent_to_children.get(variant_id, [])
        child_gts = [c for c in direct_children if c in self.ground_truth_ids]
        
        if child_gts:
            if has_complex_mutation:
                return child_gts[0], "down"
            elif parent_id not in self.ground_truth_ids:
                return child_gts[0], "down"
        
        # Check all descendants
        descendants = self.navigator.get_descendants(variant_id)
        desc_gts = [d for d in descendants if d in self.ground_truth_ids]
        
        # Check all ancestors
        ancestors = self.navigator.get_ancestors(variant_id)
        anc_gts = [a for a in ancestors if a in self.ground_truth_ids]
        
        # Prioritize based on mutation type
        if has_complex_mutation and desc_gts:
            return desc_gts[0], "down"
        
        if has_complex_mutation and parent_id in self.ground_truth_ids:
            return parent_id, "up"
        
        # Return closest ground truth
        if anc_gts:
            return anc_gts[0], "up"
        if desc_gts:
            return desc_gts[0], "down"
        
        return "", ""
    
    def generate_from_parent(
        self, 
        variant_id: str, 
        parent_id: str
    ) -> Optional[SequenceGenerationResult]:
        """Generate sequence by applying mutations to parent."""
        parent_row = self.df[self.df["enzyme_id"] == parent_id].iloc[0]
        parent_seq = parent_row.get("protein_sequence", "")
        
        if not parent_seq:
            return None
        
        variant_row = self.df[self.df["enzyme_id"] == variant_id].iloc[0]
        mutations = variant_row.get("mutations", "")
        
        if not mutations:
            return None
        
        sequence = self.manipulator.apply_mutations(parent_seq, mutations)
        
        return SequenceGenerationResult(
            sequence=sequence,
            method="from_parent",
            source_id=parent_id,
            confidence=1.0
        )
    
    def generate_from_child(
        self, 
        variant_id: str, 
        child_id: str
    ) -> Optional[SequenceGenerationResult]:
        """Generate sequence by reversing mutations from child."""
        child_row = self.df[self.df["enzyme_id"] == child_id].iloc[0]
        child_seq = child_row.get("protein_sequence", "")
        child_mutations = child_row.get("mutations", "")
        
        if not child_seq or not child_mutations:
            return None
        
        sequence = self.manipulator.reverse_mutations(child_seq, child_mutations)
        
        return SequenceGenerationResult(
            sequence=sequence,
            method="from_child",
            source_id=child_id,
            confidence=0.9
        )
    
    def generate_sequence(self, variant_id: str) -> Optional[SequenceGenerationResult]:
        """Generate sequence for a variant using the best available method."""
        # Check if already has sequence
        variant_row = self.df[self.df["enzyme_id"] == variant_id].iloc[0]
        if variant_row.get("protein_sequence", "").strip():
            return SequenceGenerationResult(
                sequence=variant_row["protein_sequence"],
                method="existing",
                source_id=variant_id,
                confidence=1.0
            )
        
        # Get variant info
        parent_id = variant_row.get("parent_enzyme_id")
        mutations = variant_row.get("mutations", "")
        
        # Check for complex mutations
        complex_muts = MutationParser.detect_complex_mutations(mutations) if mutations else []
        has_complex = bool(complex_muts)
        
        # Find best ground truth
        gt_id, direction = self.find_best_ground_truth(variant_id, has_complex)
        
        if not gt_id:
            log.warning(f"No suitable ground truth found for {variant_id}")
            return None
        
        log.info(f"Using {gt_id} as ground truth ({direction} direction) for {variant_id}")
        
        # Generate based on direction
        if direction == "up" and parent_id and mutations:
            if gt_id == parent_id:
                return self.generate_from_parent(variant_id, parent_id)
            else:
                # Non-direct ancestor - less reliable
                result = self.generate_from_parent(variant_id, gt_id)
                if result:
                    result.confidence = 0.7
                    result.notes = "Generated from non-direct ancestor"
                return result
        else:  # down or no parent/mutations
            direct_children = self.navigator.parent_to_children.get(variant_id, [])
            if gt_id in direct_children:
                return self.generate_from_child(variant_id, gt_id)
            else:
                # Try to find path through direct child
                path = self.navigator.find_path(variant_id, gt_id)
                if path and len(path) > 1:
                    direct_child = path[1]
                    result = self.generate_from_child(variant_id, direct_child)
                    if result:
                        result.confidence = 0.8
                        result.notes = f"Generated via path through {direct_child}"
                    return result
        
        return None


# === 7. MAIN PROCESSOR === ---------------------------------------------------

class SequenceProcessor:
    """Main processor for handling the complete workflow."""
    
    def __init__(self, input_csv: Path, output_csv: Path):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.df = None
        self.generator = None
    
    def load_data(self) -> None:
        """Load and prepare the input data."""
        self.df = pd.read_csv(self.input_csv, keep_default_na=False)
        
        # Detect and handle column format automatically
        self._normalize_columns()
        
        log.info(
            f"Loaded {len(self.df)} rows, "
            f"{sum(self.df['protein_sequence'].str.strip() == '')} empty sequences"
        )
        
        # Ensure required columns exist
        if "flag" not in self.df.columns:
            self.df["flag"] = ""
        
        # Initialize generator
        self.generator = SequenceGenerator(self.df)
    
    def _normalize_columns(self) -> None:
        """Automatically detect and normalize column names from different formats."""
        # Check if this is enzyme_lineage_extractor format
        if "variant_id" in self.df.columns:
            log.info("Detected enzyme_lineage_extractor format, converting columns...")
            
            # Rename columns
            column_mapping = {
                "variant_id": "enzyme_id",
                "parent_id": "parent_enzyme_id",
                "aa_seq": "protein_sequence"
            }
            
            self.df = self.df.rename(columns=column_mapping)
            
            # Convert mutation format from semicolon to comma-separated
            if "mutations" in self.df.columns:
                self.df["mutations"] = self.df["mutations"].str.replace(";", ",")
            
            log.info("Column conversion complete")
        
        # Verify required columns exist
        required_columns = ["enzyme_id", "parent_enzyme_id", "mutations", "protein_sequence"]
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Found columns: {list(self.df.columns)}"
            )
    
    def flag_complex_mutations(self) -> None:
        """Flag variants with complex mutations."""
        complex_count = 0
        
        for idx, row in self.df.iterrows():
            if row.get("mutations", ""):
                complex_muts = MutationParser.detect_complex_mutations(row["mutations"])
                if complex_muts:
                    self.df.at[idx, "flag"] = "complex_mutation"
                    complex_count += 1
                    log.info(
                        f"Variant {row['enzyme_id']} has complex mutations: {complex_muts}"
                    )
        
        log.info(f"Flagged {complex_count} variants with complex mutations")
    
    def process_simple_mutations(self) -> None:
        """Process variants with simple point mutations."""
        processed = 0
        
        for idx, row in self.df.iterrows():
            # Skip if already has sequence or has complex mutations
            if (row.get("protein_sequence", "").strip() or 
                "complex_mutation" in str(row.get("flag", ""))):
                continue
            
            variant_id = row["enzyme_id"]
            result = self.generator.generate_sequence(variant_id)
            
            if result and result.method == "from_parent":
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Check for unexpected length changes
                parent_seq = self.df[
                    self.df["enzyme_id"] == result.source_id
                ]["protein_sequence"].iloc[0]
                
                if len(result.sequence) != len(parent_seq):
                    self.df.at[idx, "flag"] = "unexpected_length_change"
                    log.warning(
                        f"Unexpected length change for {variant_id} "
                        f"with standard mutations"
                    )
                
                processed += 1
        
        log.info(f"Processed {processed} variants with simple mutations")
    
    def process_complex_mutations(self) -> None:
        """Process variants with complex mutations."""
        complex_variants = self.df[
            self.df["flag"].str.contains("complex_mutation", na=False)
        ]["enzyme_id"].tolist()
        
        log.info(f"Processing {len(complex_variants)} variants with complex mutations")
        
        processed = 0
        for variant_id in complex_variants:
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Check length changes
                parent_id = self.df.at[idx, "parent_enzyme_id"]
                parent_row = self.df[self.df["enzyme_id"] == parent_id]
                
                if not parent_row.empty and parent_row.iloc[0]["protein_sequence"]:
                    parent_seq = parent_row.iloc[0]["protein_sequence"]
                    if len(result.sequence) != len(parent_seq):
                        self.df.at[idx, "flag"] = "complex_mutation length_change"
                        log.info(
                            f"Length change for {variant_id}: "
                            f"{len(parent_seq)} -> {len(result.sequence)}"
                        )
                
                processed += 1
        
        log.info(f"Processed {processed} complex mutation variants")
    
    def process_remaining(self) -> None:
        """Process any remaining variants."""
        # Update ground truths with newly generated sequences
        self.generator._update_ground_truths()
        
        remaining = self.df[
            self.df["protein_sequence"].str.strip() == ""
        ]["enzyme_id"].tolist()
        
        if not remaining:
            return
        
        log.info(f"Processing {len(remaining)} remaining variants")
        
        # Sort by generation if available
        if "generation" in self.df.columns:
            remaining.sort(
                key=lambda x: self.df[
                    self.df["enzyme_id"] == x
                ]["generation"].iloc[0] if x in self.df["enzyme_id"].values else float('inf')
            )
        
        processed = 0
        for variant_id in remaining:
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Add generation method to flag
                method_flag = f"generated_{result.method}"
                if result.confidence < 1.0:
                    method_flag += f"_conf{result.confidence:.1f}"
                
                existing_flag = self.df.at[idx, "flag"]
                self.df.at[idx, "flag"] = f"{existing_flag} {method_flag}".strip()
                
                processed += 1
                
                # Update ground truths for next iterations
                self.generator._update_ground_truths()
        
        log.info(f"Processed {processed} remaining variants")
    
    def backward_pass(self) -> None:
        """Work backward from terminal variants to fill remaining gaps."""
        missing = self.df[
            self.df["protein_sequence"].str.strip() == ""
        ]["enzyme_id"].tolist()
        
        if not missing:
            return
        
        log.info(
            f"Backward pass: attempting to fill {len(missing)} remaining sequences"
        )
        
        # Find terminal variants (no children) with sequences
        all_parents = set(self.df["parent_enzyme_id"].dropna())
        terminal_variants = [
            v for v in self.generator.ground_truth_ids 
            if v not in all_parents
        ]
        
        log.info(f"Found {len(terminal_variants)} terminal variants with sequences")
        
        # Sort missing by generation (latest first)
        if "generation" in self.df.columns:
            missing.sort(
                key=lambda x: self.df[
                    self.df["enzyme_id"] == x
                ]["generation"].iloc[0] if x in self.df["enzyme_id"].values else 0,
                reverse=True
            )
        
        processed = 0
        for variant_id in missing:
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                self.df.at[idx, "flag"] += " backward_from_terminal"
                processed += 1
                
                # Update ground truths
                self.generator._update_ground_truths()
        
        log.info(f"Backward pass: filled {processed} sequences")
    
    def save_results(self) -> None:
        """Save the processed data."""
        # Final statistics
        empty_final = sum(self.df["protein_sequence"].str.strip() == "")
        length_changes = sum(self.df["flag"].str.contains("length_change", na=False))
        complex_mutations = sum(self.df["flag"].str.contains("complex_mutation", na=False))
        
        log.info(
            f"Final results: {len(self.df)} rows, {empty_final} empty, "
            f"{complex_mutations} complex mutations, {length_changes} length changes"
        )
        
        # Save to CSV
        self.df.to_csv(self.output_csv, index=False)
        log.info(f"Saved results to {self.output_csv}")
    
    def run(self) -> None:
        """Run the complete processing pipeline."""
        log.info("Starting sequence generation pipeline")
        
        # Load data
        self.load_data()
        
        # Flag complex mutations
        self.flag_complex_mutations()
        
        # Process in order
        self.process_simple_mutations()
        self.process_complex_mutations()
        self.process_remaining()
        self.backward_pass()
        
        # Save results
        self.save_results()
        
        log.info("Pipeline completed")


# === 8. CLI INTERFACE === ----------------------------------------------------

def setup_logging(verbose: int = 0) -> None:
    """Configure logging based on verbosity level."""
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(argv: Optional[List[str]] = None) -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cleanup_sequence_structured",
        description="Generate protein sequences from mutation data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Input CSV file with enzyme lineage data"
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        help="Output CSV file with generated sequences"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug output)"
    )
    
    args = parser.parse_args(argv)
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Process the data (format detection is automatic)
    processor = SequenceProcessor(args.input_csv, args.output_csv)
    processor.run()


if __name__ == "__main__":
    main()