"""
Utility functions and classes for SlowCLI application.
"""

import time
import logging
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import threading
import psutil

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data class."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceTracker:
    """
    Track performance metrics for various operations.
    """

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.lock = threading.Lock()

    def start(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start timing a performance metric.

        Args:
            name: Name of the metric
            metadata: Additional metadata for the metric
        """
        with self.lock:
            self.metrics[name] = PerformanceMetric(
                name=name,
                start_time=time.time(),
                metadata=metadata or {}
            )
            logger.debug(f"Started performance tracking: {name}")

    def end(self, name: str) -> Optional[float]:
        """
        End timing a performance metric.

        Args:
            name: Name of the metric

        Returns:
            Duration in seconds, or None if metric not found
        """
        with self.lock:
            if name not in self.metrics:
                logger.warning(f"Performance metric not found: {name}")
                return None

            metric = self.metrics[name]
            metric.end_time = time.time()
            metric.duration = metric.end_time - metric.start_time

            logger.debug(f"Ended performance tracking: {name} ({metric.duration:.3f}s)")
            return metric.duration

    def get_metric(self, name: str) -> Optional[PerformanceMetric]:
        """Get a specific performance metric."""
        return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get all performance metrics."""
        return self.metrics.copy()

    def print_summary(self) -> None:
        """Print a summary of all performance metrics."""
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)

        for name, metric in self.metrics.items():
            if metric.duration is not None:
                print(f"{name:30} {metric.duration:8.3f}s")
            else:
                print(f"{name:30} {'running':>8}")

        print("="*50)

    def export_metrics(self, format_type: str = 'json') -> str:
        """
        Export metrics in the specified format.

        Args:
            format_type: Output format ('json', 'yaml', 'csv')

        Returns:
            Formatted metrics string
        """
        export_data = {}

        for name, metric in self.metrics.items():
            export_data[name] = {
                'duration': metric.duration,
                'start_time': metric.start_time,
                'end_time': metric.end_time,
                'metadata': metric.metadata
            }

        if format_type == 'json':
            return json.dumps(export_data, indent=2)
        elif format_type == 'yaml':
            return yaml.dump(export_data, default_flow_style=False)
        else:
            # CSV format
            lines = ['metric_name,duration,start_time,end_time']
            for name, data in export_data.items():
                lines.append(f"{name},{data['duration']},{data['start_time']},{data['end_time']}")
            return '\n'.join(lines)

