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
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _define_validation_rules(self) -> Dict[str, Any]:
        """Define comprehensive validation rules"""
        return {
            'numeric_ranges': {
                'targets': {'min': 0, 'max': 1000},
                'thresholds': {'min': 1, 'max': 365},
                'weights': {'min': 0, 'max': 100},
                'percentages': {'min': 0.0, 'max': 100.0}
            },
            'required_kpi_fields': {
                'SM001': ['name', 'targets', 'required_fields', 'calculation'],
                'SM002': ['name', 'targets', 'required_fields', 'calculation', 'backlog_logic'],
                'SM004': ['name', 'targets', 'required_fields', 'calculation']
            },
            'business_logic': {
                'p1_incidents_should_be_zero': True,
                'aging_threshold_max_days': 60,
                'ftf_rate_reasonable_min': 20.0,
                'major_incident_levels_valid': [1, 2, 3]
            }
        }
    
    def validate_configuration(self, config_file: str, data_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive configuration validation
        
        Args:
            config_file: Path to YAML configuration file
            data_file: Optional path to CSV data file for field validation
            
        Returns:
            Validation results with errors, warnings, and info
        """
        self.logger.info(f"🔍 Validating configuration: {config_file}")
        
        # Reset validation state
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_info = []
        
        try:
            # Load configuration
            config = self._load_and_parse_config(config_file)
            if not config:
                return self._build_validation_result(False)
            
            # Schema validation
            self._validate_schema(config)
            
            # Content validation
            self._validate_content(config)
            
            # Business rules validation
            self._validate_business_rules(config)
            
            # Cross-reference validation
            self._validate_cross_references(config)
            
            # Data compatibility validation (if data file provided)
            if data_file:
                self._validate_data_compatibility(config, data_file)
            
            # Calculate overall validation result
            validation_passed = len(self.validation_errors) == 0
            if self.strict_mode:
                validation_passed = validation_passed and len(self.validation_warnings) == 0
            
            result = self._build_validation_result(validation_passed)
            
            # Log summary
            if validation_passed:
                self.logger.info("✅ Configuration validation PASSED")
            else:
                self.logger.warning("❌ Configuration validation FAILED")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed with exception: {e}")
            self.validation_errors.append(f"Validation exception: {str(e)}")
            return self._build_validation_result(False)
    
    def _load_and_parse_config(self, config_file: str) -> Optional[Dict[str, Any]]:
        """Load and parse YAML configuration file"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                self.validation_errors.append(f"Configuration file not found: {config_file}")
                return None
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config:
                self.validation_errors.append("Configuration file is empty or invalid YAML")
                return None
            
            self.validation_info.append(f"Successfully loaded configuration with {len(config)} top-level sections")
            return config
            
        except yaml.YAMLError as e:
            self.validation_errors.append(f"YAML parsing error: {str(e)}")
            return None
        except Exception as e:
            self.validation_errors.append(f"Error loading configuration: {str(e)}")
            return None
    
    def _validate_schema(self, config: Dict[str, Any]):
        """Validate configuration schema structure"""
        self.logger.info("📋 Validating configuration schema...")
        
        # Check required top-level sections
        for section, required_fields in self.required_sections.items():
            if section not in config:
                self.validation_errors.append(f"Missing required section: {section}")
                continue
            
            # Check required fields within sections
            section_data = config[section]
            if not isinstance(section_data, dict):
                self.validation_errors.append(f"Section '{section}' must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in section_data:
                    self.validation_errors.append(f"Missing required field '{field}' in section '{section}'")
        
        # Validate metadata section
        if 'metadata' in config:
            metadata = config['metadata']
            required_metadata = ['version', 'organization', 'schema_version']
            for field in required_metadata:
                if field not in metadata:
                    self.validation_errors.append(f"Missing required metadata field: {field}")
        
        # Validate KPIs section structure
        if 'kpis' in config:
            self._validate_kpis_schema(config['kpis'])
        
        self.validation_info.append("Schema validation completed")
    
    def _validate_kpis_schema(self, kpis: Dict[str, Any]):
        """Validate KPIs section schema"""
        for kpi_id, kpi_config in kpis.items():
            if not isinstance(kpi_config, dict):
                self.validation_errors.append(f"KPI '{kpi_id}' configuration must be a dictionary")
                continue
            
            # Check required KPI fields
            required_kpi_fields = self.validation_rules['required_kpi_fields'].get(kpi_id, [])
            for field in required_kpi_fields:
                if field not in kpi_config:
                    self.validation_errors.append(f"KPI '{kpi_id}' missing required field: {field}")
            
            # Validate targets structure
            if 'targets' in kpi_config and isinstance(kpi_config['targets'], dict):
                self._validate_targets(kpi_id, kpi_config['targets'])
            
            # Validate required_fields is a list
            if 'required_fields' in kpi_config:
                if not isinstance(kpi_config['required_fields'], list):
                    self.validation_errors.append(f"KPI '{kpi_id}' required_fields must be a list")
    
    def _validate_targets(self, kpi_id: str, targets: Dict[str, Any]):
        """Validate KPI targets"""
        numeric_ranges = self.validation_rules['numeric_ranges']
        
        for target_name, target_value in targets.items():
            if target_value is None:
                continue  # Null values are allowed
            
            # Validate numeric targets
            if isinstance(target_value, (int, float)):
                if '_max' in target_name:
                    if target_value < numeric_ranges['targets']['min']:
                        self.validation_errors.append(
                            f"KPI '{kpi_id}' target '{target_name}' value {target_value} below minimum {numeric_ranges['targets']['min']}"
                        )
                    if target_value > numeric_ranges['targets']['max']:
                        self.validation_warnings.append(
                            f"KPI '{kpi_id}' target '{target_name}' value {target_value} seems high (>{numeric_ranges['targets']['max']})"
                        )
                
                elif '_min' in target_name:
                    if target_value < 0:
                        self.validation_errors.append(f"KPI '{kpi_id}' minimum target '{target_name}' cannot be negative")
                    if target_value > 100 and 'rate' in target_name:
                        self.validation_errors.append(f"KPI '{kpi_id}' rate target '{target_name}' cannot exceed 100%")
    
    def _validate_content(self, config: Dict[str, Any]):
        """Validate configuration content and values"""
        self.logger.info("📊 Validating configuration content...")
        
        # Validate thresholds
        if 'thresholds' in config:
            self._validate_thresholds(config['thresholds'])
        
        # Validate processing configuration
        if 'processing' in config:
            self._validate_processing_config(config['processing'])
        
        # Validate column mappings
        if 'column_mappings' in config:
            self._validate_column_mappings(config['column_mappings'])
        
        self.validation_info.append("Content validation completed")
    
    def _validate_thresholds(self, thresholds: Dict[str, Any]):
        """Validate threshold values"""
        if 'aging' in thresholds:
            aging = thresholds['aging']
            for threshold_name, value in aging.items():
                if isinstance(value, (int, float)):
                    if value < 1:
                        self.validation_errors.append(f"Aging threshold '{threshold_name}' must be at least 1 day")
                    if value > 365:
                        self.validation_warnings.append(f"Aging threshold '{threshold_name}' ({value} days) seems very long")
        
        if 'priority' in thresholds:
            priority = thresholds['priority']
            if 'major_incident_levels' in priority:
                levels = priority['major_incident_levels']
                if not isinstance(levels, list) or not all(isinstance(x, int) for x in levels):
                    self.validation_errors.append("major_incident_levels must be a list of integers")
                elif not all(1 <= x <= 5 for x in levels):
                    self.validation_warnings.append("major_incident_levels contains unusual priority values (expected 1-5)")
    
    def _validate_processing_config(self, processing: Dict[str, Any]):
        """Validate processing configuration"""
        if 'priority_extraction' in processing:
            priority_config = processing['priority_extraction']
            if 'regex_pattern' in priority_config:
                try:
                    re.compile(priority_config['regex_pattern'])
                except re.error as e:
                    self.validation_errors.append(f"Invalid regex pattern in priority_extraction: {e}")
        
        if 'date_parsing' in processing:
            date_config = processing['date_parsing']
            if 'formats' in date_config and isinstance(date_config['formats'], list):
                for fmt in date_config['formats']:
                    try:
                        datetime.strptime("2025-01-01 12:00:00", fmt)
                    except ValueError:
                        self.validation_warnings.append(f"Date format '{fmt}' may not work with test date")
    
    def _validate_column_mappings(self, column_mappings: Dict[str, str]):
        """Validate column mappings"""
        if not isinstance(column_mappings, dict):
            self.validation_errors.append("column_mappings must be a dictionary")
            return
        
        # Check for empty mappings
        empty_mappings = [(k, v) for k, v in column_mappings.items() if not v or not v.strip()]
        if empty_mappings:
            self.validation_warnings.append(f"Empty column mappings found: {empty_mappings}")
        
        # Check for duplicate target columns
        target_columns = list(column_mappings.values())
        duplicates = [col for col in target_columns if target_columns.count(col) > 1]
        if duplicates:
            self.validation_errors.append(f"Duplicate target columns in mappings: {set(duplicates)}")
    
    def _validate_business_rules(self, config: Dict[str, Any]):
        """Validate business logic rules"""
        self.logger.info("🏢 Validating business rules...")
        
        kpis = config.get('kpis', {})
        business_rules = self.validation_rules['business_logic']
        
        # Rule: P1 incidents should have zero tolerance
        if 'SM001' in kpis and business_rules['p1_incidents_should_be_zero']:
            sm001_targets = kpis['SM001'].get('targets', {})
            if sm001_targets.get('p1_max', 0) > 0:
                self.validation_warnings.append("SM001: P1 incidents target is not zero - consider zero-tolerance policy")
        
        # Rule: Aging thresholds should be reasonable
        thresholds = config.get('thresholds', {})
        if 'aging' in thresholds:
            aging = thresholds['aging']
            max_reasonable_days = business_rules['aging_threshold_max_days']
            for threshold_name, days in aging.items():
                if isinstance(days, (int, float)) and days > max_reasonable_days:
                    self.validation_warnings.append(f"Aging threshold '{threshold_name}' ({days} days) exceeds reasonable maximum ({max_reasonable_days} days)")
        
        # Rule: First-time fix rate should be achievable
        if 'SM004' in kpis:
            sm004_targets = kpis['SM004'].get('targets', {})
            ftf_min = sm004_targets.get('ftf_rate_min', 0)
            reasonable_min = business_rules['ftf_rate_reasonable_min']
            if ftf_min < reasonable_min:
                self.validation_warnings.append(f"SM004: First-time fix target {ftf_min}% may be too low (consider minimum {reasonable_min}%)")
            if ftf_min > 95:
                self.validation_warnings.append(f"SM004: First-time fix target {ftf_min}% may be unrealistically high")
        
        # Rule: Major incident priority levels should be valid
        if 'priority' in thresholds:
            major_levels = thresholds['priority'].get('major_incident_levels', [])
            valid_levels = business_rules['major_incident_levels_valid']
            invalid_levels = [level for level in major_levels if level not in valid_levels]
            if invalid_levels:
                self.validation_warnings.append(f"Unusual major incident priority levels: {invalid_levels} (expected from {valid_levels})")
        
        self.validation_info.append("Business rules validation completed")
    
    def _validate_cross_references(self, config: Dict[str, Any]):
        """Validate cross-references between configuration sections"""
        self.logger.info("🔗 Validating cross-references...")
        
        column_mappings = config.get('column_mappings', {})
        kpis = config.get('kpis', {})
        
        # Check that required fields for each KPI are available in column mappings
        for kpi_id, kpi_config in kpis.items():
            if not kpi_config.get('enabled', True):
                continue
            
            required_fields = kpi_config.get('required_fields', [])
            missing_mappings = []
            
            for field in required_fields:
                if field not in column_mappings:
                    missing_mappings.append(field)
            
            if missing_mappings:
                self.validation_errors.append(f"KPI '{kpi_id}' requires fields not in column_mappings: {missing_mappings}")
        
        # Validate KPI weight consistency
        if 'global_status_rules' in config:
            self._validate_kpi_weights(config['global_status_rules'], kpis)
        
        self.validation_info.append("Cross-reference validation completed")
    
    def _validate_kpi_weights(self, global_rules: Dict[str, Any], kpis: Dict[str, Any]):
        """Validate KPI weight consistency"""
        if 'scorecard_scoring' not in global_rules:
            return
        
        scoring = global_rules['scorecard_scoring']
        enabled_kpis = [kpi_id for kpi_id, kpi_config in kpis.items() if kpi_config.get('enabled', True)]
        
        # Check if SM003 is enabled for weight calculation
        sm003_enabled = 'SM003' in enabled_kpis
        
        if sm003_enabled:
            expected_weights = ['weight_sm001', 'weight_sm002', 'weight_sm003', 'weight_sm004']
        else:
            expected_weights = ['weight_sm001', 'weight_sm002', 'weight_sm004']
            # Use disabled weights if available
            if 'sm003_disabled_weights' in scoring:
                scoring = scoring['sm003_disabled_weights']
        
        # Check that all expected weights are present
        missing_weights = [weight for weight in expected_weights if weight not in scoring]
        if missing_weights:
            self.validation_errors.append(f"Missing KPI weights in scorecard_scoring: {missing_weights}")
        
        # Check that weights sum to 100
        total_weight = sum(scoring.get(weight, 0) for weight in expected_weights if weight in scoring)
        if abs(total_weight - 100) > 0.1:  # Allow small floating point differences
            self.validation_errors.append(f"KPI weights sum to {total_weight}% instead of 100%")
    
    def _validate_data_compatibility(self, config: Dict[str, Any], data_file: str):
        """Validate configuration compatibility with actual data"""
        self.logger.info(f"📊 Validating data compatibility with {data_file}...")
        
        try:
            # Load data file
            df = pd.read_csv(data_file)
            actual_columns = set(df.columns)
            
            # Check column mappings
            column_mappings = config.get('column_mappings', {})
            mapped_columns = set(column_mappings.values())
            
            # Find missing columns
            missing_columns = mapped_columns - actual_columns
            if missing_columns:
                self.validation_errors.append(f"Data file missing columns required by configuration: {list(missing_columns)}")
            
            # Find extra columns in data
            extra_columns = actual_columns - mapped_columns
            if extra_columns:
                self.validation_info.append(f"Data file has additional columns not in configuration: {list(extra_columns)[:5]}{'...' if len(extra_columns) > 5 else ''}")
            
            # Validate data format compatibility
            self._validate_data_formats(df, config)
            
            # Check KPI data requirements
            self._validate_kpi_data_requirements(df, config)
            
        except Exception as e:
            self.validation_errors.append(f"Error validating data compatibility: {str(e)}")
    
    def _validate_data_formats(self, df: pd.DataFrame, config: Dict[str, Any]):
        """Validate data format compatibility"""
        column_mappings = config.get('column_mappings', {})
        
        # Check priority format
        if 'priority' in column_mappings and column_mappings['priority'] in df.columns:
            priority_col = column_mappings['priority']
            sample_priorities = df[priority_col].dropna().head(10)
            
            processing_config = config.get('processing', {})
            regex_pattern = processing_config.get('priority_extraction', {}).get('regex_pattern', r'\d+')
            
            try:
                pattern = re.compile(regex_pattern)
                non_matching = []
                for priority in sample_priorities:
                    if not pattern.search(str(priority)):
                        non_matching.append(priority)
                
                if non_matching:
                    self.validation_warnings.append(f"Some priority values may not match extraction pattern '{regex_pattern}': {non_matching[:3]}")
            except re.error:
                pass  # Already caught in processing config validation
        
        # Check date format
        date_fields = ['opened_at', 'resolved_at', 'closed_at']
        for field in date_fields:
            if field in column_mappings and column_mappings[field] in df.columns:
                date_col = column_mappings[field]
                sample_dates = df[date_col].dropna().head(5)
                
                for date_val in sample_dates:
                    try:
                        pd.to_datetime(date_val)
                    except:
                        self.validation_warnings.append(f"Date format in column '{date_col}' may not be parseable: example '{date_val}'")
                        break
        
        # Check numeric fields
        numeric_fields = ['reassignment_count']
        for field in numeric_fields:
            if field in column_mappings and column_mappings[field] in df.columns:
                numeric_col = column_mappings[field]
                if not pd.api.types.is_numeric_dtype(df[numeric_col]):
                    non_numeric_samples = df[numeric_col].dropna().head(3)
                    self.validation_warnings.append(f"Column '{numeric_col}' expected to be numeric but contains: {list(non_numeric_samples)}")
    
    def _validate_kpi_data_requirements(self, df: pd.DataFrame, config: Dict[str, Any]):
        """Validate that data supports configured KPIs"""
        column_mappings = config.get('column_mappings', {})
        kpis = config.get('kpis', {})
        
        for kpi_id, kpi_config in kpis.items():
            if not kpi_config.get('enabled', True):
                continue
            
            required_fields = kpi_config.get('required_fields', [])
            missing_for_kpi = []
            
            for field in required_fields:
                if field not in column_mappings:
                    missing_for_kpi.append(field)
                elif column_mappings[field] not in df.columns:
                    missing_for_kpi.append(f"{field} (mapped to '{column_mappings[field]}')")
            
            if missing_for_kpi:
                if kpi_config.get('data_requirements', {}).get('fallback_behavior') == 'disable':
                    self.validation_warnings.append(f"KPI '{kpi_id}' missing required data fields and will be disabled: {missing_for_kpi}")
                else:
                    self.validation_errors.append(f"KPI '{kpi_id}' missing required data fields: {missing_for_kpi}")
    
    def _build_validation_result(self, validation_passed: bool) -> Dict[str, Any]:
        """Build comprehensive validation result"""
        return {
            'validation_passed': validation_passed,
            'validation_timestamp': datetime.now().isoformat(),
            'strict_mode': self.strict_mode,
            'summary': {
                'total_errors': len(self.validation_errors),
                'total_warnings': len(self.validation_warnings),
                'total_info': len(self.validation_info)
            },
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'info': self.validation_info,
            'recommendation': self._get_validation_recommendation()
        }
    
    def _get_validation_recommendation(self) -> str:
        """Get validation recommendation based on results"""
        if len(self.validation_errors) > 0:
            return "CRITICAL: Fix all errors before using configuration"
        elif len(self.validation_warnings) > 5:
            return "WARNING: Consider addressing warnings for optimal performance"
        elif len(self.validation_warnings) > 0:
            return "MINOR: Configuration is usable but has minor issues"
        else:
            return "EXCELLENT: Configuration is fully validated and ready for use"
    
    def generate_validation_report(self, validation_result: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate human-readable validation report"""
        report = f"""
# Configuration Validation Report
Generated: {validation_result['validation_timestamp']}
Strict Mode: {'Enabled' if validation_result['strict_mode'] else 'Disabled'}

## Summary
Overall Status: {'✅ PASSED' if validation_result['validation_passed'] else '❌ FAILED'}
Recommendation: {validation_result['recommendation']}

- Errors: {validation_result['summary']['total_errors']}
- Warnings: {validation_result['summary']['total_warnings']}  
- Info Messages: {validation_result['summary']['total_info']}

"""
        
        # Add errors section
        if validation_result['errors']:
            report += "## ❌ Errors (Must Fix)\n\n"
            for i, error in enumerate(validation_result['errors'], 1):
                report += f"{i}. {error}\n"
            report += "\n"
        
        # Add warnings section
        if validation_result['warnings']:
            report += "## ⚠️ Warnings (Should Fix)\n\n"
            for i, warning in enumerate(validation_result['warnings'], 1):
                report += f"{i}. {warning}\n"
            report += "\n"
        
        # Add info section
        if validation_result['info']:
            report += "## ℹ️ Information\n\n"
            for i, info in enumerate(validation_result['info'], 1):
                report += f"{i}. {info}\n"
            report += "\n"
        
        # Add recommendations
        report += "## 💡 Next Steps\n\n"
        if validation_result['validation_passed']:
            report += "- Configuration is ready for use\n"
            report += "- Consider addressing any warnings for optimal performance\n"
            report += "- Test with actual data to verify functionality\n"
        else:
            report += "- Fix all errors before using configuration\n"
            report += "- Review warnings and address as needed\n"
            report += "- Re-run validation after making changes\n"
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            self.logger.info(f"📄 Validation report saved to {output_file}")
        
        return report


def main():
    """Command line interface for configuration validation"""
    parser = argparse.ArgumentParser(description='Validate KPI Configuration Files')
    parser.add_argument('--config', required=True, help='YAML configuration file to validate')
    parser.add_argument('--data', help='CSV data file to check compatibility')
    parser.add_argument('--strict', action='store_true', help='Enable strict validation mode')
    parser.add_argument('--output', help='Output file for validation report')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ConfigurationValidator(strict_mode=args.strict)
    
    print(f"CONFIGURATION VALIDATION")
    print(f"Configuration: {args.config}")
    print(f"Strict Mode: {'Enabled' if args.strict else 'Disabled'}")
    if args.data:
        print(f"Data File: {args.data}")
    print("="*50)
    
    # Run validation
    result = validator.validate_configuration(args.config, args.data)
    
    # Output results
    if args.json:
        json_output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"📄 JSON results saved to {args.output}")
        else:
            print(json_output)
    else:
        # Generate and display report
        report = validator.generate_validation_report(result, args.output)
        if not args.output:
            print(report)
    
    # Set exit code based on validation result
    if result['validation_passed']:
        print("✅ Validation completed successfully")
        return 0
    else:
        print("❌ Validation failed - see errors above")
        return 1


if __name__ == "__main__":
    exit(main())