#!/usr/bin/env python3
"""
Data Validation Utility for KPI Processing System
================================================

Comprehensive data validation tool that checks CSV data files for:
- Format compliance
- Required columns
- Data quality issues
- Statistical anomalies
- Processing readiness
"""

import pandas as pd
import yaml
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
import numpy as np

class DataValidator:
    """Validate CSV data files for KPI processing"""
    
    def __init__(self, config_file: str = "config/kpi_config.yaml"):
        self.config_file = config_file
        self.config = {}
        self.validation_results = {}
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
        self.load_configuration()
    
    def load_configuration(self):
        """Load KPI configuration"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {self.config_file}")
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
    
    def validate_data_file(self, data_file: str, quick_check: bool = False) -> Dict[str, Any]:
        """Validate a single data file"""
        print(f"\n🔍 Validating Data File: {data_file}")
        print("="*60)
        
        data_path = Path(data_file)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        # Initialize validation results
        self.validation_results = {
            'file_info': {},
            'structure_check': {},
            'column_analysis': {},
            'data_quality': {},
            'kpi_readiness': {},
            'statistical_summary': {},
            'overall_status': 'unknown'
        }
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
        try:
            # Step 1: File information
            self.check_file_info(data_path)
            
            # Step 2: Load and check structure
            df = self.load_and_check_structure(data_path)
            
            if df is not None:
                # Step 3: Column analysis
                self.analyze_columns(df)
                
                # Step 4: Data quality checks
                self.check_data_quality(df, quick_check)
                
                # Step 5: KPI readiness assessment
                self.assess_kpi_readiness(df)
                
                # Step 6: Statistical summary (if not quick check)
                if not quick_check:
                    self.generate_statistical_summary(df)
            
            # Step 7: Generate overall assessment
            self.generate_overall_assessment()
            
        except Exception as e:
            self.issues.append({
                'category': 'Critical Error',
                'severity': 'critical',
                'message': f"Validation failed: {e}",
                'recommendation': 'Check file format and accessibility'
            })
            self.validation_results['overall_status'] = 'failed'
        
        return self.validation_results
    
    def check_file_info(self, data_path: Path):
        """Check basic file information"""
        print("📄 Checking File Information...")
        
        stat = data_path.stat()
        file_info = {
            'name': data_path.name,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'age_days': round((datetime.now().timestamp() - stat.st_mtime) / (24 * 3600), 1),
            'extension': data_path.suffix.lower()
        }
        
        print(f"  📁 File: {file_info['name']}")
        print(f"  📏 Size: {file_info['size_mb']} MB")
        print(f"  📅 Modified: {file_info['modified']} ({file_info['age_days']} days ago)")
        
        # Check file extension
        if file_info['extension'] != '.csv':
            self.issues.append({
                'category': 'File Format',
                'severity': 'error',
                'message': f"Unexpected file extension: {file_info['extension']} (expected .csv)",
                'recommendation': 'Ensure file is in CSV format'
            })
        
        # Check file size
        if file_info['size_mb'] < 0.1:
            self.warnings.append({
                'category': 'File Size',
                'severity': 'warning',
                'message': f"Very small file size: {file_info['size_mb']} MB",
                'recommendation': 'Verify file contains sufficient data'
            })
        elif file_info['size_mb'] > 100:
            self.warnings.append({
                'category': 'File Size',
                'severity': 'warning',
                'message': f"Large file size: {file_info['size_mb']} MB",
                'recommendation': 'Processing may take longer than usual'
            })
        
        # Check file age
        if file_info['age_days'] > 30:
            self.warnings.append({
                'category': 'Data Freshness',
                'severity': 'warning',
                'message': f"Data file is {file_info['age_days']} days old",
                'recommendation': 'Consider using more recent data'
            })
        
        self.validation_results['file_info'] = file_info
    
    def load_and_check_structure(self, data_path: Path) -> Optional[pd.DataFrame]:
        """Load CSV file and check basic structure"""
        print("🏗️  Checking File Structure...")
        
        structure_check = {
            'readable': False,
            'row_count': 0,
            'column_count': 0,
            'columns': [],
            'encoding': 'unknown',
            'separator': 'unknown',
            'has_header': False
        }
        
        try:
            # Try to detect encoding and separator
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separators_to_try = [',', ';', '\t', '|']
            
            df = None
            for encoding in encodings_to_try:
                for separator in separators_to_try:
                    try:
                        df_test = pd.read_csv(data_path, encoding=encoding, sep=separator, nrows=5)
                        if len(df_test.columns) > 1:  # Reasonable number of columns
                            df = pd.read_csv(data_path, encoding=encoding, sep=separator)
                            structure_check['encoding'] = encoding
                            structure_check['separator'] = separator
                            break
                    except:
                        continue
                if df is not None:
                    break
            
            if df is None:
                # Fallback to basic read
                df = pd.read_csv(data_path)
                structure_check['encoding'] = 'default'
                structure_check['separator'] = 'default'
            
            structure_check['readable'] = True
            structure_check['row_count'] = len(df)
            structure_check['column_count'] = len(df.columns)
            structure_check['columns'] = list(df.columns)
            structure_check['has_header'] = True  # Assume header if readable
            
            print(f"  ✅ File loaded successfully")
            print(f"  📊 Dimensions: {structure_check['row_count']:,} rows × {structure_check['column_count']} columns")
            print(f"  🔤 Encoding: {structure_check['encoding']}")
            print(f"  ➖ Separator: '{structure_check['separator']}'")
            
            # Check for reasonable dimensions
            if structure_check['row_count'] < 10:
                self.warnings.append({
                    'category': 'Data Volume',
                    'severity': 'warning',
                    'message': f"Very few rows: {structure_check['row_count']}",
                    'recommendation': 'Verify this is the complete dataset'
                })
            
            if structure_check['column_count'] < 5:
                self.warnings.append({
                    'category': 'Data Structure',
                    'severity': 'warning',
                    'message': f"Few columns: {structure_check['column_count']}",
                    'recommendation': 'Check if all required columns are present'
                })
            elif structure_check['column_count'] > 50:
                self.warnings.append({
                    'category': 'Data Structure',
                    'severity': 'info',
                    'message': f"Many columns: {structure_check['column_count']}",
                    'recommendation': 'Processing will focus on mapped columns only'
                })
            
        except Exception as e:
            structure_check['readable'] = False
            self.issues.append({
                'category': 'File Structure',
                'severity': 'critical',
                'message': f"Cannot read CSV file: {e}",
                'recommendation': 'Check file format, encoding, and separators'
            })
            df = None
        
        self.validation_results['structure_check'] = structure_check
        return df
    
    def analyze_columns(self, df: pd.DataFrame):
        """Analyze column structure and mapping"""
        print("🔍 Analyzing Columns...")
        
        column_analysis = {
            'total_columns': len(df.columns),
            'mapped_columns': {},
            'unmapped_columns': [],
            'missing_required': [],
            'column_types': {},
            'mapping_coverage': 0.0
        }
        
        # Get column mappings from configuration
        column_mappings = self.config.get('column_mappings', {})
        
        # Check which columns are mapped
        mapped_count = 0
        for internal_name, csv_column in column_mappings.items():
            if csv_column in df.columns:
                column_analysis['mapped_columns'][internal_name] = {
                    'csv_column': csv_column,
                    'present': True,
                    'null_count': df[csv_column].isnull().sum(),
                    'null_percentage': round((df[csv_column].isnull().sum() / len(df)) * 100, 1),
                    'data_type': str(df[csv_column].dtype)
                }
                mapped_count += 1
                print(f"  ✅ {internal_name:<15} → {csv_column}")
            else:
                column_analysis['mapped_columns'][internal_name] = {
                    'csv_column': csv_column,
                    'present': False
                }
                column_analysis['missing_required'].append(internal_name)
                print(f"  ❌ {internal_name:<15} → {csv_column} (MISSING)")
        
        # Identify unmapped columns
        mapped_csv_columns = [info.get('csv_column') for info in column_analysis['mapped_columns'].values()]
        for col in df.columns:
            if col not in mapped_csv_columns:
                column_analysis['unmapped_columns'].append(col)
                print(f"  ➖ {col} (unmapped)")
        
        column_analysis['mapping_coverage'] = round((mapped_count / len(column_mappings)) * 100, 1)
        
        print(f"  📊 Mapping Coverage: {column_analysis['mapping_coverage']}% ({mapped_count}/{len(column_mappings)})")
        
        # Check for critical missing columns
        if column_analysis['missing_required']:
            self.issues.append({
                'category': 'Column Mapping',
                'severity': 'error',
                'message': f"Missing required columns: {', '.join(column_analysis['missing_required'])}",
                'recommendation': 'Update column mappings or provide missing data'
            })
        
        # Check for high null percentages
        for internal_name, info in column_analysis['mapped_columns'].items():
            if info.get('present') and info.get('null_percentage', 0) > 50:
                self.warnings.append({
                    'category': 'Data Quality',
                    'severity': 'warning',
                    'message': f"High null percentage in {internal_name}: {info['null_percentage']}%",
                    'recommendation': 'Review data completeness for this field'
                })
        
        self.validation_results['column_analysis'] = column_analysis
    
    def check_data_quality(self, df: pd.DataFrame, quick_check: bool = False):
        """Check data quality issues"""
        print("🔍 Checking Data Quality...")
        
        quality_check = {
            'duplicate_rows': 0,
            'empty_rows': 0,
            'data_type_issues': [],
            'format_issues': [],
            'value_range_issues': [],
            'consistency_issues': []
        }
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        quality_check['duplicate_rows'] = duplicate_count
        if duplicate_count > 0:
            print(f"  ⚠️  Duplicate rows found: {duplicate_count}")
            self.warnings.append({
                'category': 'Data Quality',
                'severity': 'warning',
                'message': f"Found {duplicate_count} duplicate rows",
                'recommendation': 'Consider removing duplicates before processing'
            })
        else:
            print(f"  ✅ No duplicate rows found")
        
        # Check for empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        quality_check['empty_rows'] = empty_rows
        if empty_rows > 0:
            print(f"  ⚠️  Empty rows found: {empty_rows}")
            self.warnings.append({
                'category': 'Data Quality',
                'severity': 'warning',
                'message': f"Found {empty_rows} completely empty rows",
                'recommendation': 'Remove empty rows before processing'
            })
        
        if not quick_check:
            # Detailed data type and format checks
            self.check_priority_format(df, quality_check)
            self.check_date_formats(df, quality_check)
            self.check_numeric_fields(df, quality_check)
            self.check_text_fields(df, quality_check)
        
        self.validation_results['data_quality'] = quality_check
    
    def check_priority_format(self, df: pd.DataFrame, quality_check: Dict):
        """Check priority field format"""
        column_mappings = self.config.get('column_mappings', {})
        priority_column = column_mappings.get('priority')
        
        if priority_column and priority_column in df.columns:
            priority_data = df[priority_column].dropna()
            if len(priority_data) > 0:
                # Check for consistent priority format
                sample_values = priority_data.value_counts().head(10)
                print(f"  🎯 Priority values sample: {dict(sample_values)}")
                
                # Check if values follow expected patterns
                numeric_pattern = re.compile(r'^\d+$')
                text_pattern = re.compile(r'^\d+\s*-\s*\w+', re.IGNORECASE)
                
                numeric_count = sum(1 for val in priority_data if numeric_pattern.match(str(val)))
                text_count = sum(1 for val in priority_data if text_pattern.match(str(val)))
                
                total_valid = numeric_count + text_count
                validity_percent = round((total_valid / len(priority_data)) * 100, 1)
                
                if validity_percent < 80:
                    quality_check['format_issues'].append({
                        'field': 'priority',
                        'issue': f'Inconsistent priority format ({validity_percent}% valid)',
                        'sample': list(sample_values.index[:3])
                    })
    
    def check_date_formats(self, df: pd.DataFrame, quality_check: Dict):
        """Check date field formats"""
        column_mappings = self.config.get('column_mappings', {})
        date_fields = ['opened_at', 'resolved_at', 'closed_at']
        
        for field in date_fields:
            column_name = column_mappings.get(field)
            if column_name and column_name in df.columns:
                date_data = df[column_name].dropna()
                if len(date_data) > 0:
                    # Try to parse dates
                    try:
                        parsed_dates = pd.to_datetime(date_data, errors='coerce')
                        valid_dates = parsed_dates.notna().sum()
                        validity_percent = round((valid_dates / len(date_data)) * 100, 1)
                        
                        print(f"  📅 {field}: {validity_percent}% valid dates")
                        
                        if validity_percent < 90:
                            quality_check['format_issues'].append({
                                'field': field,
                                'issue': f'Date parsing issues ({validity_percent}% valid)',
                                'sample': list(date_data.head(3))
                            })
                    except Exception as e:
                        quality_check['format_issues'].append({
                            'field': field,
                            'issue': f'Date format error: {e}',
                            'sample': list(date_data.head(3))
                        })
    
    def check_numeric_fields(self, df: pd.DataFrame, quality_check: Dict):
        """Check numeric field validity"""
        column_mappings = self.config.get('column_mappings', {})
        numeric_field = column_mappings.get('reassignment_count')
        
        if numeric_field and numeric_field in df.columns:
            numeric_data = df[numeric_field].dropna()
            if len(numeric_data) > 0:
                try:
                    # Try to convert to numeric
                    numeric_values = pd.to_numeric(numeric_data, errors='coerce')
                    valid_numeric = numeric_values.notna().sum()
                    validity_percent = round((valid_numeric / len(numeric_data)) * 100, 1)
                    
                    print(f"  🔢 reassignment_count: {validity_percent}% numeric values")
                    
                    if validity_percent < 95:
                        quality_check['format_issues'].append({
                            'field': 'reassignment_count',
                            'issue': f'Non-numeric values found ({validity_percent}% valid)',
                            'sample': list(numeric_data.head(3))
                        })
                    
                    # Check for reasonable ranges
                    if valid_numeric > 0:
                        max_reassignments = numeric_values.max()
                        if max_reassignments > 20:
                            quality_check['value_range_issues'].append({
                                'field': 'reassignment_count',
                                'issue': f'Unusually high reassignment count: {max_reassignments}',
                                'recommendation': 'Verify data accuracy'
                            })
                
                except Exception as e:
                    quality_check['format_issues'].append({
                        'field': 'reassignment_count',
                        'issue': f'Numeric validation error: {e}',
                        'sample': list(numeric_data.head(3))
                    })
    
    def check_text_fields(self, df: pd.DataFrame, quality_check: Dict):
        """Check text field quality"""
        column_mappings = self.config.get('column_mappings', {})
        text_fields = ['short_description', 'description', 'category']
        
        for field in text_fields:
            column_name = column_mappings.get(field)
            if column_name and column_name in df.columns:
                text_data = df[column_name].dropna()
                if len(text_data) > 0:
                    # Check for very short descriptions
                    short_descriptions = sum(1 for text in text_data if len(str(text).strip()) < 10)
                    if short_descriptions > len(text_data) * 0.3:  # More than 30%
                        quality_check['consistency_issues'].append({
                            'field': field,
                            'issue': f'Many very short descriptions ({short_descriptions}/{len(text_data)})',
                            'recommendation': 'Review description quality'
                        })
    
    def assess_kpi_readiness(self, df: pd.DataFrame):
        """Assess readiness for each KPI"""
        print("🎯 Assessing KPI Readiness...")
        
        kpi_readiness = {}
        kpis_config = self.config.get('kpis', {})
        column_mappings = self.config.get('column_mappings', {})
        
        for kpi_id, kpi_config in kpis_config.items():
            if not kpi_config.get('enabled', True):
                continue
            
            required_fields = kpi_config.get('required_fields', [])
            readiness = {
                'kpi_name': kpi_config.get('name', kpi_id),
                'required_fields': required_fields,
                'available_fields': [],
                'missing_fields': [],
                'field_coverage': 0.0,
                'data_sufficiency': 'unknown',
                'ready': False
            }
            
            # Check field availability
            for field in required_fields:
                csv_column = column_mappings.get(field)
                if csv_column and csv_column in df.columns:
                    # Check data sufficiency
                    non_null_count = df[csv_column].notna().sum()
                    sufficiency_percent = round((non_null_count / len(df)) * 100, 1)
                    
                    readiness['available_fields'].append({
                        'field': field,
                        'csv_column': csv_column,
                        'data_sufficiency': sufficiency_percent
                    })
                else:
                    readiness['missing_fields'].append(field)
            
            # Calculate readiness
            readiness['field_coverage'] = round((len(readiness['available_fields']) / len(required_fields)) * 100, 1)
            
            # Determine data sufficiency
            if readiness['available_fields']:
                min_sufficiency = min(field['data_sufficiency'] for field in readiness['available_fields'])
                if min_sufficiency >= 90:
                    readiness['data_sufficiency'] = 'excellent'
                elif min_sufficiency >= 70:
                    readiness['data_sufficiency'] = 'good'
                elif min_sufficiency >= 50:
                    readiness['data_sufficiency'] = 'fair'
                else:
                    readiness['data_sufficiency'] = 'poor'
            
            # Determine overall readiness
            readiness['ready'] = (
                readiness['field_coverage'] == 100.0 and
                readiness['data_sufficiency'] in ['excellent', 'good']
            )
            
            # Print readiness status
            status_icon = "✅" if readiness['ready'] else "❌"
            print(f"  {status_icon} {kpi_id}: {readiness['field_coverage']}% fields, {readiness['data_sufficiency']} data")
            
            kpi_readiness[kpi_id] = readiness
            
            # Add recommendations for issues
            if not readiness['ready']:
                if readiness['missing_fields']:
                    self.recommendations.append({
                        'category': 'KPI Readiness',
                        'kpi': kpi_id,
                        'message': f"Missing fields for {kpi_id}: {', '.join(readiness['missing_fields'])}",
                        'recommendation': 'Update column mappings or provide missing data'
                    })
                
                if readiness['data_sufficiency'] in ['fair', 'poor']:
                    self.recommendations.append({
                        'category': 'KPI Readiness',
                        'kpi': kpi_id,
                        'message': f"Low data quality for {kpi_id}: {readiness['data_sufficiency']}",
                        'recommendation': 'Improve data completeness for better results'
                    })
        
        self.validation_results['kpi_readiness'] = kpi_readiness
    
    def generate_statistical_summary(self, df: pd.DataFrame):
        """Generate statistical summary of the data"""
        print("📊 Generating Statistical Summary...")
        
        summary = {
            'record_count': len(df),
            'date_range': {},
            'priority_distribution': {},
            'category_distribution': {},
            'geographic_distribution': {},
            'processing_metrics': {}
        }
        
        column_mappings = self.config.get('column_mappings', {})
        
        # Date range analysis
        opened_column = column_mappings.get('opened_at')
        if opened_column and opened_column in df.columns:
            try:
                dates = pd.to_datetime(df[opened_column], errors='coerce').dropna()
                if len(dates) > 0:
                    summary['date_range'] = {
                        'earliest': dates.min().strftime('%Y-%m-%d'),
                        'latest': dates.max().strftime('%Y-%m-%d'),
                        'span_days': (dates.max() - dates.min()).days,
                        'valid_dates': len(dates)
                    }
                    print(f"  📅 Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
            except Exception as e:
                print(f"  ⚠️  Date range analysis failed: {e}")
        
        # Priority distribution
        priority_column = column_mappings.get('priority')
        if priority_column and priority_column in df.columns:
            priority_counts = df[priority_column].value_counts().head(10)
            summary['priority_distribution'] = dict(priority_counts)
            print(f"  🎯 Top priorities: {dict(priority_counts.head(3))}")
        
        # Category distribution
        category_column = column_mappings.get('category')
        if category_column and category_column in df.columns:
            category_counts = df[category_column].value_counts().head(10)
            summary['category_distribution'] = dict(category_counts)
            print(f"  📂 Top categories: {dict(category_counts.head(3))}")
        
        # Geographic distribution
        country_column = column_mappings.get('country')
        if country_column and country_column in df.columns:
            country_counts = df[country_column].value_counts().head(10)
            summary['geographic_distribution'] = dict(country_counts)
            print(f"  🌍 Top countries: {dict(country_counts.head(3))}")
        
        self.validation_results['statistical_summary'] = summary
    
    def generate_overall_assessment(self):
        """Generate overall validation assessment"""
        print("📋 Generating Overall Assessment...")
        
        # Count issues by severity
        critical_count = len([issue for issue in self.issues if issue.get('severity') == 'critical'])
        error_count = len([issue for issue in self.issues if issue.get('severity') == 'error'])
        warning_count = len([issue for issue in self.warnings if issue.get('severity') == 'warning'])
        
        # Determine overall status
        if critical_count > 0:
            overall_status = 'critical'
            status_icon = '🚨'
            status_message = 'Critical issues prevent processing'
        elif error_count > 0:
            overall_status = 'error'
            status_icon = '❌'
            status_message = 'Significant issues may affect processing'
        elif warning_count > 0:
            overall_status = 'warning'
            status_icon = '⚠️'
            status_message = 'Minor issues detected, processing should work'
        else:
            overall_status = 'passed'
            status_icon = '✅'
            status_message = 'Data validation passed successfully'
        
        # Calculate readiness percentage
        kpi_readiness = self.validation_results.get('kpi_readiness', {})
        if kpi_readiness:
            ready_kpis = len([kpi for kpi in kpi_readiness.values() if kpi.get('ready', False)])
            total_kpis = len(kpi_readiness)
            readiness_percent = round((ready_kpis / total_kpis) * 100, 1) if total_kpis > 0 else 0
        else:
            readiness_percent = 0
        
        self.validation_results['overall_status'] = overall_status
        self.validation_results['assessment'] = {
            'status': overall_status,
            'icon': status_icon,
            'message': status_message,
            'critical_issues': critical_count,
            'errors': error_count,
            'warnings': warning_count,
            'kpi_readiness_percent': readiness_percent,
            'processing_recommended': overall_status in ['passed', 'warning']
        }
        
        print(f"  {status_icon} Overall Status: {overall_status.upper()}")
        print(f"  📊 Issues: {critical_count} critical, {error_count} errors, {warning_count} warnings")
        print(f"  🎯 KPI Readiness: {readiness_percent}%")
        print(f"  🚀 Processing Recommended: {'Yes' if self.validation_results['assessment']['processing_recommended'] else 'No'}")
    
    def display_validation_report(self):
        """Display comprehensive validation report"""
        print("\n" + "="*80)
        print("                         DATA VALIDATION REPORT")
        print("="*80)
        
        assessment = self.validation_results.get('assessment', {})
        print(f"📊 Overall Status: {assessment.get('icon', '❓')} {assessment.get('status', 'unknown').upper()}")
        print(f"💬 {assessment.get('message', 'No assessment available')}")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # File information
        file_info = self.validation_results.get('file_info', {})
        if file_info:
            print("📄 FILE INFORMATION")
            print("-" * 40)
            print(f"Name: {file_info.get('name', 'Unknown')}")
            print(f"Size: {file_info.get('size_mb', 0)} MB")
            print(f"Modified: {file_info.get('modified', 'Unknown')}")
            print(f"Age: {file_info.get('age_days', 0)} days")
            print()
        
        # Structure check
        structure = self.validation_results.get('structure_check', {})
        if structure:
            print("🏗️  STRUCTURE CHECK")
            print("-" * 40)
            print(f"Readable: {'✅' if structure.get('readable') else '❌'}")
            print(f"Rows: {structure.get('row_count', 0):,}")
            print(f"Columns: {structure.get('column_count', 0)}")
            print(f"Encoding: {structure.get('encoding', 'Unknown')}")
            print()
        
        # Column analysis
        column_analysis = self.validation_results.get('column_analysis', {})
        if column_analysis:
            print("🔍 COLUMN ANALYSIS")
            print("-" * 40)
            print(f"Mapping Coverage: {column_analysis.get('mapping_coverage', 0)}%")
            print(f"Missing Required: {len(column_analysis.get('missing_required', []))}")
            print(f"Unmapped Columns: {len(column_analysis.get('unmapped_columns', []))}")
            print()
        
        # KPI readiness
        kpi_readiness = self.validation_results.get('kpi_readiness', {})
        if kpi_readiness:
            print("🎯 KPI READINESS")
            print("-" * 40)
            for kpi_id, readiness in kpi_readiness.items():
                status_icon = "✅" if readiness.get('ready') else "❌"
                coverage = readiness.get('field_coverage', 0)
                sufficiency = readiness.get('data_sufficiency', 'unknown')
                print(f"{status_icon} {kpi_id}: {coverage}% fields, {sufficiency} data")
            print()
        
        # Issues and recommendations
        all_issues = self.issues + self.warnings
        if all_issues:
            print("🚨 ISSUES AND WARNINGS")
            print("-" * 40)
            for i, issue in enumerate(all_issues, 1):
                severity = issue.get('severity', 'unknown')
                category = issue.get('category', 'Unknown')
                message = issue.get('message', 'No message')
                
                severity_icons = {
                    'critical': '🔴',
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }
                icon = severity_icons.get(severity, '⚪')
                
                print(f"{i}. {icon} {severity.upper()}: {category}")
                print(f"   {message}")
                if 'recommendation' in issue:
                    print(f"   💡 {issue['recommendation']}")
                print()
        
        if self.recommendations:
            print("💡 RECOMMENDATIONS")
            print("-" * 40)
            for i, rec in enumerate(self.recommendations, 1):
                print(f"{i}. {rec.get('message', 'No message')}")
                print(f"   Action: {rec.get('recommendation', 'No recommendation')}")
                print()
        
        print("="*80)
        print("💡 TIP: Address critical and error issues before processing")
        print("📧 Contact IT Service Management Team for validation support")
        print("="*80)
    
    def save_validation_report(self, output_file: Optional[str] = None):
        """Save validation report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"output/validation_report_{timestamp}.json"
        
        # Add issues and recommendations to results
        self.validation_results['issues'] = self.issues
        self.validation_results['warnings'] = self.warnings
        self.validation_results['recommendations'] = self.recommendations
        self.validation_results['generated_at'] = datetime.now().isoformat()
        
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(self.validation_results, f, indent=2, default=str)
            
            print(f"\n💾 Validation report saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"\n⚠️  Could not save validation report: {e}")
            return None

def main():
    """Main function for data validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Validation Utility for KPI Processing')
    parser.add_argument('--data', required=True, help='CSV data file to validate')
    parser.add_argument('--config', default='config/kpi_config.yaml', help='Configuration file')
    parser.add_argument('--quick', action='store_true', help='Quick validation (skip detailed checks)')
    parser.add_argument('--output', help='Output file for validation report')
    parser.add_argument('--no-display', action='store_true', help='Skip displaying the report')
    
    args = parser.parse_args()
    
    try:
        print("🚀 Data Validation Utility for KPI Processing")
        print("=" * 60)
        
        validator = DataValidator(args.config)
        results = validator.validate_data_file(args.data, args.quick)
        
        if not args.no_display:
            validator.display_validation_report()
        
        # Save report
        report_file = validator.save_validation_report(args.output)
        
        # Return appropriate exit code
        overall_status = results.get('overall_status', 'unknown')
        if overall_status == 'critical':
            return 2
        elif overall_status == 'error':
            return 1
        elif overall_status == 'warning':
            return 0
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\n\n👋 Validation cancelled!")
        return 130
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if '--no-display' not in sys.argv:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)
