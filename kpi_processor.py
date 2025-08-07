#!/usr/bin/env python3
"""
KPI Processor - Main Entry Point
===============================
Simplified wrapper for the complete configurable processor with Excel support
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
    """Find the most recent data file (CSV or Excel) in data/raw/ directory"""
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all supported data files
    data_files = list(data_dir.glob("*.csv")) + list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
    
    if not data_files:
        raise FileNotFoundError(f"No data files found in {data_dir}")
    
    # Return the most recent file
    latest_file = max(data_files, key=lambda p: p.stat().st_mtime)
    print(f"Auto-detected latest file: {latest_file.name}")
    return str(latest_file)

def prepare_data_file(input_file):
    """Prepare data file for processing (convert Excel to CSV if needed)"""
    file_path = Path(input_file)
    
    try:
        if file_path.suffix.lower() == '.csv':
            print(f"Using CSV file: {file_path.name}")
            return str(input_file), False
        
        elif file_path.suffix.lower() in ['.xls', '.xlsx']:
            print(f"Converting Excel file to CSV: {file_path.name}")
            df = pd.read_excel(input_file)
            
            # Create temporary CSV file
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
    parser = argparse.ArgumentParser(description='KPI Processor with Excel support')
    parser.add_argument('--mode', choices=['baseline', 'incremental', 'targeted'], 
                       default='baseline', help='Processing mode')
    parser.add_argument('--kpi', help='Specific KPI to process (for targeted mode)')
    parser.add_argument('--input', help='Input data file (auto-detects latest in data/raw/ if not specified)')
    parser.add_argument('--config', default='config/kpi_config.yaml', help='Config file')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Auto-detect input file if not specified
    if args.input is None:
        try:
            args.input = find_latest_data_file()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1
    
    # Verify input file exists
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
        
        # Initialize processor
        processor = CompleteConfigurableProcessor(
            args.config, 
            validate_config=False
        )
        
        # Process based on mode
        if args.mode == 'baseline':
            result = processor.process_baseline(processed_input, args.output)
        elif args.mode == 'incremental':
            result = processor.process_incremental(processed_input, output_file=args.output)
        elif args.mode == 'targeted':
            if not args.kpi:
                print("Error: --kpi required for targeted mode")
                return 1
            result = processor.process_targeted(args.kpi, processed_input)
            
            # Save targeted results if output specified
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
        return 1
        
    finally:
        # Clean up temporary file if it was created
        if needs_cleanup and os.path.exists(processed_input):
            try:
                os.unlink(processed_input)
                print("Cleaned up temporary CSV file")
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    sys.exit(main())
