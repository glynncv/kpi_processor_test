#!/usr/bin/env python3
"""
Final Summary Generator for KPI Processing System
===============================================

Generates comprehensive summaries of the KPI processing system including:
- System health and status
- Latest processing results
- Configuration analysis
- Performance trends
- Recommendations for improvement
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob
import yaml

class FinalSummaryGenerator:
    """Generate comprehensive system summary reports"""
    
    def __init__(self, config_dir: str = "config", output_dir: str = "output", 
                 cache_dir: str = "cache", logs_dir: str = "logs"):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.logs_dir = Path(logs_dir)
        
        self.system_health = {}
        self.latest_results = {}
        self.config_analysis = {}
        self.performance_trends = {}
        self.recommendations = []
    
    def generate_summary(self):
        """Generate complete system summary"""
        print("🔍 Analyzing KPI Processing System...")
        print("="*80)
        
        # Analyze system components
        self.analyze_system_health()
        self.analyze_latest_results()
        self.analyze_configuration()
        self.analyze_performance_trends()
        self.generate_recommendations()
        
        # Display summary
        self.display_summary()
        
        # Save summary report
        self.save_summary_report()
    
    def analyze_system_health(self):
        """Analyze overall system health"""
        print("📊 Analyzing System Health...")
        
        health = {
            'directories': {},
            'files': {},
            'data_availability': {},
            'last_activity': {},
            'overall_status': 'Unknown'
        }
        
        # Check directory structure
        dirs_to_check = {
            'config': self.config_dir,
            'output': self.output_dir,
            'cache': self.cache_dir,
            'logs': self.logs_dir,
            'data': Path("data"),
            'scripts': Path("scripts")
        }
        
        for dir_name, dir_path in dirs_to_check.items():
            health['directories'][dir_name] = {
                'exists': dir_path.exists(),
                'file_count': len(list(dir_path.glob('*'))) if dir_path.exists() else 0,
                'size_mb': self.get_directory_size(dir_path) if dir_path.exists() else 0
            }
        
        # Check critical files
        critical_files = {
            'main_config': self.config_dir / "kpi_config.yaml",
            'complete_config': self.config_dir / "complete_kpi_config.yaml",
            'main_processor': Path("scripts/complete_configurable_processor_fixed.py"),
            'config_validator': Path("scripts/config_validator_fixed.py"),
            'test_system': Path("test_system.py"),
            'data_file': Path("data/consolidated_data.csv")
        }
        
        for file_name, file_path in critical_files.items():
            if file_path.exists():
                stat = file_path.stat()
                health['files'][file_name] = {
                    'exists': True,
                    'size_kb': round(stat.st_size / 1024, 1),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                health['files'][file_name] = {'exists': False}
        
        # Check data availability
        data_dir = Path("data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            health['data_availability'] = {
                'csv_files_count': len(csv_files),
                'csv_files': [f.name for f in csv_files],
                'total_data_size_mb': sum(f.stat().st_size for f in csv_files) / (1024*1024)
            }
        
        # Check last activity
        if self.output_dir.exists():
            output_files = list(self.output_dir.glob("*.json"))
            if output_files:
                latest_output = max(output_files, key=lambda f: f.stat().st_mtime)
                health['last_activity'] = {
                    'last_processing': datetime.fromtimestamp(latest_output.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'latest_file': latest_output.name,
                    'hours_ago': round((datetime.now().timestamp() - latest_output.stat().st_mtime) / 3600, 1)
                }
        
        # Determine overall status
        critical_issues = []
        if not health['files']['main_config']['exists']:
            critical_issues.append("Missing main configuration file")
        if not health['files']['main_processor']['exists']:
            critical_issues.append("Missing main processor script")
        if not health['data_availability'].get('csv_files_count', 0):
            critical_issues.append("No data files available")
        
        if not critical_issues:
            if health['last_activity'].get('hours_ago', 999) < 24:
                health['overall_status'] = 'Healthy'
            else:
                health['overall_status'] = 'Needs Attention'
        else:
            health['overall_status'] = 'Critical Issues'
            health['critical_issues'] = critical_issues
        
        self.system_health = health
    
    def analyze_latest_results(self):
        """Analyze the latest processing results"""
        print("📈 Analyzing Latest Results...")
        
        if not self.output_dir.exists():
            self.latest_results = {'status': 'No output directory'}
            return
        
        # Find all result files
        result_files = list(self.output_dir.glob("*.json"))
        if not result_files:
            self.latest_results = {'status': 'No result files found'}
            return
        
        # Get the most recent results by type
        result_types = {
            'baseline': ['baseline_results.json', 'quick_results.json'],
            'incremental': ['incremental_results.json'],
            'targeted': ['targeted_', 'sm001_', 'sm004_'],
            'test': ['test_', 'validation_']
        }
        
        latest_by_type = {}
        
        for result_type, patterns in result_types.items():
            matching_files = []
            for file_path in result_files:
                if any(pattern in file_path.name.lower() for pattern in patterns):
                    matching_files.append(file_path)
            
            if matching_files:
                # Get the most recent file
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                        data['_file_name'] = latest_file.name
                        data['_file_time'] = latest_file.stat().st_mtime
                        latest_by_type[result_type] = data
                except Exception as e:
                    latest_by_type[result_type] = {'error': str(e), '_file_name': latest_file.name}
        
        # Find overall latest result with KPI data
        latest_overall = None
        latest_time = 0
        
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    file_time = file_path.stat().st_mtime
                    if (file_time > latest_time and 
                        ('baseline_kpis' in data or 'overall_score' in data)):
                        latest_overall = data
                        latest_overall['_file_name'] = file_path.name
                        latest_overall['_file_time'] = file_time
                        latest_time = file_time
            except:
                continue
        
        self.latest_results = {
            'by_type': latest_by_type,
            'latest_overall': latest_overall,
            'total_files': len(result_files),
            'file_types_found': list(latest_by_type.keys())
        }
    
    def analyze_configuration(self):
        """Analyze system configuration"""
        print("⚙️  Analyzing Configuration...")
        
        config_analysis = {
            'files_found': [],
            'kpis_enabled': [],
            'kpis_disabled': [],
            'configuration_issues': [],
            'recommendations': []
        }
        
        # Check for configuration files
        config_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        config_analysis['files_found'] = [f.name for f in config_files]
        
        # Analyze main configuration
        main_config_path = self.config_dir / "kpi_config.yaml"
        if main_config_path.exists():
            try:
                with open(main_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Analyze KPI configuration
                kpis = config.get('kpis', {})
                for kpi_id, kpi_config in kpis.items():
                    if kpi_config.get('enabled', True):
                        config_analysis['kpis_enabled'].append({
                            'id': kpi_id,
                            'name': kpi_config.get('name', 'Unknown'),
                            'priority': kpi_config.get('priority', 'Unknown'),
                            'business_impact': kpi_config.get('business_impact', 'Unknown')
                        })
                    else:
                        config_analysis['kpis_disabled'].append({
                            'id': kpi_id,
                            'name': kpi_config.get('name', 'Unknown'),
                            'reason': 'Disabled in configuration'
                        })
                
                # Check for configuration issues
                metadata = config.get('metadata', {})
                if not metadata.get('version'):
                    config_analysis['configuration_issues'].append("Missing version in metadata")
                
                thresholds = config.get('thresholds', {})
                if not thresholds.get('aging', {}).get('backlog_days'):
                    config_analysis['configuration_issues'].append("Missing backlog threshold configuration")
                
                # Configuration recommendations
                enabled_count = len(config_analysis['kpis_enabled'])
                if enabled_count < 3:
                    config_analysis['recommendations'].append(f"Consider enabling more KPIs (currently {enabled_count} enabled)")
                
                if 'SM003' in [kpi['id'] for kpi in config_analysis['kpis_disabled']]:
                    config_analysis['recommendations'].append("SM003 (Service Request Aging) is disabled - enable if request data available")
                
            except Exception as e:
                config_analysis['configuration_issues'].append(f"Error reading main config: {e}")
        else:
            config_analysis['configuration_issues'].append("Main configuration file not found")
        
        self.config_analysis = config_analysis
    
    def analyze_performance_trends(self):
        """Analyze performance trends from historical data"""
        print("📊 Analyzing Performance Trends...")
        
        trends = {
            'processing_history': [],
            'kpi_trends': {},
            'performance_summary': {},
            'data_volume_trends': []
        }
        
        if not self.output_dir.exists():
            self.performance_trends = trends
            return
        
        # Collect historical processing data
        result_files = sorted(self.output_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)
        
        for file_path in result_files[-10:]:  # Last 10 files
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                processing_record = {
                    'file': file_path.name,
                    'timestamp': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'mode': data.get('mode', 'Unknown'),
                    'records': data.get('records_processed', 0),
                    'processing_time': data.get('processing_time', 'Unknown')
                }
                
                # Extract overall score if available
                if 'overall_score' in data:
                    score_data = data['overall_score']
                    if isinstance(score_data, dict):
                        processing_record['overall_score'] = score_data.get('overall_score', 0)
                        processing_record['performance_band'] = score_data.get('performance_band', 'Unknown')
                    else:
                        processing_record['overall_score'] = score_data
                
                trends['processing_history'].append(processing_record)
                
                # Track data volume
                if data.get('records_processed'):
                    trends['data_volume_trends'].append({
                        'timestamp': processing_record['timestamp'],
                        'records': data['records_processed']
                    })
                
            except:
                continue
        
        # Analyze KPI trends
        for record in trends['processing_history']:
            if 'overall_score' in record:
                date_key = record['timestamp'][:10]  # YYYY-MM-DD
                if date_key not in trends['kpi_trends']:
                    trends['kpi_trends'][date_key] = []
                trends['kpi_trends'][date_key].append(record['overall_score'])
        
        # Calculate performance summary
        if trends['processing_history']:
            recent_scores = [r.get('overall_score', 0) for r in trends['processing_history'][-5:] 
                           if 'overall_score' in r]
            if recent_scores:
                trends['performance_summary'] = {
                    'average_recent_score': round(sum(recent_scores) / len(recent_scores), 1),
                    'best_recent_score': max(recent_scores),
                    'worst_recent_score': min(recent_scores),
                    'score_trend': 'improving' if len(recent_scores) >= 2 and recent_scores[-1] > recent_scores[0] else 'stable'
                }
        
        self.performance_trends = trends
    
    def generate_recommendations(self):
        """Generate system improvement recommendations"""
        print("💡 Generating Recommendations...")
        
        recommendations = []
        
        # System health recommendations
        if self.system_health.get('overall_status') == 'Critical Issues':
            for issue in self.system_health.get('critical_issues', []):
                recommendations.append({
                    'category': 'Critical',
                    'priority': 'High',
                    'issue': issue,
                    'recommendation': self.get_fix_recommendation(issue)
                })
        
        # Performance recommendations
        performance_summary = self.performance_trends.get('performance_summary', {})
        avg_score = performance_summary.get('average_recent_score', 0)
        
        if avg_score < 60:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'issue': f'Low average performance score ({avg_score}/100)',
                'recommendation': 'Review KPI targets and thresholds; investigate root causes of poor performance'
            })
        elif avg_score < 80:
            recommendations.append({
                'category': 'Performance',
                'priority': 'Medium',
                'issue': f'Performance score needs improvement ({avg_score}/100)',
                'recommendation': 'Fine-tune KPI targets and focus on improvement initiatives'
            })
        
        # Configuration recommendations
        config_recs = self.config_analysis.get('recommendations', [])
        for rec in config_recs:
            recommendations.append({
                'category': 'Configuration',
                'priority': 'Medium',
                'issue': 'Configuration optimization',
                'recommendation': rec
            })
        
        # Data processing recommendations
        last_activity = self.system_health.get('last_activity', {})
        hours_since_last = last_activity.get('hours_ago', 999)
        
        if hours_since_last > 168:  # 1 week
            recommendations.append({
                'category': 'Operations',
                'priority': 'Medium',
                'issue': f'No recent processing activity ({hours_since_last:.1f} hours ago)',
                'recommendation': 'Schedule regular KPI processing runs; consider automation'
            })
        elif hours_since_last > 48:  # 2 days
            recommendations.append({
                'category': 'Operations',
                'priority': 'Low',
                'issue': f'Infrequent processing activity ({hours_since_last:.1f} hours ago)',
                'recommendation': 'Consider more frequent KPI updates for better monitoring'
            })
        
        # Data volume recommendations
        data_availability = self.system_health.get('data_availability', {})
        csv_count = data_availability.get('csv_files_count', 0)
        
        if csv_count == 0:
            recommendations.append({
                'category': 'Data',
                'priority': 'High',
                'issue': 'No data files available',
                'recommendation': 'Upload CSV data files to the data/ directory'
            })
        elif csv_count == 1:
            recommendations.append({
                'category': 'Data',
                'priority': 'Low',
                'issue': 'Limited data files available',
                'recommendation': 'Consider maintaining multiple data files for different time periods or testing'
            })
        
        # Sort by priority
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        self.recommendations = recommendations
    
    def get_fix_recommendation(self, issue: str) -> str:
        """Get specific fix recommendation for an issue"""
        fixes = {
            "Missing main configuration file": "Create or restore config/kpi_config.yaml from template",
            "Missing main processor script": "Restore scripts/complete_configurable_processor_fixed.py",
            "No data files available": "Upload CSV data files to the data/ directory"
        }
        return fixes.get(issue, "Review system requirements and restore missing components")
    
    def get_directory_size(self, directory: Path) -> float:
        """Get directory size in MB"""
        try:
            total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0
    
    def display_summary(self):
        """Display the complete system summary"""
        print("\n" + "="*80)
        print("                          FINAL SYSTEM SUMMARY")
        print("="*80)
        
        # Header with timestamp
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 Organization: {self.get_organization_name()}")
        print()
        
        # System Health Overview
        print("🏥 SYSTEM HEALTH")
        print("-"*60)
        status = self.system_health.get('overall_status', 'Unknown')
        status_icon = {"Healthy": "✅", "Needs Attention": "⚠️", "Critical Issues": "🚨"}.get(status, "❓")
        print(f"Overall Status: {status_icon} {status}")
        
        if status == 'Critical Issues':
            print("Critical Issues:")
            for issue in self.system_health.get('critical_issues', []):
                print(f"  🔴 {issue}")
        
        # Directory status
        print("\nDirectory Structure:")
        for dir_name, dir_info in self.system_health.get('directories', {}).items():
            status_icon = "✅" if dir_info['exists'] else "❌"
            file_count = dir_info.get('file_count', 0)
            size_mb = dir_info.get('size_mb', 0)
            print(f"  {status_icon} {dir_name:12} - {file_count:3} files ({size_mb:6.1f} MB)")
        
        # Latest Processing Results
        print(f"\n📊 LATEST PROCESSING RESULTS")
        print("-"*60)
        
        latest_overall = self.latest_results.get('latest_overall')
        if latest_overall and isinstance(latest_overall, dict):
            file_time_stamp = latest_overall.get('_file_time', 0)
            if isinstance(file_time_stamp, (int, float)):
                file_time = datetime.fromtimestamp(file_time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Last Processing: {file_time}")
            
            file_name = latest_overall.get('_file_name', 'Unknown')
            print(f"Source File: {file_name}")
            
            records_processed = latest_overall.get('records_processed', 'Unknown')
            if isinstance(records_processed, int):
                print(f"Records Processed: {records_processed:,}")
            else:
                print(f"Records Processed: {records_processed}")
            
            # Overall score
            if 'overall_score' in latest_overall:
                score_data = latest_overall.get('overall_score')
                if isinstance(score_data, dict):
                    score = score_data.get('overall_score', 'Unknown')
                    band = score_data.get('performance_band', 'Unknown')
                    print(f"Overall Score: {score}/100 ({band})")
                else:
                    print(f"Overall Score: {score_data}")
            
            # KPI Summary
            baseline_kpis = latest_overall.get('baseline_kpis')
            if baseline_kpis and isinstance(baseline_kpis, dict):
                print("\nKPI Status Summary:")
                for kpi_id, kpi_data in baseline_kpis.items():
                    if isinstance(kpi_data, dict):
                        status = kpi_data.get('status', 'Unknown')
                        status_icon = {"Target Met": "✅", "Above Target": "⚠️", "Below Target": "❌", 
                                      "Needs Improvement": "⚠️", "Critical": "🚨"}.get(status, "❓")
                        print(f"  {status_icon} {kpi_id}: {status}")
        else:
            print("❌ No recent processing results found")
        
        # Configuration Analysis
        print(f"\n⚙️  CONFIGURATION ANALYSIS")
        print("-"*60)
        
        enabled_kpis = self.config_analysis.get('kpis_enabled', [])
        disabled_kpis = self.config_analysis.get('kpis_disabled', [])
        
        print(f"KPIs Enabled: {len(enabled_kpis)}")
        for kpi in enabled_kpis:
            print(f"  ✅ {kpi['id']}: {kpi['name']} ({kpi['priority']} priority)")
        
        if disabled_kpis:
            print(f"\nKPIs Disabled: {len(disabled_kpis)}")
            for kpi in disabled_kpis:
                print(f"  ❌ {kpi['id']}: {kpi['name']}")
        
        config_issues = self.config_analysis.get('configuration_issues', [])
        if config_issues:
            print("\nConfiguration Issues:")
            for issue in config_issues:
                print(f"  ⚠️  {issue}")
        
        # Performance Trends
        print(f"\n📈 PERFORMANCE TRENDS")
        print("-"*60)
        
        performance_summary = self.performance_trends.get('performance_summary', {})
        if performance_summary:
            avg_score = performance_summary.get('average_recent_score', 0)
            best_score = performance_summary.get('best_recent_score', 0)
            trend = performance_summary.get('score_trend', 'stable')
            
            trend_icon = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(trend, "❓")
            print(f"Recent Average Score: {avg_score}/100")
            print(f"Best Recent Score: {best_score}/100")
            print(f"Trend: {trend_icon} {trend.title()}")
        else:
            print("❌ Insufficient data for trend analysis")
        
        # Processing History
        history = self.performance_trends.get('processing_history', [])
        if history:
            print(f"\nRecent Processing Activity ({len(history)} runs):")
            for record in history[-5:]:  # Show last 5
                timestamp = record['timestamp']
                mode = record['mode']
                records = record.get('records', 0)
                score = record.get('overall_score', 'N/A')
                print(f"  📋 {timestamp} - {mode:12} - {records:,} records - Score: {score}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-"*60)
        
        if self.recommendations:
            for i, rec in enumerate(self.recommendations, 1):
                priority = rec['priority']
                priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
                
                print(f"{i}. {priority_icon} {rec['category']} ({priority} Priority)")
                print(f"   Issue: {rec['issue']}")
                print(f"   Action: {rec['recommendation']}")
                print()
        else:
            print("✅ No recommendations - system appears to be operating well!")
        
        # Footer
        print("="*80)
        print("💡 TIP: Run individual components from the main menu to address any issues")
        print("📧 Contact IT Service Management Team for additional support")
        print("="*80)
    
    def get_organization_name(self) -> str:
        """Get organization name from configuration"""
        config_path = self.config_dir / "kpi_config.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('metadata', {}).get('organization', 'Unknown Organization')
            except:
                pass
        return 'Unknown Organization'
    
    def save_summary_report(self):
        """Save summary report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"final_summary_{timestamp}.json"
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'organization': self.get_organization_name(),
            'system_health': self.system_health,
            'latest_results': self.latest_results,
            'config_analysis': self.config_analysis,
            'performance_trends': self.performance_trends,
            'recommendations': self.recommendations
        }
        
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"\n💾 Summary report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not save summary report: {e}")

def main():
    """Main function to generate final summary"""
    print("🚀 KPI Processing System - Final Summary Generator")
    print("="*80)
    
    generator = FinalSummaryGenerator()
    
    try:
        generator.generate_summary()
        
        print("\n✨ Summary generation completed!")
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\n👋 Summary generation cancelled!")
    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
