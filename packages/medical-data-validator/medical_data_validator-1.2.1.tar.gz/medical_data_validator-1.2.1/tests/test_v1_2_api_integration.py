"""
Test cases for Medical Data Validator v1.2 API Integration
"""

import pytest
import requests
import pandas as pd
from io import StringIO
import json

class TestV12APIIntegration:
    """Test cases for v1.2 API integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:8000"
        
        # Test data for different scenarios
        self.test_data = {
            'patient_id': ['P001', 'P002', 'P003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'ssn': ['123-45-6789', '987-65-4321', '111-22-3333'],
            'diagnosis_code': ['E11.9', 'I10', 'Z51.11'],
            'lab_code': ['58410-2', '789-8', '58410-2'],
            'procedure_code': ['99213', '99214', '99215'],
            'visit_date': ['2024-01-01', '2024-01-02', '2024-01-03']
        }
        
        self.clean_data = {
            'id': ['1', '2', '3'],
            'value': [100, 200, 300],
            'category': ['A', 'B', 'A']
        }
    
    def test_v12_compliance_endpoint(self):
        """Test v1.2 compliance endpoint."""
        # Create CSV data
        df = pd.DataFrame(self.test_data)
        csv_data = df.to_csv(index=False)
        
        files = {'file': ('test_data.csv', StringIO(csv_data), 'text/csv')}
        
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files)
        
        assert response.status_code == 200
        result = response.json()
        
        # Check response structure
        assert 'message' in result
        assert 'compliance_report' in result
        
        compliance_report = result['compliance_report']
        
        # Check v1.2 compliance data
        assert 'hipaa' in compliance_report
        assert 'gdpr' in compliance_report
        assert 'fda' in compliance_report
        assert 'medical_coding' in compliance_report
        assert 'overall_score' in compliance_report
    
    def test_v12_compliance_with_template(self):
        """Test v1.2 compliance with template."""
        df = pd.DataFrame(self.test_data)
        csv_data = df.to_csv(index=False)
        
        files = {'file': ('test_data.csv', StringIO(csv_data), 'text/csv')}
        data = {'compliance_template': 'clinical_trials'}
        
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should include template information
        assert 'compliance_report' in result
        compliance_report = result['compliance_report']
        assert 'template_applied' in compliance_report
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint."""
        df = pd.DataFrame(self.test_data)
        csv_data = df.to_csv(index=False)
        
        files = {'file': ('test_data.csv', StringIO(csv_data), 'text/csv')}
        data = {'time_column': 'visit_date'}
        
        response = requests.post(f"{self.base_url}/api/analytics", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Check analytics structure
        assert 'quality_metrics' in result
        assert 'anomalies' in result
        assert 'trends' in result
        assert 'statistical_summary' in result
        assert 'overall_quality_score' in result
        
        # Check quality metrics
        quality_metrics = result['quality_metrics']
        assert 'completeness' in quality_metrics
        assert 'consistency' in quality_metrics
        assert 'accuracy' in quality_metrics
        assert 'timeliness' in quality_metrics
    
    def test_monitoring_stats_endpoint(self):
        """Test monitoring stats endpoint."""
        response = requests.get(f"{self.base_url}/api/monitoring/stats")
        
        assert response.status_code == 200
        result = response.json()
        
        # Check stats structure
        assert 'total_validations' in result
        assert 'successful_validations' in result
        assert 'failed_validations' in result
        assert 'average_processing_time' in result
        assert 'active_alerts' in result
        assert 'last_validation_time' in result
    
    def test_monitoring_alerts_endpoint(self):
        """Test monitoring alerts endpoint."""
        response = requests.get(f"{self.base_url}/api/monitoring/alerts")
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return list of alerts
        assert isinstance(result, list)
        
        # Check alert structure if alerts exist
        if len(result) > 0:
            alert = result[0]
            assert 'id' in alert
            assert 'timestamp' in alert
            assert 'alert_type' in alert
            assert 'severity' in alert
            assert 'message' in alert
    
    def test_monitoring_trends_endpoint(self):
        """Test monitoring trends endpoint."""
        response = requests.get(f"{self.base_url}/api/monitoring/trends/compliance_score?hours=24")
        
        assert response.status_code == 200
        result = response.json()
        
        # Check trends structure
        assert 'trends' in result
        assert isinstance(result['trends'], list)
        
        # Check trend data structure if trends exist
        if len(result['trends']) > 0:
            trend = result['trends'][0]
            assert 'timestamp' in trend
            assert 'value' in trend
            assert 'status' in trend
    
    def test_custom_rules_endpoint(self):
        """Test custom rules management endpoints."""
        # Test adding custom rule
        custom_rule = {
            'name': 'test_rule',
            'description': 'Test custom rule',
            'pattern': r'\bTEST\b',
            'severity': 'high',
            'field_pattern': 'test_column',
            'recommendation': 'Remove test data'
        }
        
        response = requests.post(f"{self.base_url}/api/compliance/custom-rules", json=custom_rule)
        assert response.status_code == 200
        
        # Test getting custom rules
        response = requests.get(f"{self.base_url}/api/compliance/custom-rules")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        
        # Test removing custom rule
        response = requests.delete(f"{self.base_url}/api/compliance/custom-rules/test_rule")
        assert response.status_code == 200
    
    def test_compliance_templates_endpoint(self):
        """Test compliance templates endpoint."""
        response = requests.get(f"{self.base_url}/api/compliance/templates")
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return list of available templates
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check template structure
        template = result[0]
        assert 'name' in template
        assert 'description' in template
    
    def test_validation_with_v12_features(self):
        """Test validation with v1.2 features enabled."""
        df = pd.DataFrame(self.test_data)
        csv_data = df.to_csv(index=False)
        
        files = {'file': ('test_data.csv', StringIO(csv_data), 'text/csv')}
        data = {
            'enable_compliance': 'true',
            'compliance_template': 'clinical_trials'
        }
        
        response = requests.post(f"{self.base_url}/api/validate/file", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should include v1.2 compliance data
        assert 'compliance_report' in result
        compliance_report = result['compliance_report']
        assert 'hipaa' in compliance_report
        assert 'gdpr' in compliance_report
        assert 'fda' in compliance_report
        assert 'medical_coding' in compliance_report
    
    def test_error_handling(self):
        """Test error handling in v1.2 endpoints."""
        # Test with invalid file
        files = {'file': ('invalid.txt', StringIO('invalid data'), 'text/plain')}
        
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files)
        
        # Should handle error gracefully
        assert response.status_code in [400, 422, 500]
        
        # Test with missing file
        response = requests.post(f"{self.base_url}/api/compliance/v1.2")
        assert response.status_code in [400, 422]
    
    def test_json_serialization(self):
        """Test that all API responses are JSON serializable."""
        endpoints = [
            ('/api/compliance/v1.2', 'POST'),
            ('/api/analytics', 'POST'),
            ('/api/monitoring/stats', 'GET'),
            ('/api/monitoring/alerts', 'GET'),
            ('/api/monitoring/trends/compliance_score', 'GET'),
            ('/api/compliance/custom-rules', 'GET'),
            ('/api/compliance/templates', 'GET')
        ]
        
        for endpoint, method in endpoints:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}")
            else:
                # For POST endpoints, use minimal data
                if 'compliance/v1.2' in endpoint:
                    df = pd.DataFrame(self.clean_data)
                    csv_data = df.to_csv(index=False)
                    files = {'file': ('test.csv', StringIO(csv_data), 'text/csv')}
                    response = requests.post(f"{self.base_url}{endpoint}", files=files)
                elif 'analytics' in endpoint:
                    df = pd.DataFrame(self.clean_data)
                    csv_data = df.to_csv(index=False)
                    files = {'file': ('test.csv', StringIO(csv_data), 'text/csv')}
                    response = requests.post(f"{self.base_url}{endpoint}", files=files)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Test JSON serialization
                    json.dumps(result)
                except (TypeError, ValueError) as e:
                    pytest.fail(f"Response from {endpoint} is not JSON serializable: {e}")
    
    def test_performance_with_large_data(self):
        """Test performance with larger datasets."""
        # Create larger test dataset
        large_data = {
            'id': [str(i) for i in range(1000)],
            'value': list(range(1000)),
            'category': ['A', 'B'] * 500,
            'date': [f'2024-01-{(i % 30) + 1:02d}' for i in range(1000)]
        }
        
        df = pd.DataFrame(large_data)
        csv_data = df.to_csv(index=False)
        
        # Use a fresh file object for each request
        files1 = {'file': ('large_data.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files1)
        assert response.status_code == 200
        
        files2 = {'file': ('large_data.csv', StringIO(csv_data), 'text/csv')}
        data = {'time_column': 'date'}
        response = requests.post(f"{self.base_url}/api/analytics", files=files2, data=data)
        
        if response.status_code != 200:
            print(f"Analytics endpoint failed with status {response.status_code}")
            print(f"Response body: {response.text}")
        
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        df = pd.DataFrame(self.test_data)
        csv_data = df.to_csv(index=False)
        
        results = []
        errors = []
        
        def make_request():
            try:
                files = {'file': ('test.csv', StringIO(csv_data), 'text/csv')}
                response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(status == 200 for status in results), f"Some requests failed: {results}"
    
    def test_api_versioning(self):
        """Test API versioning compatibility."""
        # Test that v1.2 endpoints don't break existing functionality
        df = pd.DataFrame(self.clean_data)
        csv_data = df.to_csv(index=False)

        # For /api/validate/file
        files1 = {'file': ('test.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/validate/file", files=files1)
        assert response.status_code == 200

        # For /api/compliance/check
        files2 = {'file': ('test.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/compliance/check", files=files2)
        if response.status_code != 200:
            print(f"Compliance check endpoint failed with status {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        
        # Test health endpoint
        response = requests.get(f"{self.base_url}/api/health")
        assert response.status_code == 200
    
    def test_data_validation_edge_cases(self):
        """Test data validation edge cases."""
        # Test with empty data (no rows but with columns)
        empty_df = pd.DataFrame({'test': []})
        csv_data = empty_df.to_csv(index=False)
        
        files1 = {'file': ('empty.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files1)
        if response.status_code != 200:
            print(f"Compliance check endpoint failed with status {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        
        # Test with single row
        single_row_df = pd.DataFrame({'test': ['value']})
        csv_data = single_row_df.to_csv(index=False)
        
        files2 = {'file': ('single.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files2)
        assert response.status_code == 200
        
        # Test with single column
        single_col_df = pd.DataFrame({'test': ['value1', 'value2', 'value3']})
        csv_data = single_col_df.to_csv(index=False)
        
        files3 = {'file': ('single_col.csv', StringIO(csv_data), 'text/csv')}
        response = requests.post(f"{self.base_url}/api/compliance/v1.2", files=files3)
        assert response.status_code == 200 