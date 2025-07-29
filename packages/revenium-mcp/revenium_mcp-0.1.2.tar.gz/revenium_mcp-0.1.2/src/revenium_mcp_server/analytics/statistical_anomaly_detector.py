"""Statistical anomaly detector for temporal analysis.

This module provides deterministic statistical analysis using z-score calculations
for detecting temporal anomalies in cost data. Used by Enhanced Spike Analysis v2.0.
"""

import math
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


# Sensitivity thresholds as specified in PRD
SENSITIVITY_THRESHOLDS = {
    "conservative": 3.0,  # 3 standard deviations (99.7% confidence)
    "normal": 2.0,        # 2 standard deviations (95% confidence)  
    "aggressive": 1.5     # 1.5 standard deviations (86.6% confidence)
}


@dataclass
class AnomalyResult:
    """Statistical anomaly detection result."""
    value: float
    z_score: float
    severity_score: float
    is_anomaly: bool
    normal_range_min: float
    normal_range_max: float
    percentage_above_normal: float


class StatisticalAnomalyDetector:
    """Core statistical analysis engine for temporal anomaly detection.
    
    Implements deterministic z-score based anomaly detection as specified
    in Enhanced Spike Analysis v2.0 PRD. Uses exact formulas:
    - z_score = abs((value - mean) / std_dev)
    - severity_score = z_score * sqrt(dollar_impact)
    """
    
    def __init__(self) -> None:
        """Initialize the statistical anomaly detector."""
        self.logger = logger
    
    def detect_entity_temporal_anomalies(
        self,
        entity_name: str,
        time_values: List[float],
        sensitivity: str = "normal",
        min_impact_threshold: float = 10.0
    ) -> List[Tuple[int, AnomalyResult]]:
        """Detect temporal anomalies for a specific entity across time periods.
        
        Args:
            entity_name: Name of the entity being analyzed
            time_values: List of cost values across time periods
            sensitivity: Sensitivity level (conservative, normal, aggressive)
            min_impact_threshold: Minimum dollar impact to consider
            
        Returns:
            List of (time_index, AnomalyResult) tuples for detected anomalies
        """
        if len(time_values) < 3:
            self.logger.debug(f"Insufficient data points for {entity_name}: {len(time_values)}")
            return []
        
        # Calculate statistical baseline
        mean_value = statistics.mean(time_values)
        std_value = statistics.stdev(time_values) if len(time_values) > 1 else 0
        
        if std_value == 0:
            self.logger.debug(f"No variation in data for {entity_name}")
            return []
        
        threshold = SENSITIVITY_THRESHOLDS.get(sensitivity, 2.0)
        anomalies = []
        
        for i, value in enumerate(time_values):
            if value < min_impact_threshold:
                continue
                
            anomaly_result = self._analyze_value(
                value, mean_value, std_value, threshold
            )
            
            if anomaly_result.is_anomaly:
                anomalies.append((i, anomaly_result))
        
        self.logger.info(f"Detected {len(anomalies)} anomalies for {entity_name}")
        return anomalies
    
    def detect_time_period_anomalies(
        self,
        time_group: str,
        entity_values: List[float],
        sensitivity: str = "normal",
        min_impact_threshold: float = 10.0
    ) -> List[Tuple[int, AnomalyResult]]:
        """Detect anomalies within a specific time period across entities.
        
        Args:
            time_group: Time period identifier
            entity_values: List of cost values for different entities
            sensitivity: Sensitivity level (conservative, normal, aggressive)
            min_impact_threshold: Minimum dollar impact to consider
            
        Returns:
            List of (entity_index, AnomalyResult) tuples for detected anomalies
        """
        if len(entity_values) < 3:
            self.logger.debug(f"Insufficient entities for {time_group}: {len(entity_values)}")
            return []
        
        # Calculate statistical baseline across entities
        mean_value = statistics.mean(entity_values)
        std_value = statistics.stdev(entity_values) if len(entity_values) > 1 else 0
        
        if std_value == 0:
            self.logger.debug(f"No variation across entities for {time_group}")
            return []
        
        threshold = SENSITIVITY_THRESHOLDS.get(sensitivity, 2.0)
        anomalies = []
        
        for i, value in enumerate(entity_values):
            if value < min_impact_threshold:
                continue
                
            anomaly_result = self._analyze_value(
                value, mean_value, std_value, threshold
            )
            
            if anomaly_result.is_anomaly:
                anomalies.append((i, anomaly_result))
        
        self.logger.info(f"Detected {len(anomalies)} entity anomalies in {time_group}")
        return anomalies
    
    def calculate_z_score(self, value: float, mean: float, std_dev: float) -> float:
        """Calculate z-score using exact formula from PRD.
        
        Args:
            value: Observed value
            mean: Mean of the dataset
            std_dev: Standard deviation of the dataset
            
        Returns:
            Z-score as absolute value
        """
        if std_dev == 0:
            return 0.0
        return abs((value - mean) / std_dev)
    
    def calculate_severity_score(self, z_score: float, dollar_impact: float) -> float:
        """Calculate severity score using exact formula from PRD.
        
        Args:
            z_score: Statistical z-score
            dollar_impact: Dollar amount of the impact
            
        Returns:
            Severity score (z_score * sqrt(dollar_impact))
        """
        return z_score * math.sqrt(dollar_impact)
    
    def _analyze_value(
        self,
        value: float,
        mean_value: float,
        std_value: float,
        threshold: float
    ) -> AnomalyResult:
        """Analyze a single value for anomaly detection.
        
        Args:
            value: Value to analyze
            mean_value: Mean of the dataset
            std_value: Standard deviation of the dataset
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            AnomalyResult with complete analysis
        """
        z_score = self.calculate_z_score(value, mean_value, std_value)
        severity_score = self.calculate_severity_score(z_score, value)
        is_anomaly = z_score > threshold
        
        # Calculate normal range (mean ± 1 std_dev for reference)
        # Ensure minimum is never negative for cost data
        normal_range_min = max(0.0, mean_value - std_value)
        normal_range_max = mean_value + std_value
        
        # Calculate percentage above normal
        if mean_value > 0:
            percentage_above_normal = ((value - mean_value) / mean_value) * 100
        else:
            percentage_above_normal = 0.0
        
        return AnomalyResult(
            value=value,
            z_score=z_score,
            severity_score=severity_score,
            is_anomaly=is_anomaly,
            normal_range_min=normal_range_min,
            normal_range_max=normal_range_max,
            percentage_above_normal=percentage_above_normal
        )