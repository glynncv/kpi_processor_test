"""
Shared validation utilities for KPI processing system
"""
import pandas as pd
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


def validate_data_compatibility(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration compatibility with actual data"""
    results = {
        'missing_columns': [],
        'extra_columns': [],
        'format_issues': [],
        'warnings': [],
        'errors': []
    }
    
    column_mappings = config.get('column_mappings', {})
    actual_columns = set(df.columns)
    mapped_columns = set(column_mappings.values())
    
    results['missing_columns'] = list(mapped_columns - actual_columns)
    results['extra_columns'] = list(actual_columns - mapped_columns)
    
    if results['missing_columns']:
        results['errors'].append(f"Data file missing columns required by configuration: {results['missing_columns']}")
    
    if results['extra_columns']:
        extra_display = results['extra_columns'][:5]
        if len(results['extra_columns']) > 5:
            extra_display.append('...')
        results['warnings'].append(f"Data file has additional columns not in configuration: {extra_display}")
    
    format_results = validate_data_formats(df, config)
    results['format_issues'] = format_results['issues']
    results['warnings'].extend(format_results['warnings'])
    
    return results


def validate_data_formats(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data format compatibility"""
    results = {
        'issues': [],
        'warnings': []
    }
    
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
                results['warnings'].append(f"Some priority values may not match extraction pattern '{regex_pattern}': {non_matching[:3]}")
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
                    results['warnings'].append(f"Date format in column '{date_col}' may not be parseable: example '{date_val}'")
                    break
    
    # Check numeric fields
    numeric_fields = ['reassignment_count']
    for field in numeric_fields:
        if field in column_mappings and column_mappings[field] in df.columns:
            numeric_col = column_mappings[field]
            if not pd.api.types.is_numeric_dtype(df[numeric_col]):
                non_numeric_samples = df[numeric_col].dropna().head(3)
                results['warnings'].append(f"Column '{numeric_col}' expected to be numeric but contains: {list(non_numeric_samples)}")
    
    return results


def assess_kpi_readiness(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Assess readiness for each KPI based on data availability"""
    kpi_readiness = {}
    kpis_config = config.get('kpis', {})
    column_mappings = config.get('column_mappings', {})
    
    for kpi_id, kpi_config in kpis_config.items():
        if not kpi_config.get('enabled', True):
            continue
            
        required_fields = kpi_config.get('required_fields', [])
        readiness = calculate_field_readiness(df, required_fields, column_mappings, kpi_id, kpi_config)
        kpi_readiness[kpi_id] = readiness
        
    return kpi_readiness


def calculate_field_readiness(df: pd.DataFrame, required_fields: List[str], 
                             column_mappings: Dict[str, str], kpi_id: str, 
                             kpi_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate field availability and data sufficiency for KPI"""
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
    if required_fields:
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
    
    return readiness


def validate_kpi_data_requirements(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate that data supports configured KPIs - returns (errors, warnings)"""
    errors = []
    warnings = []
    
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
                warnings.append(f"KPI '{kpi_id}' missing required data fields and will be disabled: {missing_for_kpi}")
            else:
                errors.append(f"KPI '{kpi_id}' missing required data fields: {missing_for_kpi}")
    
    return errors, warnings


def standardize_exit_code(validation_passed: bool, errors: List[str], warnings: List[str], 
                         critical_issues: Optional[List[str]] = None) -> int:
    """Standardize exit codes across all validation scripts"""
    if critical_issues and len(critical_issues) > 0:
        return 2  # Critical errors
    elif not validation_passed or (errors and len(errors) > 0):
        return 2  # Errors
    elif warnings and len(warnings) > 0:
        return 1  # Warnings only
    else:
        return 0  # Success
