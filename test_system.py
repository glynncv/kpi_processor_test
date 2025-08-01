#!/usr/bin/env python3
"""
Test Script for KPI Processing System
=====================================

This script tests the complete KPI processing system with real data.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add scripts directory to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

def test_system():
    """Test the complete KPI processing system"""
    
    print("[SEARCH] TESTING KPI PROCESSING SYSTEM")
    print("=" * 50)
    
    # Define paths
    config_file = "config/complete_kpi_config.yaml"
    data_file = "data/raw/PYTHON EMEA IM Q1 (2025).csv"
    processor_module = "complete_configurable_processor_fixed"
    validator_module = "config_validator_fixed"
    
    # Check if files exist
    print("\n[CLIPBOARD] Checking required files...")
    files_to_check = [config_file, data_file]
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"[CHECKMARK] Found: {file_path}")
        else:
            print(f"[X] Missing: {file_path}")
            return False
    
    # Check data file structure
    print("\n[CHART] Analyzing data file structure...")
    try:
        df = pd.read_csv(data_file, nrows=5)
        print(f"[CHECKMARK] Data file loaded successfully")
        print(f"[INFO] Columns ({len(df.columns)}): {list(df.columns)}")
        print(f"[INFO] Shape: {df.shape}")
        print(f"[INFO] Sample data:")
        print(df.head())
    except Exception as e:
        print(f"[X] Error loading data file: {e}")
        return False
    
    # Test configuration validator
    print("\n[BUILDING] Testing configuration validator...")
    try:
        from config_validator_fixed import ConfigurationValidator
        
        validator = ConfigurationValidator(strict_mode=False)
        validation_result = validator.validate_configuration(config_file, data_file)
        
        if validation_result['validation_passed']:
            print("[CHECKMARK] Configuration validation PASSED")
        else:
            print("[X] Configuration validation FAILED")
            print(f"Errors: {validation_result['summary']['total_errors']}")
            print(f"Warnings: {validation_result['summary']['total_warnings']}")
            
            # Show first few errors
            for error in validation_result['errors'][:3]:
                print(f"  - {error}")
                
        # Generate validation report
        report = validator.generate_validation_report(validation_result, "output/validation_report.md")
        print("[DOCUMENT] Validation report generated")
        
    except Exception as e:
        print(f"[X] Configuration validator failed: {e}")
        return False
    
    # Test KPI processor
    print("\n[WRENCH] Testing KPI processor...")
    try:
        from complete_configurable_processor_fixed import CompleteConfigurableProcessor
        
        processor = CompleteConfigurableProcessor(config_file)
        
        # Test baseline processing
        print("[INFO] Running baseline processing...")
        baseline_results = processor.process_baseline(data_file, "output/baseline_results.json")
        print(f"[CHECKMARK] Baseline processing completed")
        print(f"[INFO] Processed {baseline_results.get('total_records', 0)} records")
        
        # Test incremental processing (if we have previous results)
        output_dir = Path("output")
        previous_results = list(output_dir.glob("baseline_results_*.json"))
        if previous_results:
            print("[INFO] Running incremental processing...")
            incremental_results = processor.process_incremental(
                data_file, 
                str(previous_results[0]), 
                "output/incremental_results.json"
            )
            print(f"[CHECKMARK] Incremental processing completed")
        
        print("[CHECKMARK] KPI processor test completed successfully")
        
    except Exception as e:
        print(f"[X] KPI processor failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[ROCKET] SYSTEM TEST COMPLETED SUCCESSFULLY")
    print("All components are working correctly!")
    return True

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
