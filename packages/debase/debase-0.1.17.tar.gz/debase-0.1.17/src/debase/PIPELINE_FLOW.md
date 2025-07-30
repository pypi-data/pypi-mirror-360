# DEBase Pipeline Flow

## Overview
The DEBase pipeline extracts enzyme engineering data from chemistry papers through a series of modular steps.

## Pipeline Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   Manuscript PDF    │     │       SI PDF        │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           └───────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │ 1. enzyme_lineage_extractor │
         │   - Extract enzyme variants │
         │   - Parse mutations         │
         │   - Get basic metadata      │
         └─────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │    2. cleanup_sequence      │
         │   - Validate sequences      │
         │   - Fix formatting issues   │
         │   - Generate full sequences │
         └─────────────┬───────────────┘
                       │
           ┌───────────┴───────────────┐
           │                           │
           ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ 3a. reaction_info       │ │ 3b. substrate_scope     │
│     _extractor          │ │     _extractor          │
│ - Performance metrics   │ │ - Substrate variations  │
│ - Model reaction        │ │ - Additional variants   │
│ - Conditions            │ │ - Scope data            │
└───────────┬─────────────┘ └───────────┬─────────────┘
            │                           │
            └───────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │    4. lineage_format_o3     │
          │   - Merge all data          │
          │   - Fill missing sequences  │
          │   - Format final output     │
          └─────────────┬───────────────┘
                        │
                        ▼
                ┌─────────────┐
                │ Final CSV   │
                └─────────────┘
```

## Module Details

### 1. enzyme_lineage_extractor.py
- **Input**: Manuscript PDF, SI PDF
- **Output**: CSV with enzyme variants and mutations
- **Function**: Extracts enzyme identifiers, mutation lists, and basic metadata

### 2. cleanup_sequence.py  
- **Input**: Enzyme lineage CSV
- **Output**: CSV with validated sequences
- **Function**: Validates protein sequences, generates full sequences from mutations

### 3a. reaction_info_extractor.py
- **Input**: PDFs + cleaned enzyme CSV
- **Output**: CSV with reaction performance data
- **Function**: Extracts yield, TTN, selectivity, reaction conditions

### 3b. substrate_scope_extractor.py
- **Input**: PDFs + cleaned enzyme CSV  
- **Output**: CSV with substrate scope entries
- **Function**: Extracts substrate variations tested with different enzymes

### 4. lineage_format_o3.py
- **Input**: Reaction CSV + Substrate scope CSV
- **Output**: Final formatted CSV
- **Function**: Merges data, fills missing sequences, applies consistent formatting

## Key Features

1. **Modular Design**: Each step can be run independently
2. **Parallel Extraction**: Steps 3a and 3b run independently 
3. **Error Recovery**: Pipeline can resume from any step
4. **Clean Interfaces**: Each module has well-defined inputs/outputs

## Usage

```bash
# Full pipeline
python -m debase.wrapper_clean manuscript.pdf --si si.pdf --output results.csv

# With intermediate files kept for debugging  
python -m debase.wrapper_clean manuscript.pdf --si si.pdf --keep-intermediates
```