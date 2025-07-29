#!/usr/bin/env python3
"""
Enzyme Analysis Pipeline Wrapper (Clean Version)

Pipeline flow:
1. enzyme_lineage_extractor.py - Extract enzyme data from PDFs
2. cleanup_sequence.py - Clean and validate protein sequences
3. reaction_info_extractor.py - Extract reaction performance metrics
4. substrate_scope_extractor.py - Extract substrate scope data (runs independently)
5. lineage_format_o3.py - Format and merge all data into final CSV

The reaction_info and substrate_scope extractors run in parallel,
then their outputs are combined in lineage_format_o3.
"""
import os
import sys
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnzymePipeline")


def run_lineage_extraction(manuscript: Path, si: Path, output: Path, debug_dir: Path = None) -> Path:
    """
    Step 1: Extract enzyme lineage data from PDFs
    Calls: enzyme_lineage_extractor.py
    """
    logger.info(f"Extracting enzyme lineage from {manuscript.name}")
    
    from .enzyme_lineage_extractor import run_pipeline
    run_pipeline(manuscript=manuscript, si=si, output_csv=output, debug_dir=debug_dir)
    
    logger.info(f"Lineage extraction complete: {output}")
    return output


def run_sequence_cleanup(input_csv: Path, output_csv: Path) -> Path:
    """
    Step 2: Clean and validate protein sequences
    Calls: cleanup_sequence.py
    """
    logger.info(f"Cleaning sequences from {input_csv.name}")
    
    from .cleanup_sequence import main as cleanup_sequences
    cleanup_sequences([str(input_csv), str(output_csv)])
    
    logger.info(f"Sequence cleanup complete: {output_csv}")
    return output_csv


def run_reaction_extraction(manuscript: Path, si: Path, lineage_csv: Path, output: Path, debug_dir: Path = None) -> Path:
    """
    Step 3a: Extract reaction performance metrics
    Calls: reaction_info_extractor.py
    """
    logger.info(f"Extracting reaction info for enzymes in {lineage_csv.name}")
    
    from .reaction_info_extractor import ReactionExtractor, Config
    import pandas as pd
    
    # Load enzyme data
    enzyme_df = pd.read_csv(lineage_csv)
    
    # Initialize extractor and run
    cfg = Config()
    extractor = ReactionExtractor(manuscript, si, cfg, debug_dir=debug_dir)
    df_metrics = extractor.run(enzyme_df)
    
    # Save results
    df_metrics.to_csv(output, index=False)
    logger.info(f"Reaction extraction complete: {output}")
    return output


def run_substrate_scope_extraction(manuscript: Path, si: Path, lineage_csv: Path, output: Path, debug_dir: Path = None) -> Path:
    """
    Step 3b: Extract substrate scope data (runs in parallel with reaction extraction)
    Calls: substrate_scope_extractor.py
    """
    logger.info(f"Extracting substrate scope for enzymes in {lineage_csv.name}")
    
    from .substrate_scope_extractor import run_pipeline
    
    # Run substrate scope extraction
    run_pipeline(
        manuscript=manuscript,
        si=si,
        lineage_csv=lineage_csv,
        output_csv=output,
        debug_dir=debug_dir
    )
    
    logger.info(f"Substrate scope extraction complete: {output}")
    return output


def run_lineage_format(reaction_csv: Path, substrate_scope_csv: Path, cleaned_csv: Path, output_csv: Path) -> Path:
    """
    Step 4: Format and merge all data into final CSV
    Calls: lineage_format.py
    """
    logger.info(f"Formatting and merging data into final output")
    
    from .lineage_format import run_pipeline
    import pandas as pd
    
    # First, we need to merge the protein sequences into the reaction data
    df_reaction = pd.read_csv(reaction_csv)
    df_sequences = pd.read_csv(cleaned_csv)
    
    # Merge sequences into reaction data
    # Include generation and parent info for proper mutation calculation
    sequence_cols = ['protein_sequence', 'dna_seq', 'seq_confidence', 'truncated', 'flag', 
                     'generation', 'parent_enzyme_id', 'mutations']
    sequence_data = df_sequences[['enzyme_id'] + [col for col in sequence_cols if col in df_sequences.columns]]
    
    # Merge on enzyme_id or variant_id
    if 'enzyme_id' in df_reaction.columns:
        df_reaction = df_reaction.merge(sequence_data, on='enzyme_id', how='left', suffixes=('', '_seq'))
    elif 'enzyme' in df_reaction.columns:
        sequence_data = sequence_data.rename(columns={'enzyme_id': 'enzyme'})
        df_reaction = df_reaction.merge(sequence_data, on='enzyme', how='left', suffixes=('', '_seq'))
    
    # Save the merged reaction data
    df_reaction.to_csv(reaction_csv, index=False)
    
    # Run the formatting pipeline
    df_final = run_pipeline(
        reaction_csv=reaction_csv,
        substrate_scope_csv=substrate_scope_csv,
        output_csv=output_csv
    )
    
    logger.info(f"Final formatting complete: {output_csv}")
    return output_csv


