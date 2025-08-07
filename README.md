# ServiceNow ITSM KPI Processing System

A comprehensive, configurable KPI processing system for ServiceNow ITSM data with support for baseline, incremental, and targeted processing modes.

## 🚀 Features

- **Fully Configurable**: External YAML configuration for all KPI specifications, thresholds, and business rules
- **Multiple Processing Modes**: Baseline, incremental, and targeted KPI updates
- **Real-time Analytics**: Geographic analysis and performance scoring
- **Production Ready**: Comprehensive validation, error handling, and caching
- **Scalable Architecture**: Supports large datasets with incremental processing

## 📊 Supported KPIs

- **SM001**: Major Incidents (P1/P2) tracking and management
- **SM002**: ServiceNow Backlog (Incident Aging) monitoring  
- **SM003**: Service Request Aging analysis (configurable)
- **SM004**: First Time Fix Rate measurement
- **GEOGRAPHIC**: Multi-country incident distribution analysis

## 🛠️ Quick Start

### Prerequisites

```bash
Python 3.8+
pandas
pyyaml
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/glynncv/kpi_processor_test.git
cd kpi_processor_test
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install pandas pyyaml
```

### Basic Usage

1. **Validate Configuration**:
```bash
python scripts/config_validator.py --config config/complete_kpi_config.yaml
```

2. **Run Baseline Processing**:
```bash
python scripts/complete_configurable_processor.py --config config/complete_kpi_config.yaml --mode baseline --input data/raw/your_data.csv
```

3. **Run Incremental Updates**:
```bash
python scripts/complete_configurable_processor.py --config config/complete_kpi_config.yaml --mode incremental --input data/raw/updated_data.csv
```

4. **Test Complete System**:
```bash
python test_system.py
```

5. **View Processed Results**:
```bash
python show_results.py
```

6. **Generate Final Summary**:
```bash
python final_summary.py
```

## 📁 Project Structure

```
kpi_processor_test/
├── config/
│   └── complete_kpi_config.yaml      # Main configuration file
├── scripts/
│   ├── complete_configurable_processor.py        # Main processor
│   ├── config_validator.py           # Configuration validator
├── data/
│   └── raw/                          # Input data files
├── output/                           # Generated results
├── cache/                            # Processing cache
├── test_cache/                       # Test cache directory
├── logs/                             # System logs
├── venv/                             # Python virtual environment
├── run_kpi_menu.bat                  # 🎛️ Main interactive menu system
├── quick_baseline.bat                # ⚡ Quick baseline processing
├── quick_incremental.bat             # ⚡ Quick incremental processing
├── validate_config.bat               # 🔍 Configuration validation menu
├── targeted_kpi.bat                  # 🎯 Targeted KPI processing menu
├── system_management.bat             # 🔧 System administration tools
├── setup.bat                         # 🛠️ First-time setup assistant
├── run_complete_pipeline.bat         # 🚀 End-to-end pipeline automation
├── test_system.py                    # System test script
├── show_results.py                   # Results display helper
├── final_summary.py                  # Summary generation script
└── README.md
```

## �️ Windows Batch File Automation

For Windows users, the system includes comprehensive batch file automation that eliminates the need to remember command-line parameters:

### 🎛️ Main Menu System
- **`run_kpi_menu.bat`** - Complete interactive menu system
  - All processing modes (baseline, incremental, targeted)
  - Configuration validation options
  - Advanced settings and cache management
  - Built-in file validation and error checking

```cmd
run_kpi_menu.bat
```

### ⚡ Quick Processing Scripts
- **`quick_baseline.bat`** - One-click baseline processing with defaults
  - Uses `config\kpi_config.yaml` and `data\consolidated_data.csv`
  - No prompts, immediate processing
  - Perfect for routine baseline runs

- **`quick_incremental.bat`** - One-click incremental processing
  - Automatic baseline cache checking
  - Fast incremental updates
  - Error handling for missing baseline

```cmd
quick_baseline.bat
quick_incremental.bat
```

### 🎯 Specialized Menu Systems
- **`validate_config.bat`** - Configuration validation menu
  - Config-only validation
  - Config + data compatibility checking
  - Strict validation modes
  - Report generation

- **`targeted_kpi.bat`** - KPI-specific processing menu
  - Individual KPI selection (SM001, SM002, SM003, SM004, GEOGRAPHIC)
  - Detailed KPI descriptions and guidance
  - Efficiency reporting

```cmd
validate_config.bat
targeted_kpi.bat
```

