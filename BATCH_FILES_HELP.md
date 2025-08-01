# Windows Batch Files Help Documentation

## 🖥️ Complete Guide to KPI Processing Batch File Automation

This document provides comprehensive help for all Windows batch files included in the KPI Processing System.

## 📋 Quick Reference

| Batch File | Purpose | Usage Type |
|------------|---------|------------|
| `run_kpi_menu.bat` | Main interactive menu | Interactive |
| `quick_baseline.bat` | Fast baseline processing | One-click |
| `quick_incremental.bat` | Fast incremental processing | One-click |
| `validate_config.bat` | Configuration validation | Interactive |
| `targeted_kpi.bat` | KPI-specific processing | Interactive |
| `system_management.bat` | System administration | Interactive |
| `setup.bat` | First-time setup | Interactive |
| `run_complete_pipeline.bat` | Full pipeline automation | One-click |

---

## 🎛️ Main Menu System

### `run_kpi_menu.bat`

**Purpose**: Complete interactive menu system for all KPI processing operations

**Features**:
- Full menu-driven interface
- All processing modes (baseline, incremental, targeted)
- Configuration validation options
- Advanced settings and cache management
- Built-in file validation and error checking

**Menu Options**:
1. **Run Baseline Processing** - Complete baseline KPI calculation
2. **Run Incremental Processing** - Update existing KPIs with new data
3. **Run Targeted KPI Processing** - Process specific KPIs only
4. **Validate Configuration** - Check configuration files
5. **Show Results** - Display processed results
6. **Test System** - Run comprehensive system tests
7. **View Final Summary** - Generate system summary
8. **Quick Processing** - One-click processing with defaults
9. **Advanced Options** - Custom settings and cache management

**Usage**:
```cmd
# Double-click the file or run from command line
run_kpi_menu.bat
```

