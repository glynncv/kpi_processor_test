#!/usr/bin/env python3
"""
Results Display System for KPI Processor
========================================

Displays processed KPI results in a user-friendly format.
Automatically detects and shows the latest results from various processing modes.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob

class ResultsDisplay:
    """Display KPI processing results with formatted output"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.results_files = []
        self.latest_results = {}
        
    def scan_for_results(self):
        """Scan output directory for result files"""
        if not self.output_dir.exists():
            print(f"❌ Output directory '{self.output_dir}' not found!")
            return False
            
        # Find all JSON result files using pathlib for better performance
        self.results_files = [str(p) for p in self.output_dir.glob("*.json")]
        
        if not self.results_files:
            print(f"❌ No result files found in '{self.output_dir}'")
            return False
            
        print(f"📁 Found {len(self.results_files)} result files")
        return True
    
    def load_latest_results(self):
        """Load the most recent results by category"""
        categories = {
            'baseline': ['baseline_results.json', 'baseline_test_results.json', 'quick_results.json'],
            'incremental': ['incremental_results.json', 'incremental_test_results.json'],
            'targeted': ['targeted_', 'sm001_test_results.json', 'sm004_test_results.json'],
            'test': ['test_', 'validation_'],
            'other': []
        }
        
        for file_path in self.results_files:
            file_name = Path(file_path).name
            categorized = False
            
            for category, patterns in categories.items():
                if any(pattern in file_name.lower() for pattern in patterns):
                    if category not in self.latest_results:
                        self.latest_results[category] = []
                    
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            data['_file_name'] = file_name
                            data['_file_path'] = file_path
                            data['_file_time'] = os.path.getmtime(file_path)
                            self.latest_results[category].append(data)
                            categorized = True
                            break
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"⚠️  Warning: Could not load {file_name}: {e}")
            
            if not categorized:
                if 'other' not in self.latest_results:
                    self.latest_results['other'] = []
                self.latest_results['other'].append({'_file_name': file_name, '_file_path': file_path})
        
        # Sort by modification time (newest first)
        for category in self.latest_results:
            self.latest_results[category].sort(key=lambda x: x.get('_file_time', 0), reverse=True)
    
    def display_main_menu(self):
        """Display main results menu"""
        print("\n" + "="*80)
        print("                         KPI RESULTS VIEWER")
        print("="*80)
        
        if not self.latest_results:
            print("❌ No valid result files found!")
            return False
        
        menu_options = []
        option_num = 1
        
        # Add category options
        if 'baseline' in self.latest_results and self.latest_results['baseline']:
            print(f"{option_num}. 📊 View Baseline Results ({len(self.latest_results['baseline'])} files)")
            menu_options.append(('baseline', 'View Baseline Results'))
            option_num += 1
        
        if 'incremental' in self.latest_results and self.latest_results['incremental']:
            print(f"{option_num}. 🔄 View Incremental Results ({len(self.latest_results['incremental'])} files)")
            menu_options.append(('incremental', 'View Incremental Results'))
            option_num += 1
        
        if 'targeted' in self.latest_results and self.latest_results['targeted']:
            print(f"{option_num}. 🎯 View Targeted KPI Results ({len(self.latest_results['targeted'])} files)")
            menu_options.append(('targeted', 'View Targeted Results'))
            option_num += 1
        
        if 'test' in self.latest_results and self.latest_results['test']:
            print(f"{option_num}. 🧪 View Test Results ({len(self.latest_results['test'])} files)")
            menu_options.append(('test', 'View Test Results'))
            option_num += 1
        
        # Summary options
        print(f"{option_num}. 📋 Show All Files Summary")
        menu_options.append(('summary', 'Show Summary'))
        option_num += 1
        
        print(f"{option_num}. 🏆 Show Latest Overall Results")
        menu_options.append(('latest', 'Show Latest'))
        option_num += 1
        
        print(f"{option_num}. 🔍 Search/Filter Results")
        menu_options.append(('search', 'Search Results'))
        option_num += 1
        
        print(f"0. 🚪 Exit")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (0-{0}): ".format(option_num-1))
                
                if choice == "0":
                    return False
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(menu_options):
                    action, description = menu_options[choice_idx]
                    self.handle_menu_choice(action)
                    input("\nPress Enter to continue...")
                    self.display_main_menu()
                    return True
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input. Please enter a number.")
        
        return True
    
    def handle_menu_choice(self, action: str):
        """Handle menu selections"""
        if action in ['baseline', 'incremental', 'targeted', 'test']:
            self.display_category_results(action)
        elif action == 'summary':
            self.display_files_summary()
        elif action == 'latest':
            self.display_latest_overall()
        elif action == 'search':
            self.search_results()
    
    def display_category_results(self, category: str):
        """Display results for a specific category"""
        results = self.latest_results.get(category, [])
        if not results:
            print(f"❌ No {category} results found!")
            return
        
        print(f"\n📊 {category.upper()} RESULTS")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['_file_name']}")
            print(f"   Modified: {datetime.fromtimestamp(result['_file_time']).strftime('%Y-%m-%d %H:%M:%S')}")
            
            if 'mode' in result:
                print(f"   Mode: {result['mode']}")
            if 'records_processed' in result:
                print(f"   Records: {result['records_processed']:,}")
            if 'overall_score' in result:
                score_data = result['overall_score']
                if isinstance(score_data, dict):
                    score = score_data.get('overall_score', 'Unknown')
                    band = score_data.get('performance_band', 'Unknown')
                    print(f"   Overall Score: {score}/100 ({band})")
                else:
                    print(f"   Overall Score: {score_data}")
        
        print(f"\nSelect a file to view details (1-{len(results)}) or 0 to go back:")
        try:
            choice = int(input("Choice: "))
            if choice == 0:
                return
            elif 1 <= choice <= len(results):
                self.display_detailed_results(results[choice-1])
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Invalid input!")
    
    def display_detailed_results(self, result: Dict[str, Any]):
        """Display detailed results for a specific file"""
        print(f"\n📄 DETAILED RESULTS: {result['_file_name']}")
        print("="*80)
        
        # Basic information
        if 'mode' in result:
            print(f"🔧 Processing Mode: {result['mode']}")
        if 'records_processed' in result:
            print(f"📊 Records Processed: {result['records_processed']:,}")
        if 'config_version' in result:
            print(f"⚙️  Configuration Version: {result['config_version']}")
        if 'processing_time' in result:
            print(f"⏱️  Processing Time: {result['processing_time']}")
        
        # Overall scoring
        if 'overall_score' in result:
            print(f"\n🏆 OVERALL PERFORMANCE")
            print("-"*40)
            score_data = result['overall_score']
            if isinstance(score_data, dict):
                print(f"Score: {score_data.get('overall_score', 'Unknown')}/100")
                print(f"Performance Band: {score_data.get('performance_band', 'Unknown')}")
                if 'components' in score_data:
                    print("Component Scores:")
                    for component, score in score_data['components'].items():
                        print(f"  • {component}: {score}")
            else:
                print(f"Score: {score_data}")
        
        # KPI Results
        if 'baseline_kpis' in result:
            self.display_kpi_details(result['baseline_kpis'], "BASELINE KPI RESULTS")
        elif 'updated_kpi' in result:
            print(f"\n🎯 TARGETED KPI UPDATE")
            print("-"*40)
            kpi_data = result['updated_kpi']
            self.display_single_kpi(result.get('kpi_id', 'Unknown'), kpi_data)
        elif 'affected_kpis' in result:
            print(f"\n🔄 INCREMENTAL UPDATE RESULTS")
            print("-"*40)
            print(f"Affected KPIs: {', '.join(result.get('affected_kpis', []))}")
            if 'updated_kpis' in result:
                self.display_kpi_details(result['updated_kpis'], "UPDATED KPI RESULTS")
        
        # Geographic analysis
        if 'geographic_analysis' in result and result['geographic_analysis']:
            print(f"\n🌍 GEOGRAPHIC ANALYSIS AVAILABLE")
            if 'baseline_kpis' in result and 'GEOGRAPHIC' in result['baseline_kpis']:
                geo_data = result['baseline_kpis']['GEOGRAPHIC']
                if 'country_distribution' in geo_data:
                    print("Top Countries:")
                    for country, count in geo_data['country_distribution'].items():
                        print(f"  • {country}: {count} incidents")
        
        # Processing efficiency
        if 'processing_speedup' in result:
            print(f"\n⚡ PROCESSING EFFICIENCY")
            print(f"Speedup Factor: {result['processing_speedup']}")
        
        if 'changes_detected' in result:
            print(f"Changes Detected: {'Yes' if result['changes_detected'] else 'No'}")
    
    def display_kpi_details(self, kpis: Dict[str, Any], title: str):
        """Display KPI details in formatted manner"""
        print(f"\n📈 {title}")
        print("-"*60)
        
        for kpi_id, kpi_data in kpis.items():
            self.display_single_kpi(kpi_id, kpi_data)
    
    def display_single_kpi(self, kpi_id: str, kpi_data: Dict[str, Any]):
        """Display a single KPI's details"""
        print(f"\n🔹 {kpi_id}: {kpi_data.get('name', 'Unknown KPI')}")
        
        status = kpi_data.get('status', 'Unknown')
        status_icon = {"Target Met": "✅", "Above Target": "⚠️", "Below Target": "❌", 
                      "Needs Improvement": "⚠️", "Critical": "🚨"}.get(status, "❓")
        print(f"   Status: {status_icon} {status}")
        
        # KPI-specific metrics
        if kpi_id == 'SM001':
            if 'p1_count' in kpi_data:
                print(f"   P1 Incidents: {kpi_data['p1_count']}")
            if 'p2_count' in kpi_data:
                print(f"   P2 Incidents: {kpi_data['p2_count']}")
        elif kpi_id == 'SM002':
            if 'backlog_count' in kpi_data:
                print(f"   Backlog Count: {kpi_data['backlog_count']}")
            if 'adherence_rate' in kpi_data:
                print(f"   Adherence Rate: {kpi_data['adherence_rate']:.1f}%")
        elif kpi_id == 'SM004':
            if 'ftf_rate' in kpi_data:
                print(f"   First Time Fix Rate: {kpi_data['ftf_rate']:.1f}%")
            if 'ftf_count' in kpi_data:
                print(f"   FTF Count: {kpi_data['ftf_count']}")
        elif kpi_id == 'GEOGRAPHIC':
            if 'country_count' in kpi_data:
                print(f"   Countries Analyzed: {kpi_data['country_count']}")
    
    def display_files_summary(self):
        """Display summary of all result files"""
        print(f"\n📋 FILES SUMMARY")
        print("="*80)
        
        total_files = sum(len(files) for files in self.latest_results.values())
        print(f"Total Result Files: {total_files}")
        
        for category, files in self.latest_results.items():
            if files:
                print(f"\n📁 {category.upper()} ({len(files)} files):")
                for file_data in files:
                    file_time = datetime.fromtimestamp(file_data['_file_time']).strftime('%Y-%m-%d %H:%M')
                    print(f"   • {file_data['_file_name']} ({file_time})")
    
    def display_latest_overall(self):
        """Display the most recent overall results"""
        print(f"\n🏆 LATEST OVERALL RESULTS")
        print("="*80)
        
        # Find the most recent baseline result
        latest_baseline = None
        latest_time = 0
        
        for category, files in self.latest_results.items():
            for file_data in files:
                if file_data.get('_file_time', 0) > latest_time and 'overall_score' in file_data:
                    latest_baseline = file_data
                    latest_time = file_data['_file_time']
        
        if latest_baseline:
            print(f"📄 Source: {latest_baseline['_file_name']}")
            print(f"🕒 Processed: {datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')}")
            self.display_detailed_results(latest_baseline)
        else:
            print("❌ No results with overall scores found!")
    
    def search_results(self):
        """Search and filter results"""
        print(f"\n🔍 SEARCH RESULTS")
        print("="*60)
        
        search_term = input("Enter search term (KPI ID, status, or keyword): ").lower()
        
        matches = []
        for category, files in self.latest_results.items():
            for file_data in files:
                # Search in file name
                if search_term in file_data.get('_file_name', '').lower():
                    matches.append((category, file_data, 'filename'))
                
                # Search in KPI data
                if 'baseline_kpis' in file_data:
                    for kpi_id, kpi_data in file_data['baseline_kpis'].items():
                        if (search_term in kpi_id.lower() or 
                            search_term in kpi_data.get('status', '').lower() or
                            search_term in kpi_data.get('name', '').lower()):
                            matches.append((category, file_data, f'kpi_{kpi_id}'))
        
        if matches:
            print(f"\n✅ Found {len(matches)} matches:")
            for i, (category, file_data, match_type) in enumerate(matches, 1):
                print(f"{i}. {file_data['_file_name']} ({category}) - matched: {match_type}")
            
            try:
                choice = int(input(f"\nView details for match (1-{len(matches)}) or 0 to go back: "))
                if 1 <= choice <= len(matches):
                    _, file_data, _ = matches[choice-1]
                    self.display_detailed_results(file_data)
            except ValueError:
                print("❌ Invalid input!")
        else:
            print(f"❌ No matches found for '{search_term}'")

def main():
    """Main function to run the results display system"""
    print("🚀 KPI Results Display System")
    print("Loading results...")
    
    display = ResultsDisplay()
    
    if not display.scan_for_results():
        print("\n💡 Tip: Run some KPI processing first to generate results!")
        input("Press Enter to exit...")
        return
    
    display.load_latest_results()
    
    try:
        while display.display_main_menu():
            pass
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    print("\n✨ Thanks for using the KPI Results Display System!")

if __name__ == "__main__":
    main()