### 🔧 System Management
- **`system_management.bat`** - Complete system administration
  - System status monitoring
  - Cache management and clearing
  - Log file viewing
  - Environment checking
  - Results summary display

- **`setup.bat`** - First-time setup and installation
  - Python installation verification
  - Package installation assistance
  - Virtual environment setup
  - Directory structure creation
  - Dependency checking

```cmd
system_management.bat
setup.bat
```

### 🚀 Complete Pipeline Automation
- **`run_complete_pipeline.bat`** - End-to-end processing workflow
  - Automatic validation → baseline → incremental → summary
  - Perfect for complete processing runs
  - Built-in error checking at each stage

```cmd
run_complete_pipeline.bat
```

### 📋 Batch File Features
- **User-Friendly Menus**: No command-line knowledge required
- **Error Validation**: Automatic file existence checking
- **Built-in Help**: Descriptions and guidance throughout
- **Flexible Options**: Both quick-run and interactive modes
- **Comprehensive Coverage**: All system functions accessible

## �🛠️ Helper Scripts

### test_system.py
Comprehensive system testing script that validates:
- Configuration loading and validation
- Data processing with real ServiceNow data  
- All three processing modes (baseline/incremental/targeted)
- Output generation and caching

```bash
python test_system.py
```

### show_results.py
Display formatted results from processed KPI data:
- KPI performance summary
- Geographic analysis breakdown
- Overall scoring and status

```bash
python show_results.py
```

### final_summary.py
Generate comprehensive system summary including:
- Processing statistics
- Performance metrics
- System capabilities overview

```bash
python final_summary.py
```

## 🎯 Sample Results

Recent test with 2,385 ServiceNow incidents:

```
Records Processed: 2,385
KPIs Calculated: 4 (SM001, SM002, SM004, GEOGRAPHIC)
Countries Analyzed: 12 (UK, France, Turkey, Romania, Poland, etc.)
Overall Score: 72.9 (Needs Improvement)

KPI Performance:
• SM001 (Major Incidents): Above Target (10 P2 incidents)
• SM002 (ServiceNow Backlog): Target Met (0% backlog)  
• SM004 (First Time Fix): Critical (41.6% vs 80% target)
• Geographic Analysis: Available (12 countries)
```

## 🔧 Configuration

The system uses YAML configuration for complete customization:

```yaml
metadata:
  version: "2.0"
  organization: "Global IT Services"
  
kpis:
  SM001:
    name: "Major Incidents (P1/P2)"
    enabled: true
    calculation:
      method: "priority_count"
    targets:
      p1_max: 0
      p2_max: 5
```

## 📈 Processing Modes

### Baseline Mode
Complete processing of all data to establish baseline KPIs:
```bash
python scripts/complete_configurable_processor.py --config config.yaml --mode baseline --input data.csv
```

### Incremental Mode
Efficient updates processing only changed records:
```bash
python scripts/complete_configurable_processor.py --config config.yaml --mode incremental --input data.csv
```

### Targeted Mode
Update specific KPIs with minimal processing:
```bash
python scripts/complete_configurable_processor.py --config config.yaml --mode targeted --kpi SM001 --input data.csv
```

## 🌍 Geographic Analysis

The system provides detailed geographic analysis including:
- Country-wise incident distribution
- Priority breakdown by country
- Volume trends and KPI performance by region

## 📊 Validation & Quality

- **Configuration Validator**: Comprehensive YAML validation with business rule checking
- **Data Compatibility**: Automatic validation against actual data files
- **Error Handling**: Robust error handling with detailed logging
- **Schema Validation**: Ensures configuration compliance

## 🚀 Production Features

- **Caching System**: Intelligent caching for incremental processing
- **Performance Scoring**: Weighted KPI scoring with configurable bands
- **Export Capabilities**: JSON output with comprehensive metadata
- **Logging**: Detailed logging with configurable levels

## 🔍 Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

This validates:
- Configuration loading and validation
- Data processing with real ServiceNow data
- All three processing modes
- Output generation and caching

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions and support:
- Create an issue in this repository
- Contact the development team

## 🏆 Achievements

✅ **Fully Operational System**  
✅ **Real Data Tested** (2,385+ ServiceNow incidents)  
✅ **Multi-Country Support** (12 countries analyzed)  
✅ **Production Ready** (Comprehensive validation & error handling)  
✅ **Configurable Architecture** (Zero hardcoded specifications)  
✅ **Performance Optimized** (Incremental processing with caching)
