"""
Centralized path configuration with environment variable support
"""
import os
from pathlib import Path
from typing import Optional


class PathConfig:
    """Centralized path configuration with environment variable support"""
    
    @staticmethod
    def get_config_path(filename: str = "kpi_config.yaml") -> str:
        """Get configuration file path with environment variable support"""
        config_dir = os.getenv('KPI_CONFIG_DIR', 'config')
        return str(Path(config_dir) / filename)
    
    @staticmethod
    def get_data_path(filename: str = "consolidated_data.csv") -> str:
        """Get data file path with environment variable support"""
        data_dir = os.getenv('KPI_DATA_DIR', 'data')
        return str(Path(data_dir) / filename)
    
    @staticmethod
    def get_output_path(filename: str) -> str:
        """Get output file path with environment variable support"""
        output_dir = os.getenv('KPI_OUTPUT_DIR', 'output')
        return str(Path(output_dir) / filename)
    
    @staticmethod
    def get_scripts_path(filename: str) -> str:
        """Get scripts file path with environment variable support"""
        scripts_dir = os.getenv('KPI_SCRIPTS_DIR', 'scripts')
        return str(Path(scripts_dir) / filename)
    
    @staticmethod
    def get_benchmark_config_path() -> str:
        """Get benchmark configuration path"""
        return PathConfig.get_config_path("benchmark_config.yaml")
    
    @staticmethod
    def get_benchmark_data_path() -> str:
        """Get benchmark data path"""
        return PathConfig.get_data_path("benchmark_sample.csv")
    
    @staticmethod
    def ensure_output_dir() -> Path:
        """Ensure output directory exists and return Path object"""
        output_dir = Path(os.getenv('KPI_OUTPUT_DIR', 'output'))
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    @staticmethod
    def get_validation_report_path(timestamp: Optional[str] = None) -> str:
        """Get validation report path with optional timestamp"""
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return PathConfig.get_output_path(f"validation_report_{timestamp}.json")


DEFAULT_CONFIG_FILE = PathConfig.get_config_path()
DEFAULT_DATA_FILE = PathConfig.get_data_path()
BENCHMARK_CONFIG_FILE = PathConfig.get_benchmark_config_path()
BENCHMARK_DATA_FILE = PathConfig.get_benchmark_data_path()
