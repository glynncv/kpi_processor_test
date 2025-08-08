# KPI Processor Test

A minimalist, efficient KPI processing system for ServiceNow ITSM data analysis with configurable thresholds and automated validation.

## 🚀 Features

- **Configurable KPI Processing**: Baseline, incremental, and targeted processing modes
- **Flexible Column Mapping**: Adapts to different ServiceNow CSV structures
- **Data Validation**: Comprehensive configuration and data compatibility checking
- **Efficient Processing**: Optimized pandas operations for large datasets
- **Date Format Support**: Handles DD/MM/YYYY European date formats
- **Defensive Programming**: Graceful handling of missing columns with clear warnings

## 📊 Supported KPIs

- **SM001**: Major Incidents (P1/P2) tracking and management
- **SM002**: ServiceNow Backlog (Incident Aging) monitoring
- **SM004**: First Time Fix Rate measurement
- **GEOGRAPHIC**: Multi-country incident distribution analysis

## 🛠️ Quick Start

### Prerequisites

```bash
Python 3.7+
pandas
pyyaml
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/glynncv/kpi_processor_test.git
cd kpi_processor_test
```

2. Install dependencies:
```bash
pip install pandas pyyaml
```

### Basic Usage

#### 1. Validate Configuration
```bash
python scripts/config_validator.py --config config/kpi_config.yaml
```

#### 2. Process Your Data
```bash
# Baseline processing
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode baseline --input "your_data.csv"

# Incremental processing
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode incremental --input "your_data.csv"

# Targeted KPI processing
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode targeted --kpi SM001 --input "your_data.csv"
```

#### 3. Auto-Detection Processing
```bash
# Core processor with auto-detection
python scripts/kpi_processor.py --mode baseline --input "your_data.csv"
```

## 📁 Project Structure

```
kpi_processor_test/
├── config/
│   └── kpi_config.yaml               # Main configuration file
├── scripts/
│   ├── complete_configurable_processor.py  # Main KPI processor
│   ├── config_validator.py          # Configuration validation
│   ├── kpi_processor.py              # Core processor with auto-detection
│   ├── validation_utils.py           # Shared validation functions
│   └── path_config.py                # Configurable path management
├── data/                             # Input data files (create as needed)
├── output/                           # Generated results (auto-created)
├── cache/                            # Processing cache (auto-created)
└── README.md
```

## 🔧 Configuration

The system uses `config/kpi_config.yaml` for complete customization:

### Column Mappings
Map your CSV columns to expected field names:

```yaml
column_mappings:
  number: "number"
  priority: "priority"
  state: "incident_state"           # Maps to ServiceNow incident_state
  opened_at: "opened_at"
  resolved_at: "u_resolved"         # Maps to ServiceNow u_resolved
  reassignment_count: "reassignment_count"
  country: "location"               # Maps to location column
```

### KPI Configuration
```yaml
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

## 📊 Data Requirements

### Required Columns (after mapping)
- `number`: Incident/ticket identifier
- `opened_at`: Creation timestamp
- `priority`: Priority level
- `state`: Current status
- `reassignment_count`: Number of reassignments

### Optional Columns (after mapping)
- `resolved_at`: Resolution timestamp
- `country`: Geographic location

### Date Format Support
- **DD/MM/YYYY format**: Automatically handled with `dayfirst=True`
- **Various timestamp formats**: Flexible parsing with error handling
- **Missing dates**: Graceful handling with clear warnings

## 📈 Processing Modes

### Baseline Mode
Complete processing of all data to establish baseline KPIs:
```bash
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode baseline --input "your_data.csv"
```

### Incremental Mode
Efficient updates processing only changed records:
```bash
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode incremental --input "your_data.csv"
```

### Targeted Mode
Update specific KPIs with minimal processing:
```bash
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode targeted --kpi SM001 --input "your_data.csv"
```

## 🎯 Sample Results

Recent test with 2,438 ServiceNow incidents:

```
Records processed: 2,438
Configuration version: 1.0
Enabled KPIs: SM001, SM002, SM004, GEOGRAPHIC
Overall score: 68.8/100 (Needs Improvement)

KPI Summary:
  SM001: Above Target
  SM002: Needs Improvement
  SM004: Critical
  GEOGRAPHIC: Available
```

## 🌍 Geographic Analysis

When location data is available, the system provides:
- Country-wise incident distribution
- Priority breakdown by country
- Volume trends and KPI performance by region

## 📊 Output

The system generates:
- **JSON results files** with calculated KPIs and metadata
- **Performance metrics** and processing statistics
- **Validation reports** with clear error messages
- **Geographic analysis** (when location data available)

## 🚀 Performance Features

- **Vectorized Operations**: Efficient pandas operations for large datasets
- **Optimized Signature Generation**: Fast change detection algorithms
- **Geographic Analysis**: Efficient country-based grouping
- **Memory Efficient**: Streamlined data processing pipelines
- **Defensive Programming**: Graceful handling of missing columns

## 🔍 Troubleshooting

### Common Issues

1. **Column Mapping Errors**
   - Update `column_mappings` in `config/kpi_config.yaml` to match your CSV structure
   - Example: Map `resolved_at: "u_resolved"` for ServiceNow data

2. **Date Parsing Issues**
   - System automatically handles DD/MM/YYYY format with `dayfirst=True`
   - Check for consistent date formats in your data

3. **Missing Columns**
   - System provides clear warnings for missing optional columns
   - Required columns will cause processing to fail with clear error messages

4. **File Path Issues**
   - Use quotes around filenames with spaces: `"PYTHON IM Q1 (2025).csv"`
   - Ensure input files exist and are accessible

### Debug Mode
Add `--validate` flag for detailed validation output:
```bash
python scripts/complete_configurable_processor.py --config config/kpi_config.yaml --mode baseline --input "your_data.csv" --validate
```

### Exit Codes
- **0**: Success
- **1**: Warnings/minor issues
- **2**: Errors
- **130**: Interrupted (Ctrl+C)

## 🏆 Recent Improvements

✅ **Efficiency Optimizations**: Removed BOM characters, vectorized pandas operations  
✅ **Column Mapping Fixes**: Proper ServiceNow column support (`u_resolved`, `incident_state`, `location`)  
✅ **Date Parsing**: European DD/MM/YYYY format support with `dayfirst=True`  
✅ **Defensive Programming**: Graceful handling of missing columns with clear warnings  
✅ **Project Organization**: Consistent file structure in `scripts/` folder  
✅ **Minimalist Approach**: Removed 20+ non-essential files for cleaner codebase  

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
