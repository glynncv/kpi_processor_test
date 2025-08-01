#!/usr/bin/env python3
"""
Configuration Validator for KPI Processing
==========================================

Validates YAML configuration files for:
1. Schema compliance
2. Business rule validation  
3. Data consistency checks
4. Field availability verification

Usage:
    python config_validator.py --config kpi_config.yaml --strict
    python config_validator.py --config kpi_config.yaml --check-data data.csv
"""

import yaml
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import re
import argparse

class ConfigurationValidator:
    """
    Comprehensive configuration validator for KPI processing system
    """
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.logger = self._setup_logging()
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_info = []
        
        # Define expected schema structure
        self.required_sections = {
            'metadata': ['version', 'organization', 'schema_version'],
            'column_mappings': [],  # Dynamic content
            'kpis': [],            # Dynamic content
            'thresholds': ['aging', 'priority'],
            'processing': ['priority_extraction', 'date_parsing']
        }
        
        # Define validation rules
        self.validation_rules = self._define_validation_rules()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _define_validation_rules(self) -> Dict[str, Any]:
        """Define comprehensive validation rules"""
        return {
            'required_kpi_fields': [
                'name', 'description', 'category', 'calculation_method', 
                'data_sources', 'thresholds', 'output_format'
            ],
            'valid_calculation_methods': [
                'percentage', 'count', 'ratio', 'aggregation', 'weighted_average'
            ],
            'valid_categories': [
                'incident_management', 'service_request', 'change_management', 
                'problem_management', 'availability', 'performance'
            ],
            'required_threshold_fields': ['target', 'warning', 'critical'],
            'valid_output_formats': ['percentage', 'decimal', 'integer', 'currency'],
            'date_field_patterns': [
                r'.*date.*', r'.*created.*', r'.*updated.*', 
                r'.*opened.*', r'.*closed.*', r'.*resolved.*'
            ]
        }
    
    def validate_configuration(self, config_file: str, data_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Main validation method that orchestrates all validation checks
        """
        try:
            self.logger.info(f"[SEARCH] Validating configuration: {config_file}")
            
            # Reset validation state
            self.validation_errors = []
            self.validation_warnings = []
            self.validation_info = []
            
            # Load configuration
            config = self._load_configuration(config_file)
            
            # Run validation checks
            self._validate_schema(config)
            self._validate_content(config)
            self._validate_business_rules(config)
            self._validate_cross_references(config)
            
            # Optional data compatibility check
            if data_file:
                self._validate_data_compatibility(config, data_file)
            
            # Compile results
            validation_passed = len(self.validation_errors) == 0
            
            # Log final result
            if validation_passed:
                if len(self.validation_warnings) == 0:
                    self.logger.info("[CHECKMARK] Configuration validation PASSED")
                else:
                    self.logger.warning("[X] Configuration validation FAILED")
            
            return self._compile_validation_results(validation_passed)
            
        except Exception as e:
            self.logger.error(f"[X] Validation failed with exception: {e}")
            return self._compile_validation_results(False, str(e))
    
    def _load_configuration(self, config_file: str) -> Dict[str, Any]:
        """Load and parse YAML configuration file"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.validation_info.append(f"Configuration loaded from {config_file}")
            return config
            
        except yaml.YAMLError as e:
            self.validation_errors.append(f"YAML parsing error: {e}")
            raise
        except Exception as e:
            self.validation_errors.append(f"Configuration loading error: {e}")
            raise
    
    def _validate_schema(self, config: Dict[str, Any]) -> None:
        """Validate the basic schema structure of the configuration"""
        self.logger.info("[CLIPBOARD] Validating configuration schema...")
        
        # Check for required top-level sections
        for section in self.required_sections:
            if section not in config:
                self.validation_errors.append(f"Missing required section: {section}")
            else:
                self.validation_info.append(f"Found required section: {section}")
        
        # Validate metadata section
        if 'metadata' in config:
            metadata = config['metadata']
            for field in self.required_sections['metadata']:
                if field not in metadata:
                    self.validation_errors.append(f"Missing metadata field: {field}")
                else:
                    self.validation_info.append(f"Found metadata field: {field}")
        
        # Validate column_mappings structure
        if 'column_mappings' in config:
            column_mappings = config['column_mappings']
            if not isinstance(column_mappings, dict):
                self.validation_errors.append("column_mappings must be a dictionary")
            else:
                self.validation_info.append(f"Column mappings defined for {len(column_mappings)} fields")
        
        # Validate KPIs structure
        if 'kpis' in config:
            kpis = config['kpis']
            if not isinstance(kpis, dict):
                self.validation_errors.append("kpis must be a dictionary")
            else:
                self.validation_info.append(f"Found {len(kpis)} KPI definitions")
                
                # Validate each KPI structure
                for kpi_id, kpi_config in kpis.items():
                    self._validate_kpi_structure(kpi_id, kpi_config)
        
        # Validate thresholds structure
        if 'thresholds' in config:
            thresholds = config['thresholds']
            if not isinstance(thresholds, dict):
                self.validation_errors.append("thresholds must be a dictionary")
            else:
                for threshold_type in ['aging', 'priority']:
                    if threshold_type not in thresholds:
                        self.validation_warnings.append(f"Missing threshold type: {threshold_type}")
                    else:
                        self.validation_info.append(f"Found threshold type: {threshold_type}")
        
        # Validate processing section
        if 'processing' in config:
            processing = config['processing']
            if not isinstance(processing, dict):
                self.validation_errors.append("processing must be a dictionary")
            else:
                for proc_type in ['priority_extraction', 'date_parsing']:
                    if proc_type not in processing:
                        self.validation_warnings.append(f"Missing processing config: {proc_type}")
                    else:
                        self.validation_info.append(f"Found processing config: {proc_type}")
    
    def _validate_kpi_structure(self, kpi_id: str, kpi_config: Dict[str, Any]) -> None:
        """Validate the structure of an individual KPI configuration"""
        required_fields = self.validation_rules['required_kpi_fields']
        
        for field in required_fields:
            if field not in kpi_config:
                self.validation_errors.append(f"KPI {kpi_id} missing required field: {field}")
            else:
                self.validation_info.append(f"KPI {kpi_id} has required field: {field}")
        
        # Validate calculation method
        if 'calculation_method' in kpi_config:
            method = kpi_config['calculation_method']
            valid_methods = self.validation_rules['valid_calculation_methods']
            if method not in valid_methods:
                self.validation_errors.append(
                    f"KPI {kpi_id} has invalid calculation method: {method}. "
                    f"Valid methods: {valid_methods}"
                )
        
        # Validate category
        if 'category' in kpi_config:
            category = kpi_config['category']
            valid_categories = self.validation_rules['valid_categories']
            if category not in valid_categories:
                self.validation_warnings.append(
                    f"KPI {kpi_id} has non-standard category: {category}. "
                    f"Standard categories: {valid_categories}"
                )
        
        # Validate thresholds
        if 'thresholds' in kpi_config:
            thresholds = kpi_config['thresholds']
            required_threshold_fields = self.validation_rules['required_threshold_fields']
            for field in required_threshold_fields:
                if field not in thresholds:
                    self.validation_errors.append(f"KPI {kpi_id} threshold missing field: {field}")
        
        # Validate output format
        if 'output_format' in kpi_config:
            output_format = kpi_config['output_format']
            valid_formats = self.validation_rules['valid_output_formats']
            if output_format not in valid_formats:
                self.validation_warnings.append(
                    f"KPI {kpi_id} has non-standard output format: {output_format}. "
                    f"Standard formats: {valid_formats}"
                )
    
    def _validate_content(self, config: Dict[str, Any]) -> None:
        """Validate the content and logical consistency of the configuration"""
        self.logger.info("[CHART] Validating configuration content...")
        
        # Validate column mappings content
        if 'column_mappings' in config:
            column_mappings = config['column_mappings']
            
            # Check for essential date fields
            essential_date_fields = ['created_date', 'updated_date', 'resolved_date', 'closed_date']
            for field in essential_date_fields:
                if field not in column_mappings:
                    self.validation_warnings.append(f"Missing essential date field mapping: {field}")
            
            # Check for essential categorical fields
            essential_categorical_fields = ['priority', 'state', 'category', 'assignment_group']
            for field in essential_categorical_fields:
                if field not in column_mappings:
                    self.validation_warnings.append(f"Missing essential categorical field mapping: {field}")
        
        # Validate KPI content
        if 'kpis' in config:
            kpis = config['kpis']
            
            # Check for balanced KPI coverage
            categories = [kpi.get('category', 'unknown') for kpi in kpis.values()]
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            self.validation_info.append(f"KPI category distribution: {category_counts}")
            
            # Warn if any category is heavily over-represented
            total_kpis = len(kpis)
            for category, count in category_counts.items():
                if count > total_kpis * 0.5:  # More than 50% of KPIs
                    self.validation_warnings.append(
                        f"Category '{category}' represents {count}/{total_kpis} KPIs. "
                        "Consider balancing KPI categories."
                    )
        
        # Validate threshold values
        if 'thresholds' in config:
            thresholds = config['thresholds']
            
            # Validate aging thresholds
            if 'aging' in thresholds:
                aging = thresholds['aging']
                if isinstance(aging, dict):
                    for key, value in aging.items():
                        if not isinstance(value, (int, float)) or value <= 0:
                            self.validation_errors.append(
                                f"Aging threshold '{key}' must be a positive number, got: {value}"
                            )
            
            # Validate priority mappings
            if 'priority' in thresholds:
                priority = thresholds['priority']
                if isinstance(priority, dict):
                    # Check for standard priority levels
                    standard_priorities = ['critical', 'high', 'medium', 'low']
                    for priority_level in standard_priorities:
                        if priority_level not in priority:
                            self.validation_warnings.append(
                                f"Missing standard priority level: {priority_level}"
                            )
    
    def _validate_business_rules(self, config: Dict[str, Any]) -> None:
        """Validate business-specific rules and logic"""
        self.logger.info("[BUILDING] Validating business rules...")
        
        if 'kpis' in config:
            kpis = config['kpis']
            
            for kpi_id, kpi_config in kpis.items():
                # Validate threshold logical consistency
                if 'thresholds' in kpi_config:
                    thresholds = kpi_config['thresholds']
                    
                    # For percentage-based KPIs, thresholds should be between 0-100
                    if kpi_config.get('output_format') == 'percentage':
                        for threshold_type, value in thresholds.items():
                            if isinstance(value, (int, float)):
                                if not (0 <= value <= 100):
                                    self.validation_warnings.append(
                                        f"KPI {kpi_id} percentage threshold '{threshold_type}' "
                                        f"should be 0-100, got: {value}"
                                    )
                    
                    # Validate threshold ordering (target >= warning >= critical for performance KPIs)
                    if all(key in thresholds for key in ['target', 'warning', 'critical']):
                        target = thresholds['target']
                        warning = thresholds['warning']
                        critical = thresholds['critical']
                        
                        if isinstance(target, (int, float)) and isinstance(warning, (int, float)) and isinstance(critical, (int, float)):
                            # For performance KPIs (higher is better)
                            if kpi_config.get('category') in ['availability', 'performance']:
                                if not (target >= warning >= critical):
                                    self.validation_warnings.append(
                                        f"KPI {kpi_id} thresholds should follow target >= warning >= critical "
                                        f"for performance metrics, got: target={target}, warning={warning}, critical={critical}"
                                    )
                
                # Validate data source requirements
                if 'data_sources' in kpi_config:
                    data_sources = kpi_config['data_sources']
                    if isinstance(data_sources, list) and len(data_sources) == 0:
                        self.validation_errors.append(f"KPI {kpi_id} has empty data_sources list")
                    elif isinstance(data_sources, str) and not data_sources.strip():
                        self.validation_errors.append(f"KPI {kpi_id} has empty data_sources string")
                
                # Validate calculation method compatibility
                calc_method = kpi_config.get('calculation_method')
                output_format = kpi_config.get('output_format')
                
                if calc_method == 'percentage' and output_format not in ['percentage', 'decimal']:
                    self.validation_warnings.append(
                        f"KPI {kpi_id} uses percentage calculation but output format is {output_format}. "
                        "Consider using 'percentage' or 'decimal' output format."
                    )
    
    def _validate_cross_references(self, config: Dict[str, Any]) -> None:
        """Validate cross-references between different sections"""
        self.logger.info("[LINK] Validating cross-references...")
        
        column_mappings = config.get('column_mappings', {})
        kpis = config.get('kpis', {})
        
        # Check if KPIs reference valid column mappings
        for kpi_id, kpi_config in kpis.items():
            # Check data sources references
            if 'data_sources' in kpi_config:
                data_sources = kpi_config['data_sources']
                if isinstance(data_sources, list):
                    for source in data_sources:
                        if isinstance(source, str) and source not in column_mappings:
                            self.validation_warnings.append(
                                f"KPI {kpi_id} references unknown data source: {source}"
                            )
            
            # Check calculation dependencies
            if 'calculation' in kpi_config:
                calculation = kpi_config['calculation']
                if isinstance(calculation, dict):
                    # Check for field references in calculation
                    for calc_step in calculation.values():
                        if isinstance(calc_step, dict) and 'fields' in calc_step:
                            fields = calc_step['fields']
                            if isinstance(fields, list):
                                for field in fields:
                                    if field not in column_mappings:
                                        self.validation_warnings.append(
                                            f"KPI {kpi_id} calculation references unknown field: {field}"
                                        )
        
        # Validate geographic configuration consistency
        if 'geographic' in config:
            geographic = config['geographic']
            if 'enabled' in geographic and geographic['enabled']:
                # Check if required geographic fields are mapped
                required_geo_fields = geographic.get('required_fields', [])
                for field in required_geo_fields:
                    if field not in column_mappings:
                        self.validation_errors.append(
                            f"Geographic analysis enabled but required field not mapped: {field}"
                        )
    
    def _validate_data_compatibility(self, config: Dict[str, Any], data_file: str) -> None:
        """Validate that configuration is compatible with actual data"""
        self.logger.info(f"[CHART] Validating data compatibility with {data_file}...")
        
        try:
            # Load data file
            data_path = Path(data_file)
            if not data_path.exists():
                self.validation_errors.append(f"Data file not found: {data_file}")
                return
            
            # Try to read the data file
            if data_path.suffix.lower() == '.csv':
                df = pd.read_csv(data_path, nrows=1)  # Just read header
            elif data_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(data_path, nrows=1)  # Just read header
            else:
                self.validation_warnings.append(f"Unsupported data file format: {data_path.suffix}")
                return
            
            # Get available columns
            available_columns = set(df.columns)
            self.validation_info.append(f"Data file has {len(available_columns)} columns")
            
            # Check column mappings
            column_mappings = config.get('column_mappings', {})
            mapped_columns = set(column_mappings.values())
            
            # Find missing columns
            missing_columns = mapped_columns - available_columns
            if missing_columns:
                self.validation_errors.append(
                    f"Mapped columns not found in data: {sorted(missing_columns)}"
                )
            
            # Find unmapped columns
            unmapped_columns = available_columns - mapped_columns
            if unmapped_columns:
                self.validation_info.append(
                    f"Available unmapped columns: {sorted(unmapped_columns)}"
                )
            
            # Validate date fields
            date_patterns = self.validation_rules['date_field_patterns']
            potential_date_columns = []
            for col in available_columns:
                for pattern in date_patterns:
                    if re.search(pattern, col.lower()):
                        potential_date_columns.append(col)
                        break
            
            if potential_date_columns:
                self.validation_info.append(
                    f"Potential date columns detected: {potential_date_columns}"
                )
            
            # Check for essential columns
            essential_patterns = ['priority', 'state', 'status', 'category', 'group']
            found_essential = []
            for pattern in essential_patterns:
                for col in available_columns:
                    if pattern.lower() in col.lower():
                        found_essential.append(col)
                        break
            
            self.validation_info.append(f"Essential columns found: {found_essential}")
            
        except Exception as e:
            self.validation_errors.append(f"Data compatibility check failed: {e}")
    
    def _compile_validation_results(self, validation_passed: bool, exception: Optional[str] = None) -> Dict[str, Any]:
        """Compile all validation results into a structured format"""
        return {
            'validation_passed': validation_passed,
            'timestamp': datetime.now().isoformat(),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'info': self.validation_info,
            'summary': {
                'total_errors': len(self.validation_errors),
                'total_warnings': len(self.validation_warnings),
                'total_info': len(self.validation_info)
            },
            'exception': exception
        }
    
    def generate_validation_report(self, validation_result: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate a comprehensive validation report"""
        
        report = f"""
# Configuration Validation Report

**Generated:** {validation_result['timestamp']}
**Overall Status:** {'[CHECKMARK] PASSED' if validation_result['validation_passed'] else '[X] FAILED'}

## Summary

- **Errors:** {validation_result['summary']['total_errors']} (Must fix)
- **Warnings:** {validation_result['summary']['total_warnings']} (Should fix)  
- **Information:** {validation_result['summary']['total_info']} (For reference)

"""
        
        # Add errors section
        if validation_result['errors']:
            report += "## [X] Errors (Must Fix)\n\n"
            for i, error in enumerate(validation_result['errors'], 1):
                report += f"{i}. {error}\n"
            report += "\n"
        
        # Add warnings section  
        if validation_result['warnings']:
            report += "## [WARNING] Warnings (Should Fix)\n\n"
            for i, warning in enumerate(validation_result['warnings'], 1):
                report += f"{i}. {warning}\n"
            report += "\n"
        
        # Add info section
        if validation_result['info']:
            report += "## Information\n\n"
            for i, info in enumerate(validation_result['info'], 1):
                report += f"{i}. {info}\n"
            report += "\n"
        
        # Add next steps
        report += "## [LIGHTBULB] Next Steps\n\n"
        if validation_result['validation_passed']:
            report += "- Configuration is valid and ready for use\n"
            report += "- Consider addressing any warnings for optimal performance\n"
            report += "- Test with actual data using the --check-data option\n"
        else:
            report += "- Fix all errors listed above\n"
            report += "- Re-run validation to confirm fixes\n"
            report += "- Address warnings for better reliability\n"
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"[DOCUMENT] Validation report saved to {output_file}")
        
        return report

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Validate KPI processing configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', 
        required=True, 
        help="Path to the YAML configuration file"
    )
    parser.add_argument(
        '--strict', 
        action='store_true', 
        help="Enable strict validation mode"
    )
    parser.add_argument(
        '--check-data', 
        help="Path to data file for compatibility checking"
    )
    parser.add_argument(
        '--output', 
        help="Output file for validation results (JSON format)"
    )
    parser.add_argument(
        '--report', 
        help="Output file for validation report (Markdown format)"
    )
    
    args = parser.parse_args()
    
    print(f"[SEARCH] CONFIGURATION VALIDATION")
    print(f"Configuration: {args.config}")
    if args.check_data:
        print(f"Data file: {args.check_data}")
    print(f"Strict mode: {args.strict}")
    print("-" * 50)
    
    # Create validator
    validator = ConfigurationValidator(strict_mode=args.strict)
    
    # Run validation
    result = validator.validate_configuration(args.config, args.check_data)
    
    # Save JSON results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"[DOCUMENT] JSON results saved to {args.output}")
    
    # Generate and save report
    report = validator.generate_validation_report(result, args.report)
    if not args.report:
        print("\n" + report)
    
    # Exit with appropriate code
    if result['validation_passed']:
        print("[CHECKMARK] Validation completed successfully")
        return 0
    else:
        print("[X] Validation failed - see errors above")
        return 1

if __name__ == "__main__":
    exit(main())
