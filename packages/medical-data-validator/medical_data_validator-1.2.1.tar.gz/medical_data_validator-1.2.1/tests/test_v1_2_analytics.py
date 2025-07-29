"""
Test cases for Medical Data Validator v1.2 Advanced Analytics Features
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from medical_data_validator.analytics import (
    AdvancedAnalytics, DataQualityMetric, TrendAnalysis, AnomalyDetection
)

class TestAdvancedAnalytics:
    """Test cases for the AdvancedAnalytics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analytics = AdvancedAnalytics()
        
        # Create test data with various data types and patterns
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'age': [25, 30, 35, 40, 45],
            'temperature': [98.6, 98.8, 99.0, 98.4, 98.9],
            'blood_pressure': [120, 125, 130, 135, 140],
            'visit_date': pd.date_range('2024-01-01', periods=5, freq='D'),
            'status': ['active', 'active', 'inactive', 'active', 'active'],
            'score': [85.5, 92.3, 78.9, 88.1, 95.7]
        })
        
        # Create data with anomalies
        self.anomaly_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'value': [10, 12, 15, 11, 13, 100, 14, 16, 12, 15],  # 100 is outlier
            'category': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
            'date': pd.date_range('2024-01-01', periods=10, freq='D'),
            'mixed_type': [1, 'text', 3.14, True, None, 6, 'more text', 8, 9, 10]
        })
        
        # Create time series data for trend analysis
        self.time_series_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'value': np.random.normal(100, 10, 30),
            'category': ['A'] * 15 + ['B'] * 15
        })
    
    def test_data_quality_metrics_calculation(self):
        """Test data quality metrics calculation."""
        metrics = self.analytics.calculate_data_quality_metrics(self.test_data)
        
        # Check that all expected metrics are present
        expected_metrics = ['completeness', 'consistency', 'accuracy', 'timeliness']
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], DataQualityMetric)
        
        # Check metric structure
        for metric_name, metric in metrics.items():
            assert hasattr(metric, 'name')
            assert hasattr(metric, 'value')
            assert hasattr(metric, 'unit')
            assert hasattr(metric, 'description')
            assert hasattr(metric, 'severity')
            
            # Check value ranges
            assert 0 <= metric.value <= 1
            assert metric.unit == "percentage"
            assert metric.severity in ['excellent', 'good', 'fair', 'poor', 'critical']
    
    def test_completeness_calculation(self):
        """Test completeness metric calculation."""
        # Test with complete data
        complete_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        metrics = self.analytics.calculate_data_quality_metrics(complete_data)
        assert metrics['completeness'].value == 1.0
        assert metrics['completeness'].severity == 'excellent'
        
        # Test with missing data
        incomplete_data = pd.DataFrame({
            'col1': [1, 2, None],
            'col2': ['a', None, 'c']
        })
        metrics = self.analytics.calculate_data_quality_metrics(incomplete_data)
        assert metrics['completeness'].value < 1.0
        assert metrics['completeness'].value > 0.0
    
    def test_consistency_calculation(self):
        """Test consistency metric calculation."""
        # Test with consistent data types
        consistent_data = pd.DataFrame({
            'numeric': [1, 2, 3],
            'text': ['a', 'b', 'c']
        })
        metrics = self.analytics.calculate_data_quality_metrics(consistent_data)
        assert metrics['consistency'].value == 1.0
        
        # Test with mixed data types
        mixed_data = pd.DataFrame({
            'mixed': [1, 'text', 3.14, True]
        })
        metrics = self.analytics.calculate_data_quality_metrics(mixed_data)
        assert metrics['consistency'].value < 1.0
    
    def test_accuracy_calculation(self):
        """Test accuracy metric calculation."""
        # Test with normal data (no outliers)
        normal_data = pd.DataFrame({
            'values': [10, 12, 15, 11, 13, 14, 16, 12, 15, 14]
        })
        metrics = self.analytics.calculate_data_quality_metrics(normal_data)
        assert metrics['accuracy'].value > 0.8
        
        # Test with outliers
        outlier_data = pd.DataFrame({
            'values': [10, 12, 15, 11, 13, 100, 14, 16, 12, 15]  # 100 is outlier
        })
        metrics = self.analytics.calculate_data_quality_metrics(outlier_data)
        assert metrics['accuracy'].value < 1.0
    
    def test_timeliness_calculation(self):
        """Test timeliness metric calculation."""
        # Test with recent dates
        recent_data = pd.DataFrame({
            'date': pd.date_range(datetime.now() - timedelta(days=30), periods=5, freq='D')
        })
        metrics = self.analytics.calculate_data_quality_metrics(recent_data)
        assert metrics['timeliness'].value > 0.9
        
        # Test with old dates
        old_data = pd.DataFrame({
            'date': pd.date_range(datetime.now() - timedelta(days=400), periods=5, freq='D')
        })
        metrics = self.analytics.calculate_data_quality_metrics(old_data)
        assert metrics['timeliness'].value < 0.5
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality."""
        anomalies = self.analytics.detect_anomalies(self.anomaly_data)
        
        # Should detect outliers
        outlier_anomalies = [a for a in anomalies if a.anomaly_type == 'outlier']
        assert len(outlier_anomalies) > 0
        
        # Should detect data type mismatches
        type_anomalies = [a for a in anomalies if a.anomaly_type == 'data_type_mismatch']
        assert len(type_anomalies) > 0
        
        # Check anomaly structure
        for anomaly in anomalies:
            assert hasattr(anomaly, 'column')
            assert hasattr(anomaly, 'anomaly_type')
            assert hasattr(anomaly, 'severity')
            assert hasattr(anomaly, 'description')
            assert hasattr(anomaly, 'affected_rows')
            assert hasattr(anomaly, 'recommendation')
            
            assert anomaly.anomaly_type in ['outlier', 'missing_pattern', 'data_type_mismatch', 'format_inconsistency']
            assert anomaly.severity in ['low', 'medium', 'high', 'critical']
            assert isinstance(anomaly.affected_rows, list)
    
    def test_outlier_detection(self):
        """Test specific outlier detection."""
        # Create data with clear outliers
        outlier_data = pd.DataFrame({
            'normal': [10, 12, 15, 11, 13, 14, 16, 12, 15, 14],
            'with_outliers': [10, 12, 15, 11, 13, 100, 14, 16, 12, 15]  # 100 is outlier
        })
        
        anomalies = self.analytics.detect_anomalies(outlier_data)
        
        # Should detect outlier in 'with_outliers' column
        outlier_anomalies = [a for a in anomalies if a.anomaly_type == 'outlier' and a.column == 'with_outliers']
        assert len(outlier_anomalies) > 0
        
        # Should not detect outliers in 'normal' column
        normal_anomalies = [a for a in anomalies if a.anomaly_type == 'outlier' and a.column == 'normal']
        assert len(normal_anomalies) == 0
    
    def test_missing_pattern_detection(self):
        """Test missing pattern detection."""
        # Create data with missing patterns
        missing_data = pd.DataFrame({
            'normal': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'missing_pattern': [1, 2, None, None, None, 6, 7, None, None, None]  # Consecutive missing
        })
        
        anomalies = self.analytics.detect_anomalies(missing_data)
        
        # Should detect missing pattern
        missing_anomalies = [a for a in anomalies if a.anomaly_type == 'missing_pattern']
        assert len(missing_anomalies) > 0
    
    def test_trend_analysis(self):
        """Test trend analysis functionality."""
        trends = self.analytics.analyze_trends(self.time_series_data, time_column='date')
        
        # Should return trend analysis results
        assert isinstance(trends, list)
        
        # Check trend structure
        for trend in trends:
            assert hasattr(trend, 'metric')
            assert hasattr(trend, 'trend')
            assert hasattr(trend, 'confidence')
            assert hasattr(trend, 'period')
            assert hasattr(trend, 'description')
            
            assert trend.trend in ['increasing', 'decreasing', 'stable', 'fluctuating']
            assert -1 <= trend.confidence <= 1  # Confidence can be negative for poor fits
    
    def test_trend_analysis_without_time_column(self):
        """Test trend analysis without time column."""
        # Data without time column
        no_time_data = pd.DataFrame({
            'value': [1, 2, 3, 4, 5],
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        
        trends = self.analytics.analyze_trends(no_time_data)
        
        # Should handle gracefully
        assert isinstance(trends, list)
        assert len(trends) == 0
    
    def test_statistical_summary(self):
        """Test statistical summary generation."""
        summary = self.analytics.generate_statistical_summary(self.test_data)
        
        # Check summary structure
        assert 'dataset_info' in summary
        assert 'missing_data' in summary
        assert 'numeric_summary' in summary
        assert 'categorical_summary' in summary
        
        # Check dataset info
        dataset_info = summary['dataset_info']
        assert 'rows' in dataset_info
        assert 'columns' in dataset_info
        assert 'memory_usage' in dataset_info
        assert 'data_types' in dataset_info
        
        # Check missing data
        missing_data = summary['missing_data']
        assert 'total_missing' in missing_data
        assert 'missing_percentage' in missing_data
        assert 'columns_with_missing' in missing_data
        
        # Check numeric summary
        numeric_summary = summary['numeric_summary']
        assert isinstance(numeric_summary, dict)
        
        # Check categorical summary
        categorical_summary = summary['categorical_summary']
        assert isinstance(categorical_summary, dict)
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis functionality."""
        analysis = self.analytics.comprehensive_analysis(self.test_data, time_column='visit_date')
        
        # Check analysis structure
        assert 'quality_metrics' in analysis
        assert 'anomalies' in analysis
        assert 'trends' in analysis
        assert 'statistical_summary' in analysis
        assert 'overall_quality_score' in analysis
        
        # Check quality metrics
        quality_metrics = analysis['quality_metrics']
        assert isinstance(quality_metrics, dict)
        assert len(quality_metrics) > 0
        
        # Check anomalies
        anomalies = analysis['anomalies']
        assert isinstance(anomalies, list)
        
        # Check trends
        trends = analysis['trends']
        assert isinstance(trends, list)
        
        # Check overall quality score
        overall_score = analysis['overall_quality_score']
        assert 0 <= overall_score <= 100
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()
        
        # Should handle gracefully
        metrics = self.analytics.calculate_data_quality_metrics(empty_df)
        assert isinstance(metrics, dict)
        
        anomalies = self.analytics.detect_anomalies(empty_df)
        assert isinstance(anomalies, list)
        assert len(anomalies) == 0
        
        trends = self.analytics.analyze_trends(empty_df)
        assert isinstance(trends, list)
        assert len(trends) == 0
        
        summary = self.analytics.generate_statistical_summary(empty_df)
        assert isinstance(summary, dict)
    
    def test_single_column_dataframe(self):
        """Test handling of single column dataframe."""
        single_col_df = pd.DataFrame({'test': [1, 2, 3, 4, 5]})
        
        # Should process single column
        metrics = self.analytics.calculate_data_quality_metrics(single_col_df)
        assert len(metrics) > 0
        
        anomalies = self.analytics.detect_anomalies(single_col_df)
        assert isinstance(anomalies, list)
        
        summary = self.analytics.generate_statistical_summary(single_col_df)
        assert isinstance(summary, dict)
    
    def test_large_dataframe_performance(self):
        """Test performance with larger dataframe."""
        # Create larger test data
        large_data = pd.DataFrame({
            'id': range(1000),
            'value': np.random.normal(100, 10, 1000),
            'category': np.random.choice(['A', 'B', 'C'], 1000),
            'date': pd.date_range('2024-01-01', periods=1000, freq='h')
        })
        
        # Should process large data without errors
        metrics = self.analytics.calculate_data_quality_metrics(large_data)
        assert len(metrics) > 0
        
        anomalies = self.analytics.detect_anomalies(large_data)
        assert isinstance(anomalies, list)
        
        summary = self.analytics.generate_statistical_summary(large_data)
        assert isinstance(summary, dict)
    
    def test_severity_thresholds(self):
        """Test severity threshold calculations."""
        # Test different quality values
        test_cases = [
            (0.95, 'excellent'),
            (0.85, 'good'),
            (0.70, 'fair'),
            (0.50, 'poor'),
            (0.30, 'critical')
        ]
        
        for value, expected_severity in test_cases:
            severity = self.analytics._get_severity(value, 'completeness')
            assert severity == expected_severity
    
    def test_json_serialization(self):
        """Test that analysis results can be serialized to JSON."""
        analysis = self.analytics.comprehensive_analysis(self.test_data, time_column='visit_date')
        
        # Should be JSON serializable
        import json
        try:
            json_str = json.dumps(analysis)
            assert isinstance(json_str, str)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Analysis results are not JSON serializable: {e}")
    
    def test_overall_quality_score_calculation(self):
        """Test overall quality score calculation."""
        score = self.analytics._calculate_overall_quality_score(self.test_data)
        
        # Should return a score between 0 and 100
        assert 0 <= score <= 100
        assert isinstance(score, float)
        
        # Test with different data quality levels
        high_quality_data = pd.DataFrame({
            'complete': [1, 2, 3, 4, 5],
            'consistent': ['a', 'b', 'c', 'd', 'e'],
            'accurate': [10, 11, 12, 13, 14]
        })
        
        high_score = self.analytics._calculate_overall_quality_score(high_quality_data)
        assert high_score > 0.5  # High quality data should have good score (0.5 = 50%)
        
        # Test with low quality data
        low_quality_data = pd.DataFrame({
            'incomplete': [1, None, 3, None, 5],
            'inconsistent': [1, 'text', 3.14, True, None],
            'inaccurate': [10, 1000, 12, 13, 14]  # 1000 is outlier
        })
        
        low_score = self.analytics._calculate_overall_quality_score(low_quality_data)
        assert low_score < 0.9  # Low quality data should have lower score 