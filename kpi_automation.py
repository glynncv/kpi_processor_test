#!/usr/bin/env python3
"""
KPI Processing Automation Script
===============================

Automated pipeline for KPI processing with:
- Data validation
- Configuration checking
- Processing execution
- Result verification
- Error handling and recovery
- Reporting and notifications
"""

import sys
import os
import json
import yaml
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
import logging

class KPIProcessingPipeline:
    """Automated KPI processing pipeline"""
    
    def __init__(self, config_file: str = "config/kpi_config.yaml", 
                 log_level: str = "INFO", dry_run: bool = False):
        self.config_file = config_file
        self.dry_run = dry_run
        self.start_time = datetime.now()
        
        # Setup logging
        self.setup_logging(log_level)
        
        # Pipeline state
        self.pipeline_state = {
            'status': 'initializing',
            'steps_completed': [],
            'current_step': None,
            'errors': [],
            'warnings': [],
            'results': {},
            'start_time': self.start_time.isoformat(),
            'end_time': None,
            'duration': None
        }
        
        # Configuration
        self.config = {}
        self.processing_options = {}
        
        self.logger.info("KPI Processing Pipeline initialized")
    
    def setup_logging(self, log_level: str):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"pipeline_{timestamp}.log"
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('KPIPipeline')
        self.logger.info(f"Logging initialized - Level: {log_level}")
        self.logger.info(f"Log file: {log_file}")
    
    def run_pipeline(self, data_file: str, mode: str = "baseline", 
                    kpi_id: Optional[str] = None, output_file: Optional[str] = None,
                    validate_first: bool = True, skip_validation: bool = False) -> Dict[str, Any]:
        """Run the complete processing pipeline"""
        
        self.logger.info("="*80)
        self.logger.info("KPI PROCESSING PIPELINE STARTED")
        self.logger.info("="*80)
        self.logger.info(f"Mode: {mode}")
        self.logger.info(f"Data file: {data_file}")
        self.logger.info(f"Config file: {self.config_file}")
        if kpi_id:
            self.logger.info(f"Target KPI: {kpi_id}")
        if output_file:
            self.logger.info(f"Output file: {output_file}")
        self.logger.info(f"Validate first: {validate_first}")
        self.logger.info(f"Dry run: {self.dry_run}")
        
        try:
            # Step 1: Environment check
            self.execute_step("environment_check", self.check_environment)
            
            # Step 2: Configuration validation
            self.execute_step("config_validation", self.validate_configuration)
            
            # Step 3: Data validation (if requested)
            if validate_first and not skip_validation:
                self.execute_step("data_validation", self.validate_data, data_file)
            
            # Step 4: Pre-processing checks
            self.execute_step("pre_processing_checks", self.pre_processing_checks, 
                            data_file, mode, kpi_id)
            
            # Step 5: Execute processing
            if not self.dry_run:
                self.execute_step("processing_execution", self.execute_processing, 
                                data_file, mode, kpi_id, output_file)
            else:
                self.logger.info("DRY RUN: Skipping actual processing execution")
                self.pipeline_state['steps_completed'].append('processing_execution')
            
            # Step 6: Result verification
            if not self.dry_run and output_file:
                self.execute_step("result_verification", self.verify_results, output_file)
            
            # Step 7: Generate pipeline report
            self.execute_step("report_generation", self.generate_pipeline_report)
            
            # Pipeline completed successfully
            self.pipeline_state['status'] = 'completed'
            self.logger.info("Pipeline completed successfully!")
            
        except Exception as e:
            self.pipeline_state['status'] = 'failed'
            self.pipeline_state['errors'].append({
                'step': self.pipeline_state.get('current_step', 'unknown'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            self.logger.error(f"Pipeline failed: {e}")
            raise
        
        finally:
            # Finalize pipeline
            self.finalize_pipeline()
        
        return self.pipeline_state
    
    def execute_step(self, step_name: str, step_function, *args, **kwargs):
        """Execute a pipeline step with error handling"""
        self.pipeline_state['current_step'] = step_name
        self.logger.info(f"Executing step: {step_name}")
        
        step_start = datetime.now()
        
        try:
            result = step_function(*args, **kwargs)
            
            step_duration = (datetime.now() - step_start).total_seconds()
            self.pipeline_state['steps_completed'].append({
                'name': step_name,
                'status': 'completed',
                'duration': step_duration,
                'result': result
            })
            
            self.logger.info(f"Step '{step_name}' completed in {step_duration:.2f}s")
            return result
            
        except Exception as e:
            step_duration = (datetime.now() - step_start).total_seconds()
            error_info = {
                'name': step_name,
                'status': 'failed',
                'duration': step_duration,
                'error': str(e)
            }
            
            self.pipeline_state['steps_completed'].append(error_info)
            self.pipeline_state['errors'].append(error_info)
            
            self.logger.error(f"Step '{step_name}' failed after {step_duration:.2f}s: {e}")
            raise
    
    def check_environment(self) -> Dict[str, Any]:
        """Check environment prerequisites"""
        self.logger.info("Checking environment prerequisites...")
        
        env_check = {
            'python_version': sys.version,
            'working_directory': str(Path.cwd()),
            'required_modules': {},
            'required_files': {},
            'required_directories': {},
            'status': 'unknown'
        }
        
        # Check required Python modules
        required_modules = ['pandas', 'yaml', 'json', 'pathlib', 'datetime']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                env_check['required_modules'][module] = True
                self.logger.debug(f"Module {module}: ✅")
            except ImportError:
                env_check['required_modules'][module] = False
                missing_modules.append(module)
                self.logger.error(f"Module {module}: ❌")
        
        # Check required files
        required_files = {
            'scripts/complete_configurable_processor_fixed.py': 'Main processor script',
            'scripts/config_validator_fixed.py': 'Configuration validator',
            self.config_file: 'Main configuration file'
        }
        
        missing_files = []
        for file_path, description in required_files.items():
            exists = Path(file_path).exists()
            env_check['required_files'][file_path] = exists
            
            if exists:
                self.logger.debug(f"File {file_path}: ✅")
            else:
                missing_files.append(file_path)
                self.logger.error(f"File {file_path}: ❌ ({description})")
        
        # Check required directories
        required_dirs = ['scripts', 'config', 'data', 'output']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            exists = dir_path.exists()
            env_check['required_directories'][dir_name] = exists
            
            if exists:
                self.logger.debug(f"Directory {dir_name}: ✅")
            else:
                missing_dirs.append(dir_name)
                if dir_name == 'output':
                    # Create output directory if missing
                    dir_path.mkdir(exist_ok=True)
                    self.logger.info(f"Created missing directory: {dir_name}")
                    env_check['required_directories'][dir_name] = True
                else:
                    self.logger.error(f"Directory {dir_name}: ❌")
        
        # Determine overall status
        if missing_modules or missing_files or missing_dirs:
            env_check['status'] = 'failed'
            error_msg = []
            if missing_modules:
                error_msg.append(f"Missing modules: {', '.join(missing_modules)}")
            if missing_files:
                error_msg.append(f"Missing files: {', '.join(missing_files)}")
            if missing_dirs:
                error_msg.append(f"Missing directories: {', '.join(missing_dirs)}")
            
            raise Exception(f"Environment check failed: {'; '.join(error_msg)}")
        else:
            env_check['status'] = 'passed'
            self.logger.info("Environment check passed ✅")
        
        return env_check
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration file"""
        self.logger.info("Validating configuration...")
        
        config_validation = {
            'file_exists': False,
            'file_readable': False,
            'yaml_valid': False,
            'structure_valid': False,
            'kpis_enabled': [],
            'issues': [],
            'status': 'unknown'
        }
        
        config_path = Path(self.config_file)
        
        # Check file existence
        if not config_path.exists():
            raise Exception(f"Configuration file not found: {self.config_file}")
        
        config_validation['file_exists'] = True
        self.logger.debug("Configuration file exists ✅")
        
        # Try to read and parse YAML
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            config_validation['file_readable'] = True
            config_validation['yaml_valid'] = True
            self.logger.debug("Configuration file readable and valid YAML ✅")
            
        except Exception as e:
            raise Exception(f"Cannot read configuration file: {e}")
        
        # Validate structure
        required_sections = ['metadata', 'column_mappings', 'kpis', 'thresholds']
        missing_sections = []
        
        for section in required_sections:
            if section not in self.config:
                missing_sections.append(section)
                config_validation['issues'].append(f"Missing section: {section}")
        
        if missing_sections:
            raise Exception(f"Configuration missing required sections: {', '.join(missing_sections)}")
        
        config_validation['structure_valid'] = True
        self.logger.debug("Configuration structure valid ✅")
        
        # Check enabled KPIs
        kpis = self.config.get('kpis', {})
        enabled_kpis = []
        
        for kpi_id, kpi_config in kpis.items():
            if kpi_config.get('enabled', True):
                enabled_kpis.append(kpi_id)
        
        config_validation['kpis_enabled'] = enabled_kpis
        self.logger.info(f"Enabled KPIs: {', '.join(enabled_kpis)}")
        
        if not enabled_kpis:
            config_validation['issues'].append("No KPIs are enabled")
            self.logger.warning("No KPIs are enabled")
        
        config_validation['status'] = 'valid'
        self.logger.info("Configuration validation passed ✅")
        
        return config_validation
    
    def validate_data(self, data_file: str) -> Dict[str, Any]:
        """Validate input data file"""
        self.logger.info(f"Validating data file: {data_file}")
        
        # Use the data validator script
        data_validator_script = "data_validator.py"
        
        if not Path(data_validator_script).exists():
            self.logger.warning("Data validator script not found, skipping detailed validation")
            
            # Basic validation
            data_path = Path(data_file)
            if not data_path.exists():
                raise Exception(f"Data file not found: {data_file}")
            
            if data_path.suffix.lower() != '.csv':
                raise Exception(f"Data file must be CSV format: {data_file}")
            
            return {
                'status': 'basic_check_passed',
                'file_exists': True,
                'file_format': 'csv'
            }
        
        # Run comprehensive validation
        try:
            cmd = [
                sys.executable, data_validator_script,
                '--data', data_file,
                '--config', self.config_file,
                '--quick',  # Quick validation for pipeline
                '--no-display'  # Don't display interactive report
            ]
            
            self.logger.debug(f"Running data validation: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            validation_result = {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                validation_result['status'] = 'passed'
                self.logger.info("Data validation passed ✅")
            elif result.returncode == 1:
                validation_result['status'] = 'warnings'
                self.logger.warning("Data validation passed with warnings ⚠️")
            else:
                validation_result['status'] = 'failed'
                error_msg = f"Data validation failed (exit code {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise Exception(error_msg)
            
            return validation_result
            
        except subprocess.TimeoutExpired:
            raise Exception("Data validation timed out")
        except Exception as e:
            raise Exception(f"Data validation error: {e}")
    
    def pre_processing_checks(self, data_file: str, mode: str, kpi_id: Optional[str]) -> Dict[str, Any]:
        """Perform pre-processing checks"""
        self.logger.info("Performing pre-processing checks...")
        
        checks = {
            'data_file_exists': False,
            'cache_status': {},
            'mode_requirements': {},
            'kpi_requirements': {},
            'processing_readiness': False,
            'status': 'unknown'
        }
        
        # Check data file
        data_path = Path(data_file)
        if not data_path.exists():
            raise Exception(f"Data file not found: {data_file}")
        
        checks['data_file_exists'] = True
        checks['data_file_size'] = round(data_path.stat().st_size / (1024 * 1024), 2)
        self.logger.debug(f"Data file: {data_file} ({checks['data_file_size']} MB)")
        
        # Check cache status for incremental mode
        if mode == 'incremental':
            cache_dir = Path('cache')
            required_cache_files = ['baseline_counts.json', 'kpi_cache.json']
            
            checks['cache_status'] = {}
            missing_cache = []
            
            for cache_file in required_cache_files:
                cache_path = cache_dir / cache_file
                exists = cache_path.exists()
                checks['cache_status'][cache_file] = exists
                
                if not exists:
                    missing_cache.append(cache_file)
            
            if missing_cache:
                error_msg = f"Incremental mode requires cache files: {', '.join(missing_cache)}"
                self.logger.error(error_msg)
                raise Exception(f"{error_msg}. Run baseline processing first.")
            
            checks['mode_requirements']['incremental'] = 'satisfied'
            self.logger.debug("Incremental mode requirements satisfied ✅")
        
        # Check KPI-specific requirements for targeted mode
        if mode == 'targeted':
            if not kpi_id:
                raise Exception("Targeted mode requires KPI ID")
            
            kpis = self.config.get('kpis', {})
            if kpi_id not in kpis:
                raise Exception(f"Unknown KPI ID: {kpi_id}")
            
            kpi_config = kpis[kpi_id]
            if not kpi_config.get('enabled', True):
                raise Exception(f"KPI {kpi_id} is disabled in configuration")
            
            checks['kpi_requirements'] = {
                'kpi_id': kpi_id,
                'kpi_name': kpi_config.get('name', 'Unknown'),
                'enabled': True,
                'required_fields': kpi_config.get('required_fields', [])
            }
            
            self.logger.debug(f"Targeted KPI {kpi_id} requirements satisfied ✅")
        
        # Overall readiness
        checks['processing_readiness'] = True
        checks['status'] = 'ready'
        self.logger.info("Pre-processing checks passed ✅")
        
        return checks
    
    def execute_processing(self, data_file: str, mode: str, 
                         kpi_id: Optional[str], output_file: Optional[str]) -> Dict[str, Any]:
        """Execute the KPI processing"""
        self.logger.info(f"Executing {mode} processing...")
        
        # Build command
        processor_script = "scripts/complete_configurable_processor_fixed.py"
        
        cmd = [
            sys.executable, processor_script,
            '--config', self.config_file,
            '--mode', mode,
            '--input', data_file
        ]
        
        if kpi_id:
            cmd.extend(['--kpi', kpi_id])
        
        if output_file:
            cmd.extend(['--output', output_file])
        else:
            # Generate default output file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if mode == 'targeted' and kpi_id:
                output_file = f"output/{mode}_{kpi_id}_{timestamp}.json"
            else:
                output_file = f"output/{mode}_{timestamp}.json"
            cmd.extend(['--output', output_file])
        
        self.logger.info(f"Processing command: {' '.join(cmd)}")
        
        # Execute processing
        processing_start = datetime.now()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            processing_duration = (datetime.now() - processing_start).total_seconds()
            
            processing_result = {
                'command': ' '.join(cmd),
                'exit_code': result.returncode,
                'duration': processing_duration,
                'output_file': output_file,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                processing_result['status'] = 'success'
                self.logger.info(f"Processing completed successfully in {processing_duration:.2f}s ✅")
                self.logger.info(f"Output saved to: {output_file}")
            else:
                processing_result['status'] = 'failed'
                error_msg = f"Processing failed (exit code {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise Exception(error_msg)
            
            return processing_result
            
        except subprocess.TimeoutExpired:
            processing_duration = (datetime.now() - processing_start).total_seconds()
            raise Exception(f"Processing timed out after {processing_duration:.2f}s")
        except Exception as e:
            raise Exception(f"Processing execution error: {e}")
    
    def verify_results(self, output_file: str) -> Dict[str, Any]:
        """Verify processing results"""
        self.logger.info(f"Verifying results: {output_file}")
        
        verification = {
            'output_file_exists': False,
            'output_file_readable': False,
            'json_valid': False,
            'result_structure': {},
            'result_summary': {},
            'issues': [],
            'status': 'unknown'
        }
        
        output_path = Path(output_file)
        
        # Check file existence
        if not output_path.exists():
            raise Exception(f"Output file not found: {output_file}")
        
        verification['output_file_exists'] = True
        verification['output_file_size'] = round(output_path.stat().st_size / 1024, 2)  # KB
        
        # Try to read and parse JSON
        try:
            with open(output_path, 'r') as f:
                result_data = json.load(f)
            
            verification['output_file_readable'] = True
            verification['json_valid'] = True
            
        except Exception as e:
            raise Exception(f"Cannot read result file: {e}")
        
        # Analyze result structure
        verification['result_structure'] = {
            'has_mode': 'mode' in result_data,
            'has_timestamp': any(key.endswith('timestamp') for key in result_data.keys()),
            'has_records_processed': 'records_processed' in result_data,
            'has_kpis': any('kpi' in key.lower() for key in result_data.keys()),
            'has_overall_score': 'overall_score' in result_data
        }
        
        # Extract summary information
        verification['result_summary'] = {
            'mode': result_data.get('mode', 'unknown'),
            'records_processed': result_data.get('records_processed', 0),
            'processing_time': result_data.get('processing_time', 'unknown'),
            'config_version': result_data.get('config_version', 'unknown')
        }
        
        # Check for overall score
        if 'overall_score' in result_data:
            overall_score = result_data['overall_score']
            if isinstance(overall_score, dict):
                verification['result_summary']['overall_score'] = overall_score.get('overall_score', 'unknown')
                verification['result_summary']['performance_band'] = overall_score.get('performance_band', 'unknown')
            else:
                verification['result_summary']['overall_score'] = overall_score
        
        # Check for KPI results
        kpi_fields = ['baseline_kpis', 'updated_kpis', 'affected_kpis']
        kpi_count = 0
        for field in kpi_fields:
            if field in result_data:
                if isinstance(result_data[field], dict):
                    kpi_count += len(result_data[field])
                elif isinstance(result_data[field], list):
                    kpi_count += len(result_data[field])
        
        verification['result_summary']['kpi_count'] = kpi_count
        
        # Validation checks
        if verification['result_summary']['records_processed'] == 0:
            verification['issues'].append("No records were processed")
        
        if kpi_count == 0:
            verification['issues'].append("No KPI results found")
        
        if verification['issues']:
            verification['status'] = 'issues_found'
            for issue in verification['issues']:
                self.logger.warning(f"Result verification issue: {issue}")
        else:
            verification['status'] = 'verified'
            self.logger.info("Result verification passed ✅")
        
        # Log summary
        summary = verification['result_summary']
        self.logger.info(f"Results summary:")
        self.logger.info(f"  Mode: {summary['mode']}")
        self.logger.info(f"  Records: {summary['records_processed']:,}")
        self.logger.info(f"  KPIs: {summary['kpi_count']}")
        if 'overall_score' in summary:
            self.logger.info(f"  Score: {summary['overall_score']}")
        
        return verification
    
    def generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate pipeline execution report"""
        self.logger.info("Generating pipeline report...")
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        report = {
            'pipeline_id': f"pipeline_{self.start_time.strftime('%Y%m%d_%H%M%S')}",
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_duration': total_duration,
            'status': self.pipeline_state['status'],
            'steps_summary': {
                'total_steps': len(self.pipeline_state['steps_completed']),
                'successful_steps': len([s for s in self.pipeline_state['steps_completed'] 
                                        if isinstance(s, dict) and s.get('status') == 'completed']),
                'failed_steps': len([s for s in self.pipeline_state['steps_completed'] 
                                   if isinstance(s, dict) and s.get('status') == 'failed'])
            },
            'error_count': len(self.pipeline_state['errors']),
            'warning_count': len(self.pipeline_state['warnings']),
            'configuration': {
                'config_file': self.config_file,
                'dry_run': self.dry_run
            }
        }
        
        # Step timing analysis
        step_timings = []
        for step in self.pipeline_state['steps_completed']:
            if isinstance(step, dict) and 'duration' in step:
                step_timings.append({
                    'name': step['name'],
                    'duration': step['duration'],
                    'status': step['status']
                })
        
        if step_timings:
            report['step_timings'] = step_timings
            report['longest_step'] = max(step_timings, key=lambda x: x['duration'])
            report['total_step_time'] = sum(s['duration'] for s in step_timings)
        
        # Performance metrics
        if total_duration > 0:
            report['performance_metrics'] = {
                'steps_per_minute': (len(self.pipeline_state['steps_completed']) / total_duration) * 60,
                'efficiency_ratio': report.get('total_step_time', 0) / total_duration if total_duration > 0 else 0
            }
        
        self.logger.info(f"Pipeline execution summary:")
        self.logger.info(f"  Duration: {total_duration:.2f}s")
        self.logger.info(f"  Steps: {report['steps_summary']['successful_steps']}/{report['steps_summary']['total_steps']} successful")
        self.logger.info(f"  Errors: {report['error_count']}")
        self.logger.info(f"  Warnings: {report['warning_count']}")
        
        return report
    
    def finalize_pipeline(self):
        """Finalize pipeline execution"""
        end_time = datetime.now()
        self.pipeline_state['end_time'] = end_time.isoformat()
        self.pipeline_state['duration'] = (end_time - self.start_time).total_seconds()
        self.pipeline_state['current_step'] = None
        
        # Save pipeline state
        try:
            timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
            state_file = Path(f"output/pipeline_state_{timestamp}.json")
            
            # Ensure output directory exists
            state_file.parent.mkdir(exist_ok=True)
            
            with open(state_file, 'w') as f:
                json.dump(self.pipeline_state, f, indent=2, default=str)
            
            self.logger.info(f"Pipeline state saved to: {state_file}")
            
        except Exception as e:
            self.logger.warning(f"Could not save pipeline state: {e}")
        
        # Final log
        status = self.pipeline_state['status']
        duration = self.pipeline_state['duration']
        
        self.logger.info("="*80)
        self.logger.info(f"PIPELINE {status.upper()} - Duration: {duration:.2f}s")
        self.logger.info("="*80)

def main():
    """Main function for pipeline execution"""
    parser = argparse.ArgumentParser(description='KPI Processing Automation Pipeline')
    parser.add_argument('--data', required=True, help='CSV data file to process')
    parser.add_argument('--mode', default='baseline', choices=['baseline', 'incremental', 'targeted'],
                       help='Processing mode')
    parser.add_argument('--kpi', help='Target KPI for targeted mode')
    parser.add_argument('--config', default='config/kpi_config.yaml', help='Configuration file')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--no-validate', action='store_true', help='Skip data validation')
    parser.add_argument('--skip-validation', action='store_true', help='Skip configuration validation')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - validate but do not process')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--quiet', action='store_true', help='Suppress non-error output')
    
    args = parser.parse_args()
    
    # Adjust logging for quiet mode
    if args.quiet:
        args.log_level = 'ERROR'
    
    try:
        # Initialize pipeline
        pipeline = KPIProcessingPipeline(
            config_file=args.config,
            log_level=args.log_level,
            dry_run=args.dry_run
        )
        
        # Run pipeline
        result = pipeline.run_pipeline(
            data_file=args.data,
            mode=args.mode,
            kpi_id=args.kpi,
            output_file=args.output,
            validate_first=not args.no_validate,
            skip_validation=args.skip_validation
        )
        
        # Return appropriate exit code
        status = result.get('status', 'unknown')
        error_count = len(result.get('errors', []))
        
        if status == 'completed' and error_count == 0:
            return 0
        elif status == 'completed' and error_count > 0:
            return 1  # Completed with warnings/non-critical errors
        else:
            return 2  # Failed
            
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline cancelled!")
        return 130
    except Exception as e:
        if not args.quiet:
            print(f"\n❌ Pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
