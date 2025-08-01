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
git clone https://github.com/yourusername/kpi-processor-test.git
cd kpi-processor-test
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
python scripts/config_validator_fixed.py --config config/complete_kpi_config.yaml
```

2. **Run Baseline Processing**:
```bash
python scripts/complete_configurable_processor_fixed.py --config config/complete_kpi_config.yaml --mode baseline --input data/raw/your_data.csv
```

3. **Run Incremental Updates**:
```bash
python scripts/complete_configurable_processor_fixed.py --config config/complete_kpi_config.yaml --mode incremental --input data/raw/updated_data.csv
```

4. **Test Complete System**:
```bash
python test_system.py
```

## 📁 Project Structure

```
kpi_processor_test/
├── config/
│   └── complete_kpi_config.yaml      # Main configuration file
├── scripts/
│   ├── complete_configurable_processor_fixed.py  # Main processor
│   └── config_validator_fixed.py     # Configuration validator
├── data/
│   └── raw/                          # Input data files
├── output/                           # Generated results
├── cache/                            # Processing cache
├── test_system.py                    # System test script
└── README.md
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
python scripts/complete_configurable_processor_fixed.py --config config.yaml --mode baseline --input data.csv
```

### Incremental Mode
Efficient updates processing only changed records:
```bash
python scripts/complete_configurable_processor_fixed.py --config config.yaml --mode incremental --input data.csv
```

### Targeted Mode
Update specific KPIs with minimal processing:
```bash
python scripts/complete_configurable_processor_fixed.py --config config.yaml --mode targeted --kpi SM001 --input data.csv
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
