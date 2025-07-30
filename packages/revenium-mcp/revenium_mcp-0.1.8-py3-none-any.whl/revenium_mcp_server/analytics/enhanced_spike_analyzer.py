"""Enhanced Spike Analyzer for temporal anomaly detection.

This module implements Enhanced Spike Analysis v2.0 as specified in the PRD.
Provides deterministic statistical analysis using z-score calculations for
detecting temporal anomalies in cost data across multiple dimensions.
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from loguru import logger

from .statistical_anomaly_detector import StatisticalAnomalyDetector, SENSITIVITY_THRESHOLDS


# API endpoint mappings as specified in PRD
TEMPORAL_ANALYSIS_ENDPOINTS = {
    "providers": "/profitstream/v2/api/sources/metrics/ai/total-cost-by-provider-over-time",
    "models": "/profitstream/v2/api/sources/metrics/ai/total-cost-by-model",
    "api_keys": "/profitstream/v2/api/sources/metrics/ai/cost-metrics-by-subscriber-credential", 
    "agents": "/profitstream/v2/api/sources/metrics/ai/cost-metrics-by-agents-over-time",
    "customers": "/profitstream/v2/api/sources/metrics/ai/cost-metric-by-organization",
    "tokens": "/profitstream/v2/api/sources/metrics/ai/tokens-per-minute-by-provider"
}


@dataclass
class TemporalAnomaly:
    """Temporal anomaly data structure exactly as specified in PRD."""
    entity_name: str           # "OpenAI", "gpt-4", "api-key-123"
    entity_type: str           # "provider", "model", "api_key", "agent"
    time_group: str            # "2024-01-15T14:00:00Z" 
    time_group_label: str      # "Saturday 2PM" or "Day 6"
    anomaly_value: float       # 2000.0
    normal_range_min: float    # 100.0
    normal_range_max: float    # 300.0
    z_score: float             # 2.8
    severity_score: float      # 125.6 (z_score * sqrt(dollar_impact))
    anomaly_type: str          # "entity_temporal" or "period_wide"
    context: str               # Human-readable explanation
    percentage_above_normal: float  # 566.7


class EnhancedSpikeAnalyzer:
    """Main orchestration class for temporal anomaly detection.
    
    Implements the complete Enhanced Spike Analysis v2.0 algorithm as specified
    in the PRD. Provides deterministic statistical analysis using z-score
    calculations for detecting temporal anomalies across multiple dimensions.
    """
    
    def __init__(self, client) -> None:
        """Initialize the enhanced spike analyzer.
        
        Args:
            client: Revenium API client for data fetching
        """
        self.client = client
        self.detector = StatisticalAnomalyDetector()
        self.logger = logger
        
        # Period validation mapping
        self.supported_periods = {
            "HOUR", "EIGHT_HOURS", "TWENTY_FOUR_HOURS", 
            "SEVEN_DAYS", "THIRTY_DAYS", "TWELVE_MONTHS"
        }
    
    async def analyze_temporal_anomalies(
        self,
        period: str,
        sensitivity: str = "normal",
        min_impact_threshold: float = 10.0,
        include_dimensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Complete algorithm for temporal anomaly detection.
        
        Args:
            period: Time period (HOUR, EIGHT_HOURS, etc.)
            sensitivity: Statistical sensitivity (conservative, normal, aggressive)
            min_impact_threshold: Minimum dollar impact to report
            include_dimensions: Dimensions to analyze (default: ["providers"])
            
        Returns:
            Complete temporal anomaly analysis results
        """
        # Phase 1: Validate inputs
        if period not in self.supported_periods:
            raise ValueError(f"Unsupported period: {period}")
        
        if sensitivity not in SENSITIVITY_THRESHOLDS:
            raise ValueError(f"Unsupported sensitivity: {sensitivity}")
        
        if include_dimensions is None:
            include_dimensions = ["providers"]  # Phase 1: providers only
        
        self.logger.info(f"Analyzing temporal anomalies: period={period}, sensitivity={sensitivity}")
        
        # Step 1: Collect time-series data from endpoints
        time_series_data = await self._collect_temporal_data(period, include_dimensions)
        
        # Step 2: Build entity-time matrix
        entity_time_matrix = self._build_entity_time_matrix(time_series_data)
        
        # Step 3: Detect entity-level temporal anomalies
        entity_anomalies = await self._detect_entity_anomalies(
            entity_time_matrix, sensitivity, min_impact_threshold, period
        )
        
        # Step 4: Sort by severity score and return formatted results
        entity_anomalies.sort(key=lambda x: x.severity_score, reverse=True)
        
        return self._format_temporal_results(entity_anomalies, period, sensitivity, include_dimensions)
    
    async def _collect_temporal_data(
        self,
        period: str,
        include_dimensions: List[str]
    ) -> Dict[str, Any]:
        """Collect time-series data from all specified endpoints.
        
        Args:
            period: Time period for data collection
            include_dimensions: Dimensions to collect data for
            
        Returns:
            Raw time-series data from API endpoints
        """
        collected_data = {}
        
        # Get team_id for API calls
        team_id = getattr(self.client, 'team_id', None)
        if not team_id:
            import os
            team_id = os.getenv('REVENIUM_TEAM_ID')
            if not team_id:
                raise Exception("Team ID not available from client or environment")
        
        # Collect data for each specified dimension
        for dimension in include_dimensions:
            if dimension not in TEMPORAL_ANALYSIS_ENDPOINTS:
                self.logger.warning(f"Unknown dimension: {dimension}")
                continue
            
            endpoint = TEMPORAL_ANALYSIS_ENDPOINTS[dimension]
            params = {"teamId": team_id, "period": period}
            
            try:
                self.logger.info(f"Collecting {dimension} data from {endpoint}")
                response = await self.client.get(endpoint, params=params)
                collected_data[dimension] = response
                self.logger.info(f"Successfully collected {dimension} data")
            except Exception as e:
                self.logger.error(f"Failed to collect {dimension} data: {e}")
                collected_data[dimension] = []
        
        return collected_data
    
    def _build_entity_time_matrix(self, time_series_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Build entity-time matrix from time-series data.
        
        Args:
            time_series_data: Raw time-series data from API
            
        Returns:
            Entity-time matrix where keys are entity names and values are time series
        """
        entity_time_matrix = {}
        # Track entity to dimension mapping for proper type identification
        self.entity_dimension_map = {}
        
        for dimension, data in time_series_data.items():
            if isinstance(data, list) and data:
                self._process_time_series_data(data, entity_time_matrix, dimension)
            elif isinstance(data, dict) and 'groups' in data:
                self._process_single_period_data(data, entity_time_matrix, dimension)
        
        self.logger.info(f"Built entity-time matrix with {len(entity_time_matrix)} entities")
        return entity_time_matrix
    
    def _process_time_series_data(self, data: List[Dict], entity_time_matrix: Dict[str, List[float]], dimension: str) -> None:
        """Process time-series format data with multiple time periods."""
        for time_entry in data:
            if not isinstance(time_entry, dict) or 'groups' not in time_entry:
                continue
            
            groups = time_entry.get('groups', [])
            for group in groups:
                if not isinstance(group, dict):
                    continue
                
                entity_name = group.get('groupName', 'Unknown')
                total_cost = self._calculate_group_cost(group.get('metrics', []))
                
                # Track entity to dimension mapping
                self.entity_dimension_map[entity_name] = dimension
                
                if entity_name not in entity_time_matrix:
                    entity_time_matrix[entity_name] = []
                
                entity_time_matrix[entity_name].append(total_cost)
    
    def _process_single_period_data(self, data: Dict, entity_time_matrix: Dict[str, List[float]], dimension: str) -> None:
        """Process single time period format data."""
        groups = data.get('groups', [])
        for group in groups:
            if not isinstance(group, dict):
                continue
            
            entity_name = group.get('groupName', 'Unknown')
            total_cost = self._calculate_group_cost(group.get('metrics', []))
            
            # Track entity to dimension mapping
            self.entity_dimension_map[entity_name] = dimension
            
            # For single period, create single-item time series
            entity_time_matrix[entity_name] = [total_cost]
    
    def _calculate_group_cost(self, metrics: List[Dict]) -> float:
        """Calculate total cost for a group from metrics."""
        total_cost = 0.0
        for metric in metrics:
            if isinstance(metric, dict):
                cost = float(metric.get('metricResult', 0))
                total_cost += cost
        return total_cost
    
    async def _detect_entity_anomalies(
        self,
        entity_time_matrix: Dict[str, List[float]],
        sensitivity: str,
        min_impact_threshold: float,
        period: str
    ) -> List[TemporalAnomaly]:
        """Detect entity-level temporal anomalies.
        
        Args:
            entity_time_matrix: Entity-time matrix data
            sensitivity: Statistical sensitivity level
            min_impact_threshold: Minimum dollar impact threshold
            
        Returns:
            List of detected temporal anomalies
        """
        entity_anomalies = []
        
        for entity_name, time_values in entity_time_matrix.items():
            if len(time_values) < 3:
                self.logger.debug(f"Insufficient data for {entity_name}: {len(time_values)}")
                continue
            
            # Use statistical detector to find anomalies
            anomaly_results = self.detector.detect_entity_temporal_anomalies(
                entity_name, time_values, sensitivity, min_impact_threshold
            )
            
            # Convert to TemporalAnomaly objects
            for time_index, anomaly_result in anomaly_results:
                temporal_anomaly = TemporalAnomaly(
                    entity_name=entity_name,
                    entity_type=self._get_entity_type(entity_name),
                    time_group=self._get_time_group_timestamp(time_index),
                    time_group_label=self._get_time_group_label(time_index, period),
                    anomaly_value=anomaly_result.value,
                    normal_range_min=anomaly_result.normal_range_min,
                    normal_range_max=anomaly_result.normal_range_max,
                    z_score=anomaly_result.z_score,
                    severity_score=anomaly_result.severity_score,
                    anomaly_type="entity_temporal",
                    context=self._generate_context(entity_name, time_index, anomaly_result, period),
                    percentage_above_normal=anomaly_result.percentage_above_normal
                )
                entity_anomalies.append(temporal_anomaly)
        
        self.logger.info(f"Detected {len(entity_anomalies)} entity temporal anomalies")
        return entity_anomalies
    
    def _format_temporal_results(
        self,
        anomalies: List[TemporalAnomaly],
        period: str,
        sensitivity: str,
        include_dimensions: List[str]
    ) -> Dict[str, Any]:
        """Format temporal anomaly results according to PRD specification.
        
        Args:
            anomalies: List of detected anomalies
            period: Analysis period
            sensitivity: Sensitivity level used
            include_dimensions: Dimensions that were analyzed
            
        Returns:
            Formatted results matching PRD JSON example
        """
        # Calculate entities analyzed by dimension
        entities_analyzed = {}
        for dimension in include_dimensions:
            # Count entities from this dimension based on entity_dimension_map
            dimension_entities = {name for name, dim in self.entity_dimension_map.items() if dim == dimension}
            entities_analyzed[dimension] = len(dimension_entities)
        
        # Convert anomalies to dict format
        temporal_anomalies = []
        for anomaly in anomalies:
            temporal_anomalies.append({
                "entity_name": anomaly.entity_name,
                "entity_type": anomaly.entity_type,
                "time_group": anomaly.time_group,
                "time_group_label": anomaly.time_group_label,
                "anomaly_value": round(anomaly.anomaly_value, 2),
                "normal_range_min": round(anomaly.normal_range_min, 2),
                "normal_range_max": round(anomaly.normal_range_max, 2),
                "z_score": round(anomaly.z_score, 1),
                "severity_score": round(anomaly.severity_score, 1),
                "anomaly_type": anomaly.anomaly_type,
                "context": anomaly.context,
                "percentage_above_normal": round(anomaly.percentage_above_normal, 1)
            })
        
        # Phase 3: Generate time period summary and entity summary
        time_period_summary = self._generate_time_period_summary(anomalies, period)
        entity_summary = self._generate_entity_summary(anomalies)
        
        # Generate intelligent recommendations based on detected patterns
        recommendations = self._generate_recommendations(anomalies, include_dimensions)
        
        # Complete result structure matching PRD Phase 3
        result = {
            "period_analyzed": period,
            "sensitivity_used": sensitivity,
            "time_groups_analyzed": self._get_time_groups_count(period),
            "entities_analyzed": entities_analyzed,
            "total_anomalies_detected": len(temporal_anomalies),
            "temporal_anomalies": temporal_anomalies,
            "time_period_summary": time_period_summary,
            "entity_summary": entity_summary,
            "recommendations": recommendations
        }
        
        return result
    
    def _generate_recommendations(self, anomalies: List[TemporalAnomaly], include_dimensions: List[str]) -> List[str]:
        """Generate intelligent recommendations based on detected anomaly patterns.
        
        Args:
            anomalies: List of detected anomalies
            include_dimensions: Dimensions that were analyzed
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Check for ANONYMOUS API key anomalies
        if "api_keys" in include_dimensions:
            anonymous_anomalies = [
                a for a in anomalies 
                if a.entity_type == "api_key" and a.entity_name.upper() == "ANONYMOUS"
            ]
            
            if anonymous_anomalies:
                # ANONYMOUS API key found in anomalies - critical attribution issue
                recommendations.append(
                    "Add subscriber credential tagging to usage metadata when submitting transactions to enable attribution of API Key spending to specific users or projects."
                )
        
        # Future: Add more pattern-based recommendations here
        # - Weekend spike patterns
        # - Multi-provider spikes (potential credential compromise)
        # - Model-specific anomalies (cost optimization opportunities)
        
        return recommendations
    
    def _generate_time_period_summary(self, anomalies: List[TemporalAnomaly], period: str) -> Dict[str, Any]:
        """Generate time period summary with mathematical aggregations only.
        
        Args:
            anomalies: List of detected anomalies
            period: Analysis period
            
        Returns:
            Time period summary with absolute determinations only
        """
        time_period_summary = {}
        
        # Group anomalies by time period
        period_groups = {}
        for anomaly in anomalies:
            time_label = anomaly.time_group_label
            if time_label not in period_groups:
                period_groups[time_label] = []
            period_groups[time_label].append(anomaly)
        
        # Calculate mathematical aggregations for each time period
        for time_label, period_anomalies in period_groups.items():
            total_anomalies = len(period_anomalies)
            total_anomalous_cost = sum(a.anomaly_value for a in period_anomalies)
            
            # Calculate normal cost for period (mathematical baseline)
            normal_costs = []
            for anomaly in period_anomalies:
                # Use midpoint of normal range as baseline estimate
                normal_baseline = (anomaly.normal_range_min + anomaly.normal_range_max) / 2
                normal_costs.append(normal_baseline)
            
            normal_cost_for_period = sum(normal_costs)
            
            # Calculate cost multiplier (absolute determination)
            cost_multiplier = (total_anomalous_cost / normal_cost_for_period) if normal_cost_for_period > 0 else 0
            
            # Generate factual explanation (no business impact assessment)
            if total_anomalies == 1:
                entity_desc = f"{period_anomalies[0].entity_name} anomaly"
            else:
                entity_desc = f"{total_anomalies} entity anomalies"
            
            time_period_summary[time_label] = {
                "total_anomalies": total_anomalies,
                "total_anomalous_cost": round(total_anomalous_cost, 2),
                "normal_cost_for_period": round(normal_cost_for_period, 2),
                "cost_multiplier": round(cost_multiplier, 1),
                "anomaly_explanation": f"{time_label} had {entity_desc} with {cost_multiplier:.1f}x normal cost levels"
            }
        
        return time_period_summary
    
    def _generate_entity_summary(self, anomalies: List[TemporalAnomaly]) -> Dict[str, Any]:
        """Generate entity summary with absolute pattern detection.
        
        Args:
            anomalies: List of detected anomalies
            
        Returns:
            Entity summary with mathematical determinations only
        """
        entity_summary = {}
        
        # Group anomalies by entity
        entity_groups = {}
        for anomaly in anomalies:
            entity_name = anomaly.entity_name
            if entity_name not in entity_groups:
                entity_groups[entity_name] = []
            entity_groups[entity_name].append(anomaly)
        
        # Calculate mathematical summaries for each entity
        for entity_name, entity_anomalies in entity_groups.items():
            anomalous_time_periods = [a.time_group_label for a in entity_anomalies]
            total_anomalous_cost = sum(a.anomaly_value for a in entity_anomalies)
            
            # Calculate normal daily average (mathematical baseline)
            normal_values = []
            for anomaly in entity_anomalies:
                # Use midpoint of normal range as baseline estimate
                normal_baseline = (anomaly.normal_range_min + anomaly.normal_range_max) / 2
                normal_values.append(normal_baseline)
            
            normal_daily_average = statistics.mean(normal_values) if normal_values else 0
            
            # Detect absolute patterns (mathematical determination only)
            anomaly_pattern = self._detect_absolute_pattern(anomalous_time_periods)
            
            entity_summary[entity_name] = {
                "anomalous_time_periods": anomalous_time_periods,
                "total_anomalous_cost": round(total_anomalous_cost, 2),
                "normal_daily_average": round(normal_daily_average, 2),
                "anomaly_pattern": anomaly_pattern
            }
        
        return entity_summary
    
    def _detect_absolute_pattern(self, time_periods: List[str]) -> str:
        """Detect absolute patterns in time periods using mathematical determination.
        
        Args:
            time_periods: List of time period labels where anomalies occurred
            
        Returns:
            Absolute pattern description (entity-specific, no inference)
        """
        if len(time_periods) < 2:
            return "Single period anomaly (this entity only)"
        
        # Check for weekend spike pattern (absolute determination)
        weekend_days = {"Saturday", "Sunday"}
        weekend_anomalies = [tp for tp in time_periods if any(day in tp for day in weekend_days)]
        
        # Absolute weekend spike: ALL anomalies on weekends AND ≥2 anomalies
        if len(weekend_anomalies) == len(time_periods) and len(time_periods) >= 2:
            return f"Weekend spike pattern for this entity ({len(time_periods)} weekend periods)"
        
        # Check for consecutive day pattern
        if len(time_periods) >= 2:
            # Convert day names to indices for mathematical comparison
            day_mapping = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, 
                          "Thursday": 4, "Friday": 5, "Saturday": 6}
            
            day_indices = []
            for tp in time_periods:
                for day, index in day_mapping.items():
                    if day in tp:
                        day_indices.append(index)
                        break
            
            if len(day_indices) >= 2:
                day_indices.sort()
                # Check if consecutive (mathematical determination)
                is_consecutive = all(day_indices[i] == day_indices[i-1] + 1 for i in range(1, len(day_indices)))
                if is_consecutive:
                    return f"Consecutive day pattern for this entity ({len(time_periods)} consecutive periods)"
        
        # Default: Multiple anomaly pattern
        return f"Multiple period anomalies for this entity ({len(time_periods)} periods)"
    
    def _get_entity_type(self, entity_name: str) -> str:
        """Determine entity type from entity name based on dimension mapping."""
        # Use dimension mapping to determine entity type
        dimension = self.entity_dimension_map.get(entity_name, 'providers')
        
        # Map dimension to entity type
        dimension_to_type = {
            'providers': 'provider',
            'models': 'model',
            'agents': 'agent', 
            'api_keys': 'api_key',
            'customers': 'customer'
        }
        
        return dimension_to_type.get(dimension, 'provider')
    
    def _get_time_group_timestamp(self, time_index: int) -> str:
        """Generate timestamp for time group."""
        # Simplified timestamp generation for Phase 1
        base_time = datetime.utcnow()
        delta = timedelta(days=time_index)
        return (base_time - delta).isoformat() + "Z"
    
    def _get_time_group_label(self, time_index: int, period: str) -> str:
        """Generate human-readable label for time group based on period."""
        if period == "HOUR":
            # For hourly analysis, show specific time ranges
            start_hour = time_index
            end_hour = (time_index + 1) % 24
            return f"hour {start_hour:02d}:00-{end_hour:02d}:00"
        elif period == "EIGHT_HOURS":
            # For 8-hour analysis, show time ranges
            start_hour = time_index * 8
            end_hour = (start_hour + 8) % 24
            return f"period {start_hour:02d}:00-{end_hour:02d}:00"
        elif period == "TWENTY_FOUR_HOURS":
            # For daily analysis, show relative days
            if time_index == 0:
                return "today"
            elif time_index == 1:
                return "yesterday"
            else:
                return f"{time_index} days ago"
        elif period == "SEVEN_DAYS":
            # For weekly analysis, show day names
            days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            return days[time_index % 7]
        elif period == "THIRTY_DAYS":
            # For monthly analysis, show relative days or weeks
            if time_index < 7:
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                return f"{days[time_index % 7]} (week 1)"
            elif time_index < 14:
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                return f"{days[time_index % 7]} (week 2)"
            else:
                return f"day {time_index + 1}"
        elif period == "TWELVE_MONTHS":
            # For yearly analysis, show month names
            months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            return months[time_index % 12]
        else:
            return f"period {time_index + 1}"
    
    def _generate_context(self, entity_name: str, time_index: int, anomaly_result, period: str) -> str:
        """Generate human-readable context for anomaly."""
        time_label = self._get_time_group_label(time_index, period)
        
        # Choose appropriate preposition based on time label
        if time_label in ["today", "yesterday"]:
            # No preposition sounds more natural: "costs yesterday" vs "costs on yesterday"
            preposition = ""
        elif "hour" in time_label or "period" in time_label or "day" in time_label and "ago" in time_label:
            preposition = "during "
        elif any(day in time_label for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]):
            preposition = "on "
        elif any(month in time_label for month in ["January", "February", "March", "April", "May", "June"]):
            preposition = "in "
        else:
            preposition = "during "
        
        return (f"{entity_name} costs {preposition}{time_label} (${anomaly_result.value:.2f}) "
                f"were {anomaly_result.z_score:.1f} standard deviations above "
                f"the average value in the evaluated period")
    
    def _get_time_groups_count(self, period: str) -> int:
        """Get number of time groups for the period."""
        period_mapping = {
            "HOUR": 1,
            "EIGHT_HOURS": 8,
            "TWENTY_FOUR_HOURS": 24,
            "SEVEN_DAYS": 7,
            "THIRTY_DAYS": 30,
            "TWELVE_MONTHS": 12
        }
        return period_mapping.get(period, 1)