**Requirements**:
- Configuration file: `config\kpi_config.yaml`
- Data files in: `data\` folder
- Python environment properly configured

---

## ⚡ Quick Processing Scripts

### `quick_baseline.bat`

**Purpose**: One-click baseline processing with default settings

**Features**:
- No prompts or user interaction required
- Uses default configuration and data files
- Automatic error checking
- Immediate processing start

**Default Files Used**:
- Config: `config\kpi_config.yaml`
- Data: `data\consolidated_data.csv`
- Output: `output\baseline_quick.json`

**Usage**:
```cmd
quick_baseline.bat
```

**Prerequisites**:
- Ensure `data\consolidated_data.csv` exists
- Ensure `config\kpi_config.yaml` exists
- Python environment configured

### `quick_incremental.bat`

**Purpose**: One-click incremental processing with default settings

**Features**:
- Automatic baseline cache checking
- Fast incremental updates
- Error handling for missing baseline
- No user interaction required

**Default Files Used**:
- Config: `config\kpi_config.yaml`
- Data: `data\consolidated_data.csv`
- Output: `output\incremental_quick.json`

**Usage**:
```cmd
quick_incremental.bat
```

**Prerequisites**:
- Baseline processing must have been run first
- Cache directory must contain baseline data
- Same file requirements as quick_baseline.bat

---

## 🔍 Configuration Management

### `validate_config.bat`

**Purpose**: Interactive configuration validation with multiple options

**Menu Options**:
1. **Quick validation** - Config file only
2. **Full validation** - Config + data compatibility
3. **Strict validation** - Config only with strict rules
4. **Strict validation + data** - Complete validation
5. **Generate validation report** - Create detailed report

**Features**:
- Multiple validation levels
- Data compatibility checking
- Report generation
- Detailed error descriptions

**Usage**:
```cmd
validate_config.bat
```

**Output Files**:
- Validation reports saved to: `output\validation_report.txt`

---

## 🎯 Specialized Processing

### `targeted_kpi.bat`

**Purpose**: KPI-specific processing with detailed guidance

**Supported KPIs**:
1. **SM001** - Major Incidents (Priority 1 & 2)
2. **SM002** - ServiceNow Backlog
3. **SM003** - Service Request Aging
4. **SM004** - First Time Fix Rate
5. **GEOGRAPHIC** - Geographic Analysis

**Features**:
- Individual KPI selection
- Detailed KPI descriptions
- Processing efficiency reporting
- Reusable for multiple KPIs

**Usage**:
```cmd
targeted_kpi.bat
```

**Output Files**:
- Results saved as: `output\targeted_{KPI_ID}_results.json`

---

## 🔧 System Administration

### `system_management.bat`

**Purpose**: Complete system administration and monitoring

**Menu Options**:
1. **View System Status** - Check all components
2. **Check Cache Status** - Review cached data
3. **Clear Cache** - Remove all cached processing data
4. **View Log Files** - Browse system logs
5. **Show Results Summary** - Display processed results
6. **Test System** - Run comprehensive tests
7. **Show Final Summary** - Generate system overview
8. **Environment Check** - Verify Python and dependencies

**Features**:
- Complete system monitoring
- Cache management
- Log file viewing
- Environment verification
- Results display

**Usage**:
```cmd
system_management.bat
```

### `setup.bat`

**Purpose**: First-time setup and installation assistance

**Menu Options**:
1. **Check Python Installation** - Verify Python is installed
2. **Install Required Packages** - Install dependencies
3. **Setup Virtual Environment** - Create isolated environment
4. **Create Required Directories** - Build folder structure
5. **Check All Dependencies** - Verify all components
6. **First-Time Setup** - Complete automated setup

**Features**:
- Python installation verification
- Package installation assistance
- Virtual environment setup
- Directory structure creation
- Comprehensive dependency checking

**Usage**:
```cmd
setup.bat
```

---

## 🚀 Pipeline Automation

### `run_complete_pipeline.bat`

**Purpose**: End-to-end processing workflow automation

**Pipeline Steps**:
1. **Validate Configuration** - Check config files
2. **Run Baseline Processing** - Calculate baseline KPIs
3. **Run Incremental Processing** - Update with latest data
4. **Generate Final Summary** - Create comprehensive report

**Features**:
- Fully automated workflow
- Error checking at each stage
- Complete processing pipeline
- No user interaction required

**Usage**:
```cmd
run_complete_pipeline.bat
```

**Output Files**:
- `output\pipeline_baseline.json`
- `output\pipeline_incremental.json`
- Final summary displayed on screen

**Prerequisites**:
- All default files must exist
- Python environment properly configured
- No missing dependencies

---

## 🛠️ Common Troubleshooting

### File Not Found Errors

**Problem**: "Error: File not found"
**Solution**: 
- Ensure data files exist in `data\` folder
- Check configuration file exists: `config\kpi_config.yaml`
- Verify file names match exactly

### Python Environment Issues

**Problem**: "Python command not found"
**Solution**:
- Run `setup.bat` to check Python installation
- Verify Python is in system PATH
- Consider using virtual environment

### Configuration Validation Failures

**Problem**: Configuration validation errors
**Solution**:
- Run `validate_config.bat` for detailed analysis
- Check YAML syntax in configuration file
- Verify all required sections are present

### Cache Issues

**Problem**: "No baseline found" for incremental processing
**Solution**:
- Run baseline processing first using `quick_baseline.bat`
- Check cache directory exists and has files
- Clear cache and rebuild if corrupted

### Permission Errors

**Problem**: "Access denied" or permission errors
**Solution**:
- Run command prompt as Administrator
- Check file/folder permissions
- Ensure antivirus is not blocking files

---

## 📊 Understanding Output

### Success Indicators
- ✅ Green checkmarks indicate successful operations
- File paths shown for generated outputs
- Record counts and processing statistics displayed

### Error Indicators
- ❌ Red X marks indicate failures
- Detailed error messages provided
- Suggestions for resolution included

### Status Messages
- ⚠️ Warnings for non-critical issues
- ℹ️ Information messages for guidance
- 🎯 Progress indicators during processing

---

## 🔗 Integration with Python Scripts

### Direct Python Equivalents

Each batch file corresponds to Python commands:

```cmd
# Batch file equivalent to:
quick_baseline.bat
# Python command:
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode baseline --input data\consolidated_data.csv
```

### Advanced Usage
For advanced users who prefer command-line:
- All batch files can be modified to change default parameters
- Python scripts can be called directly with custom arguments
- Configuration files can be customized for specific needs

---

## 📞 Getting Help

### Built-in Help
- All menu systems include guidance and descriptions
- Error messages provide specific troubleshooting steps
- File validation includes helpful suggestions

### System Information
- Use `system_management.bat` → "Environment Check" for system details
- Check `README.md` for comprehensive documentation
- Review log files for detailed processing information

### Common Commands for Manual Troubleshooting
```cmd
# Check Python version
python --version

# Verify packages
python -c "import pandas, yaml; print('Packages OK')"

# List data files
dir data\*.csv

# Check configuration
type config\kpi_config.yaml
```

---

This help documentation covers all aspects of the Windows batch file automation system. Each batch file is designed to be self-explanatory with built-in guidance, but this document provides comprehensive reference information for all features and troubleshooting scenarios.
