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
    Returns output path even if cleanup fails (copies input file)
    """
    logger.info(f"Cleaning sequences from {input_csv.name}")
    
    try:
        from .cleanup_sequence import main as cleanup_sequences
        cleanup_sequences([str(input_csv), str(output_csv)])
        
        logger.info(f"Sequence cleanup complete: {output_csv}")
        return output_csv
        
    except Exception as e:
        logger.warning(f"Sequence cleanup failed: {e}")
        logger.info("Copying original file to continue pipeline...")
        
        # Copy the input file as-is to continue pipeline
        import shutil
        shutil.copy2(input_csv, output_csv)
        
        logger.info(f"Original file copied: {output_csv}")
        return output_csv


def run_reaction_extraction(manuscript: Path, si: Path, lineage_csv: Path, output: Path, debug_dir: Path = None) -> Path:
    """
    Step 3a: Extract reaction performance metrics
    Calls: reaction_info_extractor.py
    Returns output path even if extraction fails (creates empty file)
    """
    logger.info(f"Extracting reaction info for enzymes in {lineage_csv.name}")
    
    try:
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
        
    except Exception as e:
        logger.warning(f"Reaction extraction failed: {e}")
        logger.info("Creating empty reaction info file to continue pipeline...")
        
        # Create empty reaction CSV with basic columns
        import pandas as pd
        empty_df = pd.DataFrame(columns=[
            'enzyme', 'substrate', 'product', 'yield_percent', 'ee_percent',
            'conversion_percent', 'reaction_type', 'reaction_conditions', 'notes'
        ])
        empty_df.to_csv(output, index=False)
        
        logger.info(f"Empty reaction file created: {output}")
        return output


def run_substrate_scope_extraction(manuscript: Path, si: Path, lineage_csv: Path, output: Path, debug_dir: Path = None) -> Path:
    """
    Step 3b: Extract substrate scope data (runs in parallel with reaction extraction)
    Calls: substrate_scope_extractor.py
    Returns output path even if extraction fails (creates empty file)
    """
    logger.info(f"Extracting substrate scope for enzymes in {lineage_csv.name}")
    
    try:
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
        
    except Exception as e:
        logger.warning(f"Substrate scope extraction failed: {e}")
        logger.info("Creating empty substrate scope file to continue pipeline...")
        
        # Create empty substrate scope CSV with proper headers
        import pandas as pd
        empty_df = pd.DataFrame(columns=[
            'enzyme', 'substrate', 'product', 'yield_percent', 'ee_percent', 
            'conversion_percent', 'selectivity', 'reaction_conditions', 'notes'
        ])
        empty_df.to_csv(output, index=False)
        
        logger.info(f"Empty substrate scope file created: {output}")
        return output


def match_enzyme_variants_with_gemini(lineage_enzymes: list, data_enzymes: list, model=None) -> dict:
    """
    Use Gemini to match enzyme variant IDs between different datasets.
    Returns a mapping of data_enzyme_id -> lineage_enzyme_id.
    """
    import json
    
    if not model:
        try:
            from .enzyme_lineage_extractor import get_model
            model = get_model()
        except:
            logger.warning("Could not load Gemini model for variant matching")
            return {}
    
    prompt = f"""Match enzyme variant IDs between two lists from the same scientific paper.

These lists come from different sections or analyses of the same study, but may use different naming conventions.

List 1 (from lineage/sequence data):
{json.dumps(lineage_enzymes)}

List 2 (from experimental data):
{json.dumps(data_enzymes)}