def run_pipeline(
    manuscript_path: Path,
    si_path: Path = None,
    output_path: Path = None,
    keep_intermediates: bool = False,
    debug_dir: Path = None
) -> Path:
    """Run the complete enzyme analysis pipeline."""
    # Setup paths
    manuscript_path = Path(manuscript_path)
    si_path = Path(si_path) if si_path else None
    
    # Create output filename based on manuscript
    if not output_path:
        output_name = manuscript_path.stem.replace(' ', '_')
        output_path = Path(f"{output_name}_debase.csv")
    else:
        output_path = Path(output_path)
    
    # Use the output directory for all files
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define intermediate file paths (all in the same directory as output)
    lineage_csv = output_dir / "enzyme_lineage_data.csv"  # This is what enzyme_lineage_extractor actually outputs
    cleaned_csv = output_dir / "2_enzyme_sequences.csv"
    reaction_csv = output_dir / "3a_reaction_info.csv"
    substrate_csv = output_dir / "3b_substrate_scope.csv"
    
    try:
        logger.info("="*60)
        logger.info("Starting DEBase Enzyme Analysis Pipeline")
        logger.info(f"Manuscript: {manuscript_path}")
        logger.info(f"SI: {si_path if si_path else 'None'}")
        logger.info(f"Output: {output_path}")
        logger.info("="*60)
        
        start_time = time.time()
        
        # Step 1: Extract enzyme lineage
        logger.info("\n[Step 1/5] Extracting enzyme lineage...")
        run_lineage_extraction(manuscript_path, si_path, lineage_csv, debug_dir=debug_dir)
        
        # Step 2: Clean sequences
        logger.info("\n[Step 2/5] Cleaning sequences...")
        run_sequence_cleanup(lineage_csv, cleaned_csv)
        
        # Step 3: Extract reaction and substrate scope in parallel
        logger.info("\n[Step 3/5] Extracting reaction info and substrate scope...")
        
        # Run reaction extraction
        logger.info("  - Extracting reaction metrics...")
        run_reaction_extraction(manuscript_path, si_path, cleaned_csv, reaction_csv, debug_dir=debug_dir)
        
        # Add small delay to avoid API rate limits
        time.sleep(2)
        
        # Run substrate scope extraction
        logger.info("  - Extracting substrate scope...")
        run_substrate_scope_extraction(manuscript_path, si_path, cleaned_csv, substrate_csv, debug_dir=debug_dir)
        
        # Step 4: Format and merge
        logger.info("\n[Step 4/5] Formatting and merging data...")
        run_lineage_format(reaction_csv, substrate_csv, cleaned_csv, output_path)
        
        # Step 5: Finalize
        logger.info("\n[Step 5/5] Finalizing...")
        elapsed = time.time() - start_time
        
        if keep_intermediates:
            logger.info(f"All intermediate files saved in: {output_dir}")
        else:
            logger.info("Note: Use --keep-intermediates to save intermediate files")
        
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Output: {output_path}")
        logger.info(f"Runtime: {elapsed:.1f} seconds")
        logger.info("="*60)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise
    

def main():
    parser = argparse.ArgumentParser(
        description='DEBase Enzyme Analysis Pipeline - Extract enzyme data from chemistry papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline steps:
  1. enzyme_lineage_extractor - Extract enzyme variants from PDFs
  2. cleanup_sequence - Validate and clean protein sequences  
  3. reaction_info_extractor - Extract reaction performance metrics
  4. substrate_scope_extractor - Extract substrate scope data
  5. lineage_format_o3 - Format and merge into final CSV

The pipeline automatically handles all steps sequentially.
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--manuscript',
        type=Path,
        help='Path to manuscript PDF'
    )
    
    # Optional arguments
    parser.add_argument(
        '--si',
        type=Path,
        help='Path to supplementary information PDF'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output CSV path (default: manuscript_name_debase.csv)'
    )
    parser.add_argument(
        '--keep-intermediates',
        action='store_true',
        help='Keep intermediate files for debugging'
    )
    parser.add_argument(
        '--debug-dir',
        type=Path,
        help='Directory for debug output (prompts, API responses)'
    )
    
    args = parser.parse_args()
    
    # Check inputs
    if not args.manuscript.exists():
        parser.error(f"Manuscript not found: {args.manuscript}")
    if args.si and not args.si.exists():
        parser.error(f"SI not found: {args.si}")
    
    # Run pipeline
    try:
        run_pipeline(
            manuscript_path=args.manuscript,
            si_path=args.si,
            output_path=args.output,
            keep_intermediates=args.keep_intermediates,
            debug_dir=args.debug_dir
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()