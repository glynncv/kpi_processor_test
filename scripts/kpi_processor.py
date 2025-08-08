#!/usr/bin/env python3
"""
KPI Processor - Main Entry Point
===============================
Simple wrapper for the complete configurable processor with Excel and data transformation support
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
    print(" Error: complete_configurable_processor.py not found in scripts/")
    print("   Please ensure the scripts directory contains the main processor.")
    sys.exit(1)

def find_latest_raw_data():
    """Find the most recent data file (CSV or Excel) in data/raw/ directory"""
    raw_data_dir = Path("data/raw")
    
    # Create data/raw directory if it doesn't exist
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f" Searching for data files in: {raw_data_dir}")
    
    # Find all data files in data/raw/ (CSV and Excel)
    data_files = []
    data_files.extend(raw_data_dir.glob("*.csv"))
    data_files.extend(raw_data_dir.glob("*.xls"))
    data_files.extend(raw_data_dir.glob("*.xlsx"))
    
    print(f" Found {len(data_files)} data files in data/raw/:")
    for f in data_files:
        print(f"   - {f.name}")
    
    if data_files:
        # Return the most recent file from data/raw/
        latest_file = max(data_files, key=lambda p: p.stat().st_mtime)
        print(f" Auto-detected latest file: {latest_file}")
        return str(latest_file)
    
    # Fallback: check data/ directory for backward compatibility
    data_dir = Path("data")
    if data_dir.exists():
        print(f" No files in data/raw/, checking fallback: {data_dir}")
        data_files = []
        data_files.extend(data_dir.glob("*.csv"))
        data_files.extend(data_dir.glob("*.xls"))
        data_files.extend(data_dir.glob("*.xlsx"))
        
        print(f" Found {len(data_files)} data files in data/:")
        for f in data_files:
            print(f"   - {f.name}")
        
        if data_files:
            # Return the most recent file from data/
            latest_file = max(data_files, key=lambda p: p.stat().st_mtime)
            print(f" Using fallback file: {latest_file}")
            return str(latest_file)
    
    # No data files found anywhere
    print("  No CSV or Excel files found in data/raw/ or data/")
    return "data/raw/no_data_found.csv"

def load_data_file(file_path):
    """Load data from CSV or Excel file"""
    file_path = Path(file_path)
    
    try:
        if file_path.suffix.lower() == '.csv':
            print(f" Loading CSV file: {file_path.name}")
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xls', '.xlsx']:
            print(f" Loading Excel file: {file_path.name}")
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    except Exception as e:
        print(f" Error loading {file_path}: {e}")
        raise

def transform_data_if_needed(input_file):
    """Transform data to expected column format if needed"""
    try:
        print(f" Checking data format in: {Path(input_file).name}")
        
        # Load the data file (CSV or Excel)
        df_sample = load_data_file(input_file)
        if len(df_sample) > 5:
            df_sample = df_sample.head(5)
            
        original_columns = set(df_sample.columns)
        print(f" Found columns: {sorted(original_columns)}")
        
        # EMEA data column mapping
        emea_column_mapping = {
            'Number': 'number',
            'Priority': 'priority', 
            'Created': 'opened_at',
            'Resolved': 'resolved_at',
            'Incident State': 'state',
            'Reassignment count': 'reassignment_count',
            'Country': 'country',
            'Assignment group': 'assignment_group',
            'Short description': 'description',
            'Category': 'category',
            'Subcategory': 'subcategory'
        }
        
        # Check if this looks like EMEA data (has EMEA-style column names)
        emea_columns = set(emea_column_mapping.keys())
        matching_columns = emea_columns.intersection(original_columns)
        
        if matching_columns:
            print(f" Detected EMEA data format - applying column transformation...")
            print(f"   Matching EMEA columns: {sorted(matching_columns)}")
            
            # Load full dataset
            df = load_data_file(input_file)
            
            # Apply column mapping
            df = df.rename(columns=emea_column_mapping)
            
            # Create temporary CSV file with transformed data
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            df.to_csv(temp_file.name, index=False)
            temp_file.close()
            
            print(f" Data transformed successfully!")
            print(f"   New columns: {sorted(df.columns)}")
            
            return temp_file.name, True
        else:
            # Data is already in expected format, but we might need to convert Excel to CSV
            if Path(input_file).suffix.lower() in ['.xls', '.xlsx']:
                print(" Converting Excel to CSV format...")
                df = load_data_file(input_file)
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                df.to_csv(temp_file.name, index=False)
                temp_file.close()
                print(f" Excel file converted to CSV format")
                return temp_file.name, True
            else:
                print("ℹ  Data already in expected CSV format")
                return input_file, False
            
    except Exception as e:
        print(f"  Could not process data format: {e}")
        print(f"   Proceeding with original file...")
        return input_file, False

def main():
    parser = argparse.ArgumentParser(description='KPI Processor with Excel and transformation support')
    parser.add_argument('--mode', choices=['baseline', 'incremental', 'targeted'], 
                       default='baseline', help='Processing mode')
    parser.add_argument('--kpi', help='Specific KPI to process (for targeted mode)')
    parser.add_argument('--input', default=None, help='Input data file (auto-detects latest in data/raw/ if not specified)')
    parser.add_argument('--config', default='config/kpi_config.yaml', help='Config file')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Auto-detect input file if not specified
    if args.input is None:
        args.input = find_latest_raw_data()
    
    # Verify input file exists
    if not Path(args.input).exists():
        print(f" Error: Input file '{args.input}' not found!")
        return 2  # Use standardized exit code for errors
    
    # Transform data if needed
    processed_input, was_transformed = transform_data_if_needed(args.input)
    temp_file_to_cleanup = processed_input if was_transformed else None
    
    try:
        print(f" KPI Processor Starting...")
        print(f"Mode: {args.mode}")
        print(f"Config: {args.config}")
        print(f"Input: {args.input}")
        if was_transformed:
            print(f"Processed: {Path(processed_input).name} (transformed)")
        print("="*50)
        
        # Initialize processor with validation disabled temporarily
        processor = CompleteConfigurableProcessor(
            args.config, 
            validate_config=False
        )
        
        # Process based on mode (use transformed input)
        if args.mode == 'baseline':
            result = processor.process_baseline(processed_input, args.output)
        elif args.mode == 'incremental':
            result = processor.process_incremental(processed_input, output_file=args.output)
        elif args.mode == 'targeted':
            if not args.kpi:
                print(" Error: --kpi required for targeted mode")
                return 2  # Use standardized exit code for errors
            result = processor.process_targeted(args.kpi, processed_input)
            
            # Save targeted results if output specified
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
        
        print(f" {args.mode.title()} processing completed successfully!")
        
        if 'overall_score' in result:
            score_data = result['overall_score']
            print(f" Overall Score: {score_data['overall_score']}/100 ({score_data['performance_band']})")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Processing cancelled!")
        return 130
    except Exception as e:
        print(f" Processing failed: {e}")
        return 2  # Use standardized exit code for errors
        
    finally:
        # Clean up temporary file if it was created
        if temp_file_to_cleanup and os.path.exists(temp_file_to_cleanup):
            try:
                os.unlink(temp_file_to_cleanup)
                print(" Cleaned up temporary transformed file")
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    sys.exit(main())
