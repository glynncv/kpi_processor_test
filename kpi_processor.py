#!/usr/bin/env python3
"""
KPI Processor - Main Entry Point & Simplified Wrapper
====================================================

This module serves as the primary interface to the KPI processing system, providing
a simplified command-line wrapper around the CompleteConfigurableProcessor engine.

PURPOSE:
--------
The kpi_processor.py acts as a user-friendly facade that:
- Handles file format detection and conversion (CSV/Excel)
- Provides auto-detection of the latest data files
- Simplifies command-line interface for common operations
- Manages temporary file cleanup and error handling
- Abstracts away the complexity of the core processor

ARCHITECTURE:
------------
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  User CLI       │───▶│  kpi_processor   │───▶│ CompleteConfigurable│
│  Commands       │    │  (this file)     │    │ Processor (core)    │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ File Detection & │
                       │ Format Conversion│
                       └──────────────────┘

WORKFLOW:
--------
1. Parse command-line arguments
2. Auto-detect input file if not specified (find_latest_data_file)
3. Convert Excel to CSV if needed (prepare_data_file)
4. Initialize core processor with configuration
5. Execute processing mode (baseline/incremental/targeted)
6. Display results and cleanup temporary files

SUPPORTED FORMATS:
-----------------
- CSV files (.csv) - Used directly
- Excel files (.xls, .xlsx) - Converted to temporary CSV
- Auto-detection based on file modification time

PROCESSING MODES:
----------------
- baseline: Full KPI calculation from scratch
- incremental: Process only new/changed records
- targeted: Process specific KPI only
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import tempfile
import os

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

try:
    from complete_configurable_processor import CompleteConfigurableProcessor
except ImportError:
    print("Error: complete_configurable_processor.py not found in scripts/")
    print("Please ensure the scripts directory contains the main processor.")
    sys.exit(1)

def find_latest_data_file():
    """
    Auto-detect the most recent data file in the data/raw/ directory.
    
    This function implements intelligent file discovery by:
    1. Scanning data/raw/ directory for supported file formats
    2. Filtering for CSV and Excel files (.csv, .xls, .xlsx)
    3. Selecting the file with the most recent modification time
    4. Creating the directory structure if it doesn't exist
    
    Returns:
        str: Absolute path to the most recent data file
        
    Raises:
        FileNotFoundError: If no supported data files are found
        
    Example:
        >>> latest_file = find_latest_data_file()
        Auto-detected latest file: PYTHON IM Q1 (2025).csv
        >>> print(latest_file)
        /path/to/data/raw/PYTHON IM Q1 (2025).csv
        
    Note:
        This replaces the previous complex fallback logic that checked
        multiple directories. The simplified approach focuses on the
        standard data/raw/ location only.
    """
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all supported data files (CSV and Excel formats)
    data_files = list(data_dir.glob("*.csv")) + list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
    
    if not data_files:
        raise FileNotFoundError(f"No data files found in {data_dir}")
    
    # Return the most recent file based on modification time
    latest_file = max(data_files, key=lambda p: p.stat().st_mtime)
    print(f"Auto-detected latest file: {latest_file.name}")
    return str(latest_file)

def prepare_data_file(input_file):
    """
    Prepare input data file for processing by the core engine.
    
    The core CompleteConfigurableProcessor expects CSV format, so this function
    handles format conversion and validation:
    
    1. CSV files: Used directly without modification
    2. Excel files: Converted to temporary CSV files using pandas
    3. Unsupported formats: Raise clear error messages
    
    This approach maintains Excel support for business users while ensuring
    the core processor only deals with standardized CSV format.
    
    Args:
        input_file (str): Path to the input data file
        
    Returns:
        tuple: (processed_file_path, needs_cleanup)
            - processed_file_path (str): Path to CSV file ready for processing
            - needs_cleanup (bool): True if temporary file was created
            
    Raises:
        ValueError: If file format is not supported
        Exception: If file conversion fails (e.g., corrupted Excel file)
        
    Example:
        >>> # CSV file - no conversion needed
        >>> path, cleanup = prepare_data_file("data.csv")
        Using CSV file: data.csv
        >>> print(path, cleanup)
        data.csv False
        
        >>> # Excel file - converted to temporary CSV
        >>> path, cleanup = prepare_data_file("data.xlsx")
        Converting Excel file to CSV: data.xlsx
        Excel file converted to temporary CSV
        >>> print(path, cleanup)
        /tmp/tmpXXXXXX.csv True
        
    Note:
        When needs_cleanup=True, the caller is responsible for deleting
        the temporary file after processing is complete.
    """
    file_path = Path(input_file)
    
    try:
        if file_path.suffix.lower() == '.csv':
            print(f"Using CSV file: {file_path.name}")
            return str(input_file), False
        
        elif file_path.suffix.lower() in ['.xls', '.xlsx']:
            print(f"Converting Excel file to CSV: {file_path.name}")
            df = pd.read_excel(input_file)
            
            # Create temporary CSV file for processing
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            df.to_csv(temp_file.name, index=False)
            temp_file.close()
            
            print(f"Excel file converted to temporary CSV")
            return temp_file.name, True
        
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
    except Exception as e:
        print(f"Error preparing data file {input_file}: {e}")
        raise

def main():
    """
    Main entry point for the KPI Processor command-line interface.
    
    This function orchestrates the entire processing workflow:
    1. Parse and validate command-line arguments
    2. Auto-detect input file if not specified
    3. Prepare data file (handle Excel conversion)
    4. Initialize the core processor with configuration
    5. Execute the requested processing mode
    6. Display results and handle cleanup
    
    Command-line Arguments:
        --mode: Processing strategy
            - baseline: Full calculation from scratch (default)
            - incremental: Process only new/changed records
            - targeted: Process specific KPI only
        --kpi: KPI identifier (required for targeted mode)
            - Examples: SM001, SM002, SM004, GEOGRAPHIC
        --input: Data file path (auto-detects if omitted)
            - Supports: CSV (.csv), Excel (.xls, .xlsx)
        --config: Configuration file (default: config/kpi_config.yaml)
            - Contains KPI definitions, thresholds, column mappings
        --output: JSON output file (optional)
            - Saves detailed results for further analysis
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
        
    Example Usage:
        python kpi_processor.py
        
        python kpi_processor.py --input data.xlsx --mode incremental
        
        python kpi_processor.py --mode targeted --kpi SM001 --output results.json
    """
    parser = argparse.ArgumentParser(
        description='KPI Processor - Simplified wrapper for ServiceNow ITSM analytics',
        epilog="""