Analyze the patterns and match variants that refer to the same enzyme.
Return ONLY a JSON object mapping IDs from List 2 to their corresponding IDs in List 1.
Format: {{"list2_id": "list1_id", ...}}
Only include matches you are confident about based on the naming patterns.
"""
    
    try:
        response = model.generate_content(prompt)
        mapping_text = response.text.strip()
        
        # Extract JSON from response
        if '```json' in mapping_text:
            mapping_text = mapping_text.split('```json')[1].split('```')[0].strip()
        elif '```' in mapping_text:
            mapping_text = mapping_text.split('```')[1].split('```')[0].strip()
        
        mapping = json.loads(mapping_text)
        logger.info(f"Gemini matched {len(mapping)} enzyme variants")
        for k, v in mapping.items():
            logger.info(f"  Matched '{k}' -> '{v}'")
        return mapping
    except Exception as e:
        logger.warning(f"Failed to match variants with Gemini: {e}")
        return {}


def run_lineage_format(reaction_csv: Path, substrate_scope_csv: Path, cleaned_csv: Path, output_csv: Path) -> Path:
    """
    Step 4: Format and merge all data into final CSV
    Creates comprehensive format merging all available data, even if some extraction steps failed
    """
    logger.info(f"Formatting and merging data into final output")
    
    try:
        import pandas as pd
        
        # Read all available data files
        logger.info("Reading enzyme lineage data...")
        df_lineage = pd.read_csv(cleaned_csv)
        
        logger.info("Reading reaction data...")
        try:
            df_reaction = pd.read_csv(reaction_csv)
            has_reaction_data = len(df_reaction) > 0 and not df_reaction.empty
        except:
            df_reaction = pd.DataFrame()
            has_reaction_data = False
        
        logger.info("Reading substrate scope data...")
        try:
            df_scope = pd.read_csv(substrate_scope_csv)
            has_scope_data = len(df_scope) > 0 and not df_scope.empty
        except:
            df_scope = pd.DataFrame()
            has_scope_data = False
        
        # Start with lineage data as base
        df_final = df_lineage.copy()
        
        # Ensure consistent enzyme ID column
        if 'variant_id' in df_final.columns and 'enzyme_id' not in df_final.columns:
            df_final = df_final.rename(columns={'variant_id': 'enzyme_id'})
        
        # Merge reaction data if available
        if has_reaction_data:
            logger.info(f"Merging reaction data ({len(df_reaction)} records)")
            # Match on enzyme_id or enzyme
            merge_key = 'enzyme_id' if 'enzyme_id' in df_reaction.columns else 'enzyme'
            if merge_key in df_reaction.columns:
                df_final = df_final.merge(df_reaction, left_on='enzyme_id', right_on=merge_key, how='left', suffixes=('', '_reaction'))
        else:
            logger.info("No reaction data available")
        
        # Merge substrate scope data if available
        if has_scope_data:
            logger.info(f"Merging substrate scope data ({len(df_scope)} records)")
            merge_key = 'enzyme_id' if 'enzyme_id' in df_scope.columns else 'enzyme'
            
            if merge_key in df_scope.columns:
                # First try direct merge
                df_test_merge = df_final.merge(df_scope, left_on='enzyme_id', right_on=merge_key, how='left', suffixes=('', '_scope'))
                
                # Check if any matches were found
                matched_count = df_test_merge[merge_key + '_scope'].notna().sum() if merge_key + '_scope' in df_test_merge.columns else 0
                
                if matched_count == 0:
                    logger.info("No direct matches found, using Gemini to match enzyme variants...")
                    
                    # Get unique enzyme IDs from both datasets
                    lineage_enzymes = df_final['enzyme_id'].dropna().unique().tolist()
                    scope_enzymes = df_scope[merge_key].dropna().unique().tolist()
                    
                    # Get mapping from Gemini
                    mapping = match_enzyme_variants_with_gemini(lineage_enzymes, scope_enzymes)
                    
                    if mapping:
                        # Apply mapping to scope data
                        df_scope_mapped = df_scope.copy()
                        df_scope_mapped[merge_key] = df_scope_mapped[merge_key].map(lambda x: mapping.get(x, x))
                        df_final = df_final.merge(df_scope_mapped, left_on='enzyme_id', right_on=merge_key, how='left', suffixes=('', '_scope'))
                    else:
                        logger.warning("Could not match enzyme variants between datasets")
                        df_final = df_test_merge
                else:
                    df_final = df_test_merge
                    logger.info(f"Direct merge matched {matched_count} records")
        else:
            logger.info("No substrate scope data available")
        
        # Add comprehensive column structure for missing data
        essential_columns = [
            'enzyme_id', 'parent_id', 'generation', 'mutations', 'campaign_id', 'notes',
            'aa_seq', 'dna_seq', 'seq_confidence', 'truncated', 'seq_source', 'doi',
            'substrate_list', 'substrate_iupac_list', 'product_list', 'product_iupac_list',
            'cofactor_list', 'cofactor_iupac_list', 'yield', 'ee', 'ttn',
            'reaction_temperature', 'reaction_ph', 'reaction_buffer', 'reaction_other_conditions',
            'data_location'
        ]
        
        # Add missing columns with NaN
        for col in essential_columns:
            if col not in df_final.columns:
                df_final[col] = None
        
        # Clean up duplicate columns from merging
        columns_to_keep = []
        seen_base_names = set()
        for col in df_final.columns:
            base_name = col.split('_reaction')[0].split('_scope')[0]
            if base_name not in seen_base_names:
                columns_to_keep.append(col)
                seen_base_names.add(base_name)
            elif col.endswith('_scope') or col.endswith('_reaction'):
                # Prefer scope or reaction data over base lineage data for certain columns
                if base_name in ['substrate_list', 'product_list', 'yield', 'ee', 'reaction_temperature']:
                    columns_to_keep.append(col)
                    # Remove the base column if it exists
                    if base_name in columns_to_keep:
                        columns_to_keep.remove(base_name)
                    seen_base_names.add(base_name)
        
        df_final = df_final[columns_to_keep]
        
        # Rename merged columns back to standard names
        rename_map = {}
        for col in df_final.columns:
            if col.endswith('_scope') or col.endswith('_reaction'):
                base_name = col.split('_scope')[0].split('_reaction')[0]
                rename_map[col] = base_name
        df_final = df_final.rename(columns=rename_map)
        
        # Save the comprehensive final output
        df_final.to_csv(output_csv, index=False)
        
        logger.info(f"Final comprehensive format complete: {output_csv}")
        logger.info(f"Final output contains {len(df_final)} variants with {len(df_final.columns)} data columns")
        
        # Log what data was successfully merged
        if has_reaction_data:
            logger.info("✓ Reaction performance data merged")
        if has_scope_data:
            logger.info("✓ Substrate scope data merged")
        
        # Now run the actual lineage format to produce plate-based format
        logger.info("\nRunning lineage format to produce plate-based output...")
        try:
            from .lineage_format import flatten_dataframe
            
            # Create the plate-based output filename
            plate_output = output_csv.parent / (output_csv.stem + "_plate_format.csv")
            
            # Flatten the dataframe to plate format
            df_flattened = flatten_dataframe(df_final)
            
            # Save the flattened output
            df_flattened.to_csv(plate_output, index=False)
            
            logger.info(f"✓ Plate-based format saved to: {plate_output}")
            logger.info(f"  Contains {len(df_flattened)} rows with plate/well assignments")
            
            # Update the final output path to be the plate format
            output_csv = plate_output
            
        except Exception as e:
            logger.warning(f"Could not generate plate-based format: {e}")
            logger.info("Comprehensive format will be used as final output")
        
        return output_csv
        
    except Exception as e:
        logger.warning(f"Final formatting failed: {e}")
        logger.info("Using cleaned sequence data as final output...")
        
        # Copy the cleaned CSV as the final output
        import shutil
        shutil.copy2(cleaned_csv, output_csv)
        
        logger.info(f"Cleaned sequence file used as final output: {output_csv}")
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
        final_output = run_lineage_format(reaction_csv, substrate_csv, cleaned_csv, output_path)
        
        # Step 5: Finalize
        logger.info("\n[Step 5/5] Finalizing...")
        elapsed = time.time() - start_time
        
        if keep_intermediates:
            logger.info(f"All intermediate files saved in: {output_dir}")
        else:
            logger.info("Note: Use --keep-intermediates to save intermediate files")
        
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Comprehensive output: {output_path}")
        if final_output != output_path:
            logger.info(f"Plate-based output: {final_output}")
        logger.info(f"Runtime: {elapsed:.1f} seconds")
        logger.info("="*60)
        
        return final_output
        
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