#!/usr/bin/env python3
"""
Quick Fix Script to Add Missing Methods
=======================================

This script will add the missing methods to your complete_configurable_processor.py file.

Usage:
    python quick_fix_script.py

This will modify your complete_configurable_processor.py file in place.
"""

import os
import re

def add_missing_methods():
    """Add the missing methods to the processor file"""
    
    # The missing methods as strings
    missing_methods = '''
    def _update_affected_counts(self, changes: Dict[str, Any]) -> Dict[str, int]:
        """Update baseline counts based on detected changes"""
        self.logger.info("📊 Updating affected counts based on changes...")
        
        # Start with existing baseline counts
        updated_counts = self.baseline_counts.copy()
        
        if changes.get('has_changes', False):
            total_changes = changes.get('total_changes', 0)
            
            # Update total tickets count if new records were added
            if changes.get('new_records', 0) > 0:
                updated_counts['total_tickets'] = updated_counts.get('total_tickets', 0) + changes['new_records']
            
            self.logger.info(f"Simplified count update: {total_changes} records changed")
        
        self.logger.info(f"✅ Updated {len(updated_counts)} count metrics")
        return updated_counts

    def _update_affected_kpis(self, changes: Dict[str, Any], updated_counts: Dict[str, int], df: pd.DataFrame) -> Dict[str, Dict]:
        """Update KPIs that are affected by the detected changes"""
        self.logger.info("🎯 Updating affected KPIs...")
        
        # Start with existing KPI cache
        updated_kpis = self.kpi_cache.copy()
        
        # Get list of affected KPIs from change detection
        affected_kpis = changes.get('affected_kpis', set())
        
        # Recalculate each affected KPI
        for kpi_id in affected_kpis:
            try:
                self.logger.debug(f"Updating KPI: {kpi_id}")
                
                # Recalculate the KPI using the updated counts and data
                updated_kpi = self._calculate_single_configurable_kpi(kpi_id, updated_counts, df)
                
                if updated_kpi:
                    updated_kpis[kpi_id] = updated_kpi
                    self.logger.debug(f"✅ Updated {kpi_id}: {updated_kpi.get('status', 'Unknown')}")
                else:
                    self.logger.warning(f"⚠️ Failed to update KPI {kpi_id}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error updating KPI {kpi_id}: {e}")
        
        self.logger.info(f"✅ Updated {len(affected_kpis)} affected KPIs")
        return updated_kpis

    def _calculate_targeted_kpi_counts(self, df: pd.DataFrame, kpi_id: str) -> Dict[str, int]:
        """Calculate counts needed for a specific KPI using configuration"""
        self.logger.debug(f"📊 Calculating targeted counts for {kpi_id}...")
        
        kpi_config = self.kpis_config.get(kpi_id, {})
        calculation_config = kpi_config.get('calculation', {})
        calculation_method = calculation_config.get('method', '')
        
        counts = {'total_tickets': len(df)}
        
        try:
            if calculation_method == 'priority_count' and 'priority' in df.columns:
                # SM001 - Major Incidents calculation
                priority_config = self.thresholds.get('priority', {})
                major_levels = priority_config.get('major_incident_levels', [1, 2])
                unknown_fallback = priority_config.get('unknown_fallback', 99)
                
                # Extract priority using configured pattern
                extraction_config = self.processing_rules.get('priority_extraction', {})
                regex_pattern = extraction_config.get('regex_pattern', r'\\d+')
                
                df['priority_numeric'] = df['priority'].str.extract(f'({regex_pattern})')[0].astype(float).fillna(unknown_fallback)
                
                # Count by priority level
                for level in major_levels:
                    counts[f'priority_{level}_tickets'] = int((df['priority_numeric'] == level).sum())
            
            elif calculation_method == 'zero_reassignments' and 'reassignment_count' in df.columns:
                # SM004 - First Time Fix calculation
                reassignment_config = self.processing_rules.get('numeric_handling', {})
                null_value = reassignment_config.get('reassignment_null_value', 0)
                
                df['reassignment_count'] = df['reassignment_count'].fillna(null_value)
                counts['zero_reassignments'] = int((df['reassignment_count'] == 0).sum())
            
            elif calculation_method == 'servicenow_backlog':
                # SM002 - ServiceNow Backlog calculation
                if all(col in df.columns for col in ['opened_at', 'resolved_at']):
                    df['opened_at'] = pd.to_datetime(df['opened_at'], errors='coerce')
                    current_date = datetime.now()
                    df['age_days'] = (current_date - df['opened_at']).dt.days
                    
                    # Get configurable backlog threshold
                    backlog_days = self.thresholds.get('aging', {}).get('backlog_days', 10)
                    df['is_resolved'] = df['resolved_at'].notna()
                    
                    # Apply ServiceNow backlog logic
                    backlog_mask = (
                        (df['is_resolved'] & (df['age_days'] > backlog_days)) |
                        (~df['is_resolved'] & (df['age_days'] > backlog_days))
                    )
                    counts['servicenow_backlog_total'] = int(backlog_mask.sum())
            
            elif calculation_method == 'country_distribution' and 'country' in df.columns:
                # GEOGRAPHIC - Country analysis
                counts['total_countries'] = df['country'].nunique()
                counts['geographic_data_available'] = 1
            
        except Exception as e:
            self.logger.error(f"Error calculating targeted counts for {kpi_id}: {e}")
        
        self.logger.debug(f"✅ Calculated {len(counts)} metrics for {kpi_id}")
        return counts
'''
    
    filename = 'scripts/complete_configurable_processor.py'
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found in current directory")
        print("Make sure you're running this script in the same directory as your processor file")
        return False
    
    try:
        # Read the existing file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the best place to insert the methods (before the cache management methods)
        insert_position = content.find('def _load_baseline_counts(self)')
        
        if insert_position == -1:
            # Alternative insertion point
            insert_position = content.find('def main():')
        
        if insert_position == -1:
            print("❌ Could not find insertion point in the file")
            return False
        
        # Insert the missing methods
        new_content = content[:insert_position] + missing_methods + '\n\n    ' + content[insert_position:]
        
        # Create a backup
        backup_filename = f"{filename}.backup"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_filename}")
        
        # Write the updated file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Successfully added missing methods to {filename}")
        print(f"📊 Added 3 missing methods:")
        print(f"   • _update_affected_counts")
        print(f"   • _update_affected_kpis") 
        print(f"   • _calculate_targeted_kpi_counts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error modifying file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 QUICK FIX: Adding Missing Methods to Configurable Processor")
    print("="*60)
    
    success = add_missing_methods()
    
    if success:
        print("\n🎉 SUCCESS! Your processor file is now complete.")
        print("\n📋 Next steps:")
        print("1. Test the configuration validator:")
        print("   python config_validator.py --config config/kpi_config.yaml")
        print("\n2. Test the complete processor:")
        print("   python complete_configurable_processor.py --config config/kpi_config.yaml --mode baseline --input your_data.csv")
    else:
        print("\n❌ Fix failed. You may need to manually add the methods.")
        print("Copy the methods from the 'missing_methods' artifact and add them to your processor class.")