class ConfigManager:
    """
    Manage configuration for the SlowCLI application.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.default_config = {
            'output': {
                'format': 'human',
                'verbose': False,
                'quiet': False
            },
            'performance': {
                'track_metrics': True,
                'log_performance': False
            },
            'data': {
                'chunk_size': 10000,
                'default_format': 'csv',
                'compression': 'none'
            },
            'network': {
                'timeout': 30,
                'retries': 3,
                'threads': 10
            },
            'analysis': {
                'test_size': 0.2,
                'cross_validation_folds': 5,
                'random_state': 42
            }
        }

        # Load default config
        self.config = self.default_config.copy()

        # Load from file if provided
        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = Path(config_file)

            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_file}")
                return False

            with open(config_path, 'r') as f:
                if config_path.suffix.lower() == '.json':
                    file_config = json.load(f)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    file_config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.toml':
                    file_config = toml.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {config_path.suffix}")
                    return False

            # Merge with existing config
            self._merge_config(file_config)
            logger.info(f"Configuration loaded from: {config_file}")
            return True

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge new configuration with existing config.

        Args:
            new_config: New configuration to merge
        """
        def merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> None:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value

        merge_dicts(self.config, new_config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'output.format')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'output.format')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save_config(self, config_file: Optional[str] = None) -> bool:
        """
        Save current configuration to file.

        Args:
            config_file: Path to save configuration (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                logger.error("No configuration file path specified")
                return False

            config_path = Path(save_path)

            with open(config_path, 'w') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(self.config, f, default_flow_style=False)
                elif config_path.suffix.lower() == '.toml':
                    toml.dump(self.config, f)
                else:
                    logger.error(f"Unsupported configuration file format: {config_path.suffix}")
                    return False

            logger.info(f"Configuration saved to: {save_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

class DataProcessor:
    """
    Utility class for data processing operations.
    """

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def simulate_heavy_processing(self, data_size: int) -> float:
        """
        Simulate heavy data processing.

        Args:
            data_size: Size of data to process

        Returns:
            Processing time in seconds
        """
        # Simulate processing time based on data size
        processing_time = data_size / 10000  # 1 second per 10k items
        time.sleep(processing_time)
        return processing_time

    def compress_data(self, data: bytes, method: str) -> bytes:
        """
        Compress data using specified method.

        Args:
            data: Data to compress
            method: Compression method ('gzip', 'bzip2', 'lzma')

        Returns:
            Compressed data
        """
        if method == 'gzip':
            return gzip.compress(data)
        elif method == 'bzip2':
            return bz2.compress(data)
        elif method == 'lzma':
            return lzma.compress(data)
        else:
            return data

    def decompress_data(self, data: bytes, method: str) -> bytes:
        """
        Decompress data using specified method.

        Args:
            data: Data to decompress
            method: Compression method ('gzip', 'bzip2', 'lzma')

        Returns:
            Decompressed data
        """
        if method == 'gzip':
            return gzip.decompress(data)
        elif method == 'bzip2':
            return bz2.decompress(data)
        elif method == 'lzma':
            return lzma.decompress(data)
        else:
            return data

class NetworkScanner:
    """
    Utility class for network scanning operations.
    """

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def simulate_port_scan(self, target: str, ports: List[int], timeout: int) -> Dict[str, Any]:
        """
        Simulate port scanning.

        Args:
            target: Target IP address
            ports: List of ports to scan
            timeout: Connection timeout

        Returns:
            Scan results
        """
        # Simulate scanning time
        scan_time = len(ports) * 0.1  # 0.1 seconds per port
        time.sleep(scan_time)

        # Mock results
        open_ports = [port for port in ports if port % 3 == 0]  # Mock logic

        return {
            'target': target,
            'ports_scanned': ports,
            'open_ports': open_ports,
            'scan_time': scan_time
        }

    def simulate_service_detection(self, target: str, ports: List[int]) -> Dict[str, str]:
        """
        Simulate service detection.

        Args:
            target: Target IP address
            ports: List of open ports

        Returns:
            Service mapping
        """
        # Simulate service detection time
        time.sleep(len(ports) * 0.2)

        # Mock service mapping
        services = {
            80: 'HTTP',
            443: 'HTTPS',
            22: 'SSH',
            21: 'FTP',
            25: 'SMTP',
            53: 'DNS',
            8080: 'HTTP-Proxy'
        }

        return {str(port): services.get(port, 'Unknown') for port in ports}

class SystemMonitor:
    """
    Utility class for system monitoring operations.
    """

    def __init__(self):
        pass

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get current system information.

        Returns:
            System information dictionary
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'platform': {
                    'system': psutil.sys.platform,
                    'release': psutil.sys.getwindowsversion().release if hasattr(psutil.sys, 'getwindowsversion') else 'Unknown',
                    'machine': psutil.sys.machine
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}

    def monitor_resources(self, duration: int, interval: float, metrics: List[str]) -> List[Dict[str, Any]]:
        """
        Monitor system resources over time.

        Args:
            duration: Monitoring duration in seconds
            interval: Update interval in seconds
            metrics: List of metrics to monitor

        Returns:
            List of monitoring snapshots
        """
        snapshots = []
        start_time = time.time()

        while time.time() - start_time < duration:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'elapsed': time.time() - start_time
            }

            if 'cpu' in metrics or 'all' in metrics:
                snapshot['cpu_percent'] = psutil.cpu_percent(interval=0.1)

            if 'memory' in metrics or 'all' in metrics:
                memory = psutil.virtual_memory()
                snapshot['memory_percent'] = memory.percent

            if 'disk' in metrics or 'all' in metrics:
                disk = psutil.disk_usage('/')
                snapshot['disk_percent'] = (disk.used / disk.total) * 100

            snapshots.append(snapshot)
            time.sleep(interval)

        return snapshots
