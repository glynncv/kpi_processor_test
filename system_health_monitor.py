#!/usr/bin/env python3
"""
System Health Monitor for KPI Processing System
==============================================

Real-time monitoring and health checking for the KPI processing system.
Provides diagnostics, alerts, and system status information.
"""

import os
import sys
import json
import yaml
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import platform

class SystemHealthMonitor:
    """Monitor system health and provide diagnostics"""
    
    def __init__(self):
        self.health_status = {}
        self.alerts = []
        self.recommendations = []
        self.start_time = datetime.now()
        
    def run_health_check(self):
        """Run comprehensive health check"""
        print("🔍 KPI System Health Monitor")
        print("="*60)
        print(f"⏰ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Platform: {platform.system()} {platform.release()}")
        print()
        
        # Run all health checks
        self.check_environment()
        self.check_file_structure()
        self.check_configuration()
        self.check_data_availability()
        self.check_processing_status()
        self.check_system_resources()
        self.check_recent_activity()
        
        # Generate summary
        self.generate_health_summary()
        self.display_health_report()
        
        return self.health_status
    
    def check_environment(self):
        """Check Python environment and dependencies"""
        print("🐍 Checking Python Environment...")
        
        env_status = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'modules': {},
            'status': 'unknown'
        }
        
        # Check required modules
        required_modules = {
            'pandas': 'Data processing',
            'yaml': 'Configuration parsing',
            'json': 'JSON handling',
            'pathlib': 'Path operations',
            'datetime': 'Date/time operations',
            'argparse': 'Command line parsing'
        }
        
        missing_modules = []
        for module, description in required_modules.items():
            try:
                __import__(module)
                env_status['modules'][module] = {
                    'available': True,
                    'description': description
                }
                print(f"  ✅ {module:<12} - {description}")
            except ImportError:
                env_status['modules'][module] = {
                    'available': False,
                    'description': description
                }
                missing_modules.append(module)
                print(f"  ❌ {module:<12} - {description} (MISSING)")
        
        if missing_modules:
            env_status['status'] = 'critical'
            self.alerts.append({
                'level': 'critical',
                'component': 'Python Environment',
                'message': f"Missing required modules: {', '.join(missing_modules)}"
            })
        else:
            env_status['status'] = 'healthy'
            print("  🎉 All required modules available!")
        
        self.health_status['environment'] = env_status
        print()
    
    def check_file_structure(self):
        """Check directory and file structure"""
        print("📁 Checking File Structure...")
        
        structure_status = {
            'directories': {},
            'critical_files': {},
            'status': 'unknown'
        }
        
        # Check directories
        required_dirs = {
            'config': 'Configuration files',
            'scripts': 'Python scripts',
            'data': 'Input data files',
            'output': 'Processing results',
            'cache': 'Processing cache (optional)',
            'logs': 'System logs (optional)'
        }
        
        missing_dirs = []
        for dir_name, description in required_dirs.items():
            dir_path = Path(dir_name)
            exists = dir_path.exists()
            structure_status['directories'][dir_name] = {
                'exists': exists,
                'description': description,
                'file_count': len(list(dir_path.glob('*'))) if exists else 0
            }
            
            if exists:
                file_count = structure_status['directories'][dir_name]['file_count']
                print(f"  ✅ {dir_name:<8} - {description} ({file_count} files)")
            else:
                if dir_name in ['config', 'scripts', 'data']:
                    missing_dirs.append(dir_name)
                    print(f"  ❌ {dir_name:<8} - {description} (MISSING)")
                else:
                    print(f"  ⚠️  {dir_name:<8} - {description} (missing, optional)")
        
        # Check critical files
        critical_files = {
            'config/kpi_config.yaml': 'Main KPI configuration',
            'scripts/complete_configurable_processor_fixed.py': 'Main processor script',
            'scripts/config_validator_fixed.py': 'Configuration validator',
            'test_system.py': 'System test script',
            'show_results.py': 'Results display script',
            'final_summary.py': 'Summary generator script'
        }
        
        missing_files = []
        for file_path, description in critical_files.items():
            path = Path(file_path)
            exists = path.exists()
            structure_status['critical_files'][file_path] = {
                'exists': exists,
                'description': description,
                'size_kb': round(path.stat().st_size / 1024, 1) if exists else 0,
                'modified': path.stat().st_mtime if exists else None
            }
            
            if exists:
                size_kb = structure_status['critical_files'][file_path]['size_kb']
                print(f"  ✅ {file_path:<45} ({size_kb} KB)")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path:<45} (MISSING)")
        
        # Determine status
        if missing_dirs or missing_files:
            structure_status['status'] = 'critical'
            self.alerts.append({
                'level': 'critical',
                'component': 'File Structure',
                'message': f"Missing critical components: {len(missing_dirs)} dirs, {len(missing_files)} files"
            })
        else:
            structure_status['status'] = 'healthy'
            print("  🎉 All critical files and directories present!")
        
        self.health_status['file_structure'] = structure_status
        print()
    
    def check_configuration(self):
        """Check configuration validity"""
        print("⚙️  Checking Configuration...")
        
        config_status = {
            'files': {},
            'validation': {},
            'kpis': {},
            'status': 'unknown'
        }
        
        # Check main configuration file
        config_path = Path('config/kpi_config.yaml')
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                config_status['files']['main'] = {
                    'exists': True,
                    'valid_yaml': True,
                    'size_kb': round(config_path.stat().st_size / 1024, 1)
                }
                
                # Check configuration sections
                required_sections = ['metadata', 'column_mappings', 'kpis', 'thresholds']
                missing_sections = []
                
                for section in required_sections:
                    if section in config:
                        print(f"  ✅ {section:<15} section present")
                    else:
                        missing_sections.append(section)
                        print(f"  ❌ {section:<15} section missing")
                
                # Check KPI configuration
                kpis = config.get('kpis', {})
                enabled_kpis = []
                disabled_kpis = []
                
                for kpi_id, kpi_config in kpis.items():
                    if kpi_config.get('enabled', True):
                        enabled_kpis.append(kpi_id)
                    else:
                        disabled_kpis.append(kpi_id)
                
                config_status['kpis'] = {
                    'total': len(kpis),
                    'enabled': enabled_kpis,
                    'disabled': disabled_kpis
                }
                
                print(f"  📊 KPIs: {len(enabled_kpis)} enabled, {len(disabled_kpis)} disabled")
                
                if missing_sections:
                    config_status['status'] = 'error'
                    self.alerts.append({
                        'level': 'error',
                        'component': 'Configuration',
                        'message': f"Missing configuration sections: {', '.join(missing_sections)}"
                    })
                else:
                    config_status['status'] = 'healthy'
                    print("  🎉 Configuration file is valid!")
                
            except yaml.YAMLError as e:
                config_status['files']['main'] = {
                    'exists': True,
                    'valid_yaml': False,
                    'error': str(e)
                }
                config_status['status'] = 'critical'
                print(f"  ❌ YAML parsing error: {e}")
                self.alerts.append({
                    'level': 'critical',
                    'component': 'Configuration',
                    'message': f"YAML parsing error: {e}"
                })
            except Exception as e:
                config_status['status'] = 'critical'
                print(f"  ❌ Configuration error: {e}")
                self.alerts.append({
                    'level': 'critical',
                    'component': 'Configuration',
                    'message': f"Configuration error: {e}"
                })
        else:
            config_status['files']['main'] = {'exists': False}
            config_status['status'] = 'critical'
            print("  ❌ Main configuration file not found!")
            self.alerts.append({
                'level': 'critical',
                'component': 'Configuration',
                'message': "Main configuration file missing"
            })
        
        self.health_status['configuration'] = config_status
        print()
    
    def check_data_availability(self):
        """Check data file availability"""
        print("📊 Checking Data Availability...")
        
        data_status = {
            'data_directory': False,
            'csv_files': [],
            'default_file': False,
            'total_size_mb': 0,
            'status': 'unknown'
        }
        
        data_dir = Path('data')
        if data_dir.exists():
            data_status['data_directory'] = True
            
            csv_files = list(data_dir.glob('*.csv'))
            data_status['csv_files'] = []
            total_size = 0
            
            for csv_file in csv_files:
                file_size = csv_file.stat().st_size
                total_size += file_size
                data_status['csv_files'].append({
                    'name': csv_file.name,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'modified': csv_file.stat().st_mtime
                })
                print(f"  📄 {csv_file.name:<30} ({round(file_size / (1024 * 1024), 2)} MB)")
            
            data_status['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # Check for default file
            default_file = data_dir / 'consolidated_data.csv'
            data_status['default_file'] = default_file.exists()
            
            if data_status['default_file']:
                print("  ✅ Default data file (consolidated_data.csv) found")
            else:
                print("  ⚠️  Default data file (consolidated_data.csv) not found")
            
            if csv_files:
                data_status['status'] = 'healthy'
                print(f"  🎉 {len(csv_files)} CSV files available ({data_status['total_size_mb']} MB total)")
            else:
                data_status['status'] = 'warning'
                print("  ⚠️  No CSV files found in data directory")
                self.alerts.append({
                    'level': 'warning',
                    'component': 'Data',
                    'message': "No CSV data files available"
                })
        else:
            data_status['status'] = 'critical'
            print("  ❌ Data directory not found!")
            self.alerts.append({
                'level': 'critical',
                'component': 'Data',
                'message': "Data directory missing"
            })
        
        self.health_status['data'] = data_status
        print()
    
    def check_processing_status(self):
        """Check recent processing activity"""
        print("🔄 Checking Processing Status...")
        
        processing_status = {
            'output_directory': False,
            'result_files': [],
            'cache_status': {},
            'last_processing': None,
            'status': 'unknown'
        }
        
        # Check output directory
        output_dir = Path('output')
        if output_dir.exists():
            processing_status['output_directory'] = True
            
            json_files = list(output_dir.glob('*.json'))
            if json_files:
                processing_status['result_files'] = []
                
                for json_file in sorted(json_files, key=lambda f: f.stat().st_mtime, reverse=True):
                    file_info = {
                        'name': json_file.name,
                        'size_kb': round(json_file.stat().st_size / 1024, 1),
                        'modified': json_file.stat().st_mtime,
                        'age_hours': round((time.time() - json_file.stat().st_mtime) / 3600, 1)
                    }
                    processing_status['result_files'].append(file_info)
                
                # Get most recent file
                latest_file = processing_status['result_files'][0]
                processing_status['last_processing'] = latest_file
                
                print(f"  📄 Latest result: {latest_file['name']} ({latest_file['age_hours']} hours ago)")
                print(f"  📁 Total result files: {len(json_files)}")
                
                # Determine processing freshness
                if latest_file['age_hours'] < 2:
                    print("  ✅ Very recent processing activity")
                elif latest_file['age_hours'] < 24:
                    print("  ✅ Recent processing activity")
                elif latest_file['age_hours'] < 168:  # 1 week
                    print("  ⚠️  Processing activity is getting stale")
                else:
                    print("  ❌ No recent processing activity")
                    self.alerts.append({
                        'level': 'warning',
                        'component': 'Processing',
                        'message': f"Last processing was {latest_file['age_hours']:.1f} hours ago"
                    })
                
            else:
                print("  ❌ No result files found")
                processing_status['status'] = 'warning'
                self.alerts.append({
                    'level': 'warning',
                    'component': 'Processing',
                    'message': "No processing results available"
                })
        else:
            print("  ❌ Output directory not found")
            processing_status['status'] = 'critical'
        
        # Check cache status
        cache_dir = Path('cache')
        if cache_dir.exists():
            cache_files = {
                'baseline_counts.json': 'Baseline counts',
                'kpi_cache.json': 'KPI cache',
                'last_processed.json': 'Last processing info',
                'record_signatures.pkl': 'Record signatures'
            }
            
            processing_status['cache_status'] = {}
            for cache_file, description in cache_files.items():
                file_path = cache_dir / cache_file
                exists = file_path.exists()
                processing_status['cache_status'][cache_file] = {
                    'exists': exists,
                    'description': description
                }
                
                if exists:
                    age_hours = round((time.time() - file_path.stat().st_mtime) / 3600, 1)
                    print(f"  ✅ {cache_file:<25} - {description} ({age_hours:.1f}h old)")
                else:
                    print(f"  ❌ {cache_file:<25} - {description} (missing)")
        else:
            print("  ⚠️  Cache directory not found (will be created on first run)")
        
        if processing_status.get('last_processing'):
            if processing_status['last_processing']['age_hours'] < 48:
                processing_status['status'] = 'healthy'
            else:
                processing_status['status'] = 'warning'
        elif processing_status['result_files']:
            processing_status['status'] = 'warning'
        else:
            processing_status['status'] = 'critical'
        
        self.health_status['processing'] = processing_status
        print()
    
    def check_system_resources(self):
        """Check system resources"""
        print("💾 Checking System Resources...")
        
        resource_status = {
            'disk_space': {},
            'memory': {},
            'status': 'unknown'
        }
        
        try:
            # Check disk space for current directory
            current_path = Path.cwd()
            if platform.system() == 'Windows':
                import shutil
                total, used, free = shutil.disk_usage(current_path)
                
                resource_status['disk_space'] = {
                    'total_gb': round(total / (1024**3), 1),
                    'used_gb': round(used / (1024**3), 1),
                    'free_gb': round(free / (1024**3), 1),
                    'free_percent': round((free / total) * 100, 1)
                }
                
                free_gb = resource_status['disk_space']['free_gb']
                free_percent = resource_status['disk_space']['free_percent']
                
                print(f"  💿 Disk Space: {free_gb} GB free ({free_percent}%)")
                
                if free_gb < 1:
                    print("  ❌ Very low disk space!")
                    self.alerts.append({
                        'level': 'critical',
                        'component': 'System Resources',
                        'message': f"Very low disk space: {free_gb} GB free"
                    })
                elif free_gb < 5:
                    print("  ⚠️  Low disk space")
                    self.alerts.append({
                        'level': 'warning',
                        'component': 'System Resources',
                        'message': f"Low disk space: {free_gb} GB free"
                    })
                else:
                    print("  ✅ Sufficient disk space")
            
            resource_status['status'] = 'healthy'
            
        except Exception as e:
            print(f"  ⚠️  Could not check system resources: {e}")
            resource_status['status'] = 'unknown'
        
        self.health_status['resources'] = resource_status
        print()
    
    def check_recent_activity(self):
        """Check for recent system activity"""
        print("⏰ Checking Recent Activity...")
        
        activity_status = {
            'recent_files': [],
            'activity_level': 'none',
            'status': 'unknown'
        }
        
        # Look for files modified in the last 24 hours
        current_time = time.time()
        recent_threshold = current_time - (24 * 3600)  # 24 hours ago
        
        directories_to_check = ['output', 'cache', 'logs']
        recent_files = []
        
        for dir_name in directories_to_check:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file() and file_path.stat().st_mtime > recent_threshold:
                        age_hours = round((current_time - file_path.stat().st_mtime) / 3600, 1)
                        recent_files.append({
                            'path': str(file_path),
                            'age_hours': age_hours,
                            'type': file_path.suffix
                        })
        
        activity_status['recent_files'] = sorted(recent_files, key=lambda x: x['age_hours'])
        
        if recent_files:
            print(f"  🎯 {len(recent_files)} files modified in last 24 hours:")
            for file_info in recent_files[:5]:  # Show top 5
                print(f"     📄 {file_info['path']:<40} ({file_info['age_hours']:.1f}h ago)")
            
            if len(recent_files) > 5:
                print(f"     ... and {len(recent_files) - 5} more files")
            
            if len(recent_files) > 10:
                activity_status['activity_level'] = 'high'
                print("  🔥 High activity level")
            elif len(recent_files) > 3:
                activity_status['activity_level'] = 'medium'
                print("  ⚡ Medium activity level")
            else:
                activity_status['activity_level'] = 'low'
                print("  💤 Low activity level")
            
            activity_status['status'] = 'active'
        else:
            print("  😴 No recent file activity detected")
            activity_status['activity_level'] = 'none'
            activity_status['status'] = 'inactive'
        
        self.health_status['activity'] = activity_status
        print()
    
    def generate_health_summary(self):
        """Generate overall health summary"""
        print("📋 Generating Health Summary...")
        
        # Count status levels
        component_statuses = []
        for component, data in self.health_status.items():
            status = data.get('status', 'unknown')
            component_statuses.append(status)
        
        critical_count = component_statuses.count('critical')
        error_count = component_statuses.count('error')
        warning_count = component_statuses.count('warning')
        healthy_count = component_statuses.count('healthy')
        
        # Determine overall status
        if critical_count > 0:
            overall_status = 'critical'
            overall_icon = '🚨'
        elif error_count > 0:
            overall_status = 'error'
            overall_icon = '❌'
        elif warning_count > 0:
            overall_status = 'warning'
            overall_icon = '⚠️'
        elif healthy_count > 0:
            overall_status = 'healthy'
            overall_icon = '✅'
        else:
            overall_status = 'unknown'
            overall_icon = '❓'
        
        self.health_status['overall'] = {
            'status': overall_status,
            'icon': overall_icon,
            'component_count': len(component_statuses),
            'healthy_components': healthy_count,
            'warning_components': warning_count,
            'error_components': error_count,
            'critical_components': critical_count
        }
        
        print(f"  {overall_icon} Overall Status: {overall_status.upper()}")
        print(f"  📊 Components: {healthy_count} healthy, {warning_count} warning, {error_count} error, {critical_count} critical")
        print()
    
    def display_health_report(self):
        """Display comprehensive health report"""
        print("="*80)
        print("                         SYSTEM HEALTH REPORT")
        print("="*80)
        
        overall = self.health_status.get('overall', {})
        print(f"🏥 Overall Status: {overall.get('icon', '❓')} {overall.get('status', 'unknown').upper()}")
        print(f"⏰ Check Duration: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Component status summary
        print("📊 COMPONENT STATUS SUMMARY")
        print("-" * 40)
        
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨',
            'unknown': '❓'
        }
        
        for component, data in self.health_status.items():
            if component == 'overall':
                continue
            
            status = data.get('status', 'unknown')
            icon = status_icons.get(status, '❓')
            print(f"  {icon} {component.replace('_', ' ').title():<20} - {status.upper()}")
        
        # Alerts and issues
        if self.alerts:
            print(f"\n🚨 ALERTS AND ISSUES ({len(self.alerts)})")
            print("-" * 40)
            
            for i, alert in enumerate(self.alerts, 1):
                level = alert['level']
                component = alert['component']
                message = alert['message']
                
                level_icons = {
                    'critical': '🔴',
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }
                icon = level_icons.get(level, '⚪')
                
                print(f"  {i}. {icon} {level.upper()}: {component}")
                print(f"     {message}")
        else:
            print(f"\n✅ NO ALERTS - System is operating normally!")
        
        # Quick stats
        print(f"\n📈 QUICK STATISTICS")
        print("-" * 40)
        
        # Data stats
        data_info = self.health_status.get('data', {})
        csv_count = len(data_info.get('csv_files', []))
        total_data_mb = data_info.get('total_size_mb', 0)
        print(f"  📊 Data Files: {csv_count} CSV files ({total_data_mb} MB)")
        
        # Processing stats
        processing_info = self.health_status.get('processing', {})
        result_count = len(processing_info.get('result_files', []))
        last_processing = processing_info.get('last_processing')
        if last_processing:
            last_age = last_processing.get('age_hours', 0)
            print(f"  🔄 Results: {result_count} files, latest {last_age:.1f}h ago")
        else:
            print(f"  🔄 Results: {result_count} files, no recent processing")
        
        # System stats
        resource_info = self.health_status.get('resources', {})
        disk_info = resource_info.get('disk_space', {})
        if disk_info:
            free_gb = disk_info.get('free_gb', 0)
            print(f"  💾 Disk Space: {free_gb} GB available")
        
        # Activity stats
        activity_info = self.health_status.get('activity', {})
        recent_count = len(activity_info.get('recent_files', []))
        activity_level = activity_info.get('activity_level', 'none')
        print(f"  ⚡ Activity: {recent_count} recent files ({activity_level} level)")
        
        print("\n" + "="*80)
        print("💡 TIP: Run 'python final_summary.py' for detailed system analysis")
        print("📧 Contact IT Service Management Team for support")
        print("="*80)

def main():
    """Main function to run health monitoring"""
    monitor = SystemHealthMonitor()
    
    try:
        health_status = monitor.run_health_check()
        
        # Save health report if possible
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = Path(f'output/health_report_{timestamp}.json')
            
            # Create output directory if needed
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(health_status, f, indent=2, default=str)
            
            print(f"\n💾 Health report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save health report: {e}")
        
        # Return appropriate exit code
        overall_status = health_status.get('overall', {}).get('status', 'unknown')
        if overall_status in ['critical', 'error']:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\n\n👋 Health check cancelled!")
        return 130
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)
