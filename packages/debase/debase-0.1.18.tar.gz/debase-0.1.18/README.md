# DEBase

Enzyme lineage analysis and sequence extraction package with advanced parallel processing capabilities.

## Installation

### Quick Install (PyPI)
```bash
pip install debase
```

### Development Setup with Conda (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/YuemingLong/DEBase.git
cd DEBase
```

2. **Create conda environment from provided file**
```bash
conda env create -f environment.yml
conda activate debase
```

3. **Install DEBase in development mode**
```bash
pip install -e .
```

### Manual Setup

If you prefer to set up the environment manually:

```bash
# Create new conda environment
conda create -n debase python=3.9
conda activate debase

# Install conda packages
conda install -c conda-forge pandas numpy matplotlib seaborn jupyter jupyterlab openpyxl biopython requests tqdm

# Install RDKit (optional - used for SMILES canonicalization)
conda install -c conda-forge rdkit

# Install pip-only packages
pip install PyMuPDF google-generativeai debase
```

**Note about RDKit**: RDKit is optional and only used for canonicalizing SMILES strings in the output. If not installed, DEBase will still function normally but SMILES strings won't be standardized.

## Requirements

- Python 3.8 or higher
- A Gemini API key (set as environment variable `GEMINI_API_KEY`)

### Setting up Gemini API Key

```bash
# Option 1: Export in your shell
export GEMINI_API_KEY="your-api-key-here"

# Option 2: Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Option 3: Create .env file in project directory
echo 'GEMINI_API_KEY=your-api-key-here' > .env
```

## Recent Updates

- **Campaign-Aware Extraction**: Automatically detects and processes multiple directed evolution campaigns in a single paper
- **Improved Model Support**: Updated to use stable Gemini models for better reliability
- **Enhanced PDB Integration**: Intelligent AI-based matching of PDB structures to enzyme variants
- **Better Filtering**: Automatic removal of non-enzyme entries (buffers, controls, media)
- **Optimized Performance**: Removed unnecessary rate limiting for faster processing
- **External Sequence Fetching**: Automatic retrieval from PDB and UniProt databases when sequences aren't in papers
- **Improved SI Processing**: Structure-aware extraction of supplementary information
- **Vision Support**: Extracts data from figures and tables using multimodal AI capabilities

## Quick Start

### Basic Usage
```bash
# Run the full pipeline (sequential processing)
debase --manuscript manuscript.pdf --si supplementary.pdf --output output.csv
```

### High-Performance Parallel Processing
```bash
# Use parallel individual processing for maximum speed + accuracy
debase --manuscript manuscript.pdf --si supplementary.pdf --output output.csv \
  --use-parallel-individual --max-workers 5

# Use batch processing for maximum speed (slight accuracy trade-off)
debase --manuscript manuscript.pdf --si supplementary.pdf --output output.csv \
  --use-optimized-reaction --reaction-batch-size 5
```

## Processing Methods

DEBase offers three processing approaches optimized for different use cases:

### 1. **Parallel Individual Processing** (Recommended)
- **42 individual API calls** (21 for reactions + 21 for substrate scope)
- **5 calls running simultaneously** for 4-5x speedup
- **Maximum accuracy** - each enzyme gets dedicated attention
- **Best for:** Production use, important analyses

```bash
debase --manuscript paper.pdf --si si.pdf --use-parallel-individual --max-workers 5
```

### 2. **Batch Processing** (Fastest)
- **~8 total API calls** (multiple enzymes per call)
- **Fastest processing** - up to 8x speedup
- **Good accuracy** - slight trade-off for complex chemical names
- **Best for:** Quick analyses, large-scale processing

```bash
debase --manuscript paper.pdf --si si.pdf --use-optimized-reaction --reaction-batch-size 5
```

### 3. **Sequential Processing** (Most Accurate)
- **42 sequential API calls** (one at a time)
- **Highest accuracy** but slowest
- **Best for:** Critical analyses, small datasets

```bash
debase --manuscript paper.pdf --si si.pdf  # Default method
```


## Advanced Usage

### Skip Steps with Existing Data
```bash
# Skip lineage extraction if you already have it
debase --manuscript paper.pdf --si si.pdf --output output.csv \
  --skip-lineage --existing-lineage existing_lineage.csv \
  --use-parallel-individual