Examples:
  %(prog)s                                    # Auto-detect latest file, baseline mode
  %(prog)s --input data.xlsx --mode incremental  # Process Excel file incrementally  
  %(prog)s --mode targeted --kpi SM001           # Calculate major incidents only
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--mode', choices=['baseline', 'incremental', 'targeted'], 
                       default='baseline', 
                       help='Processing mode: baseline (full), incremental (changes only), targeted (single KPI)')
    parser.add_argument('--kpi', 
                       help='Specific KPI to process (required for targeted mode): SM001, SM002, SM004, GEOGRAPHIC')
    parser.add_argument('--input', 
                       help='Input data file path (auto-detects latest in data/raw/ if not specified)')
    parser.add_argument('--config', default='config/kpi_config.yaml', 
                       help='YAML configuration file containing KPI definitions and business rules')
    parser.add_argument('--output', 
                       help='Output JSON file path for detailed results (optional)')
    
    args = parser.parse_args()
    
    if args.input is None:
        try:
            args.input = find_latest_data_file()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Hint: Place CSV or Excel files in data/raw/ directory")
            return 1
    
    # Verify the specified input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found!")
        return 1
    
    processed_input, needs_cleanup = prepare_data_file(args.input)
    
    try:
        print(f"KPI Processor Starting...")
        print(f"Mode: {args.mode}")
        print(f"Config: {args.config}")
        print(f"Input: {args.input}")
        if needs_cleanup:
            print(f"Processed: {Path(processed_input).name} (converted from Excel)")
        print("="*50)
        
        processor = CompleteConfigurableProcessor(
            args.config, 
            validate_config=False  # Skip validation for performance
        )
        
        if args.mode == 'baseline':
            result = processor.process_baseline(processed_input, args.output)
            
        elif args.mode == 'incremental':
            # Process only new/changed records since last run
            result = processor.process_incremental(processed_input, output_file=args.output)
            
        elif args.mode == 'targeted':
            # Process specific KPI only
            if not args.kpi:
                print("Error: --kpi required for targeted mode")
                print("Available KPIs: SM001 (Major Incidents), SM002 (Backlog), SM004 (First Time Fix), GEOGRAPHIC")
                return 1
            result = processor.process_targeted(args.kpi, processed_input)
            
            # Save targeted results if output file specified
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
        
        print(f"{args.mode.title()} processing completed successfully!")
        
        if 'overall_score' in result:
            score_data = result['overall_score']
            print(f"Overall Score: {score_data['overall_score']}/100 ({score_data['performance_band']})")
        
        return 0
        
    except Exception as e:
        print(f"Processing failed: {e}")
        print("Check that your data file format matches the expected column mappings in the config file")
        return 1
        
    finally:
        if needs_cleanup and os.path.exists(processed_input):
            try:
                os.unlink(processed_input)
                print("Cleaned up temporary CSV file")
            except:
                pass  # Ignore cleanup errors to avoid masking main exceptions

if __name__ == "__main__":
    """
    Entry point when script is executed directly.
    
    This wrapper ensures proper exit code handling and allows the module
    to be imported without executing the main function.
    """
    sys.exit(main())
