#!/usr/bin/env python3
"""
KPI Processor - Main Entry Point
===============================
Simple wrapper for the complete configurable processor
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

try:
    from complete_configurable_processor import CompleteConfigurableProcessor
except ImportError:
    print(" Error: complete_configurable_processor.py not found in scripts/")
    print("   Please ensure the scripts directory contains the main processor.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='KPI Processor')
    parser.add_argument('--mode', choices=['baseline', 'incremental', 'targeted'], 
                       default='baseline', help='Processing mode')
    parser.add_argument('--kpi', help='Specific KPI to process (for targeted mode)')
    parser.add_argument('--input', default='data/sample_data.csv', help='Input CSV file')
    parser.add_argument('--config', default='config/kpi_config.yaml', help='Config file')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    try:
        print(f" KPI Processor Starting...")
        print(f"Mode: {args.mode}")
        print(f"Config: {args.config}")
        print(f"Input: {args.input}")
        print("="*50)
        
        # Initialize processor
        processor = CompleteConfigurableProcessor(
            args.config, 
            validate_config=True
        )
        
        # Process based on mode
        if args.mode == 'baseline':
            result = processor.process_baseline(args.input, args.output)
        elif args.mode == 'incremental':
            result = processor.process_incremental(args.input, output_file=args.output)
        elif args.mode == 'targeted':
            if not args.kpi:
                print(" Error: --kpi required for targeted mode")
                return 1
            result = processor.process_targeted(args.kpi, args.input)
            
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
        
    except Exception as e:
        print(f" Processing failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