```

### Direct Module Usage
```bash
# Run only reaction extraction with parallel processing
python -m debase.reaction_info_extractor_parallel \
  --manuscript paper.pdf --si si.pdf --lineage-csv lineage.csv \
  --max-workers 5 --output reactions.csv

# Run only substrate scope extraction with parallel processing  
python -m debase.substrate_scope_extractor_parallel \
  --manuscript paper.pdf --si si.pdf --lineage-csv lineage.csv \
  --max-workers 5 --output substrate_scope.csv
```
## Pipeline Architecture

The DEBase pipeline consists of 5 main steps:

1. **Lineage Extraction** (Sequential) - Identifies all enzymes and their relationships
   - Extracts mutation information and evolutionary paths
   - Detects multiple directed evolution campaigns automatically
   - Fetches sequences from external databases (PDB, UniProt)
   - Filters out non-enzyme entries automatically
2. **Sequence Cleanup** (Local) - Generates protein sequences from mutations  
   - Applies mutations to parent sequences
   - Handles complex mutations and domain modifications
   - Validates sequence integrity
3. **Reaction Extraction** (Parallel/Batch/Sequential) - Extracts reaction conditions and performance data
   - Campaign-aware extraction for multi-lineage papers
   - Vision-based extraction from figures and tables
   - Automatic IUPAC name resolution
4. **Substrate Scope Extraction** (Parallel/Sequential) - Finds additional substrates tested
5. **Data Formatting** (Local) - Combines all data into final output

## Features

- **Multi-processing modes:** Sequential, parallel individual, and batch processing
- **Campaign detection:** Automatically identifies and separates multiple directed evolution campaigns
- **Intelligent error handling:** Automatic retries with exponential backoff
- **External database integration:** Automatic sequence fetching from PDB and UniProt
- **AI-powered matching:** Uses Gemini to intelligently match database entries to enzyme variants
- **Smart filtering:** Automatically excludes non-enzyme entries (buffers, controls, etc.)
- **Vision capabilities:** Extracts data from both text and images in PDFs

## Complete Command Reference

### Core Arguments
```bash
--manuscript PATH           # Required: Path to manuscript PDF
--si PATH                  # Optional: Path to supplementary information PDF
--output PATH              # Output file path (default: manuscript_name_debase.csv)
```

### Performance Options
```bash
--use-parallel-individual  # Use parallel processing (recommended)
--max-workers N            # Number of parallel workers (default: 5)
--use-optimized-reaction   # Use batch processing for speed
--reaction-batch-size N    # Enzymes per batch (default: 5)
--no-parallel-queries      # Disable parallel processing
```

### Pipeline Control
```bash
--skip-lineage             # Skip lineage extraction step
--skip-sequence            # Skip sequence cleanup step  
--skip-reaction            # Skip reaction extraction step
--skip-substrate-scope     # Skip substrate scope extraction step
--skip-lineage-format      # Skip final formatting step
--skip-validation          # Skip data validation step
```

### Data Management
```bash
--existing-lineage PATH    # Use existing lineage data
--existing-sequence PATH   # Use existing sequence data
--existing-reaction PATH   # Use existing reaction data
--keep-intermediates       # Preserve intermediate files
```

### Advanced Options
```bash
--model-name NAME          # Gemini model to use
--max-retries N            # Maximum retry attempts (default: 2)
--max-chars N              # Max characters from PDFs (default: 75000)
--debug-dir PATH           # Directory for debug output (prompts, API responses)
```

## Tips for Best Performance

1. **Use parallel individual processing** for the best balance of speed and accuracy
2. **Set max-workers to 5** to avoid API rate limits while maximizing throughput
3. **Use batch processing** only when speed is critical and some accuracy loss is acceptable
4. **Skip validation** (`--skip-validation`) for faster processing in production
5. **Keep intermediates** (`--keep-intermediates`) for debugging and incremental runs
6. 

