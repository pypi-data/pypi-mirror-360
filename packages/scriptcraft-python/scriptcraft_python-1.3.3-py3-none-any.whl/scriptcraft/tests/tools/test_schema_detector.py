#!/usr/bin/env python3
"""
🧪 Test Suite for Schema Detection Tool
======================================

Comprehensive tests for the schema detection tool with healthcare sample data.
Tests privacy-safe analysis, healthcare pattern recognition, and output generation.

Author: ScriptCraft Team
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json
import tempfile
import shutil
from typing import List, Dict, Any

from scriptcraft.tools.schema_detector import SchemaDetector
from scriptcraft.common.io import ensure_output_dir


class TestSchemaDetector:
    """🔍 Test suite for schema detection functionality"""
    
    def setup_method(self):
        """🔧 Set up test environment for each test"""
        self.detector = SchemaDetector()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.temp_dir / "input"
        self.output_dir = self.temp_dir / "output"
        
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample healthcare data
        self.sample_files = self._create_sample_healthcare_data()
    
    def teardown_method(self):
        """🧹 Clean up test environment after each test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_healthcare_data(self) -> List[str]:
        """🗂️ Create realistic healthcare sample data for testing"""
        
        # Sample patient data
        patient_data = {
            'PatientId': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'FirstName': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'LastName': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown'],
            'DateOfBirth': ['1980-05-15', '1975-12-20', '1990-03-10', '1985-07-22', '1992-11-08'],
            'Gender': ['M', 'F', 'M', 'F', 'M'],
            'Phone': ['555-1234', '555-5678', '555-9012', '555-3456', '555-7890'],
            'Email': ['john.doe@email.com', 'jane.smith@email.com', 'bob.j@email.com', 'alice.w@email.com', 'charlie.b@email.com'],
            'IsActive': [True, True, False, True, True]
        }
        
        # Sample visit data
        visit_data = {
            'VisitId': ['V001', 'V002', 'V003', 'V004', 'V005'],
            'PatientId': ['P001', 'P001', 'P002', 'P003', 'P004'],
            'VisitDate': ['2024-01-15', '2024-02-20', '2024-01-22', '2024-03-10', '2024-02-14'],
            'VisitType': ['Initial', 'Follow-up', 'Initial', 'Follow-up', 'Initial'],
            'ProviderId': ['DR001', 'DR001', 'DR002', 'DR001', 'DR003'],
            'Duration': [45, 30, 60, 30, 45],
            'BloodPressureSystolic': [120, 125, 118, 130, 115],
            'BloodPressureDiastolic': [80, 82, 75, 85, 78],
            'HeartRate': [72, 75, 68, 80, 70],
            'Temperature': [98.6, 98.4, 98.8, 99.1, 98.2],
            'Notes': ['Normal visit', 'Patient doing well', 'Initial assessment completed', 'Blood pressure slightly elevated', 'Routine check-up']
        }
        
        # Sample lab results
        lab_data = {
            'LabResultId': ['L001', 'L002', 'L003', 'L004', 'L005'],
            'PatientId': ['P001', 'P001', 'P002', 'P003', 'P004'],
            'TestName': ['Complete Blood Count', 'Cholesterol Panel', 'Blood Glucose', 'Complete Blood Count', 'Thyroid Function'],
            'TestCategory': ['Hematology', 'Chemistry', 'Chemistry', 'Hematology', 'Endocrinology'],
            'ResultValue': ['Normal', '185', '95', 'Normal', '2.1'],
            'ResultUnit': ['', 'mg/dL', 'mg/dL', '', 'mIU/L'],
            'ReferenceRange': ['4.5-11.0 K/uL', '< 200', '70-100', '4.5-11.0 K/uL', '0.4-4.0'],
            'AbnormalFlag': ['', 'H', '', '', ''],
            'CollectionDate': ['2024-01-15', '2024-02-20', '2024-01-22', '2024-03-10', '2024-02-14'],
            'ResultDate': ['2024-01-16', '2024-02-21', '2024-01-23', '2024-03-11', '2024-02-15']
        }
        
        # Save sample files
        patient_file = self.input_dir / 'sample_patients.csv'
        visit_file = self.input_dir / 'sample_visits.csv'
        lab_file = self.input_dir / 'sample_lab_results.xlsx'
        
        pd.DataFrame(patient_data).to_csv(patient_file, index=False)
        pd.DataFrame(visit_data).to_csv(visit_file, index=False)
        pd.DataFrame(lab_data).to_excel(lab_file, index=False)
        
        return [str(patient_file), str(visit_file), str(lab_file)]
    
    def test_initialization(self) -> None:
        """🧪 Test schema detector initialization"""
        assert self.detector.tool_name == "schema_detector"
        assert self.detector.description == "🔍 Analyzes datasets and generates database schemas"
        assert self.detector.config['privacy_mode'] is True
        assert self.detector.config['target_database'] == 'sqlite'
        assert self.detector.supported_formats == {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
    
    def test_healthcare_patterns(self) -> None:
        """🏥 Test healthcare pattern recognition"""
        patterns = self.detector.healthcare_patterns
        
        # Test patient ID pattern
        assert 'patient_id' in patterns
        assert patterns['patient_id']['privacy'] == 'sensitive'
        assert 'UNIQUE' in patterns['patient_id']['constraints']
        
        # Test SSN pattern
        assert 'ssn' in patterns
        assert patterns['ssn']['privacy'] == 'highly_sensitive'
        
        # Test diagnosis pattern
        assert 'diagnosis' in patterns
        assert patterns['diagnosis']['privacy'] == 'highly_sensitive'
    
    def test_data_type_mapping(self) -> None:
        """🗂️ Test data type mapping for different databases"""
        mappings = self.detector.data_type_mapping
        
        # Test SQLite mapping
        assert mappings['sqlite']['integer'] == 'INTEGER'
        assert mappings['sqlite']['string'] == 'TEXT'
        
        # Test SQL Server mapping
        assert mappings['sqlserver']['integer'] == 'INT'
        assert mappings['sqlserver']['string'] == 'NVARCHAR'
        
        # Test PostgreSQL mapping
        assert mappings['postgresql']['boolean'] == 'BOOLEAN'
        assert mappings['postgresql']['json'] == 'JSONB'
    
    def test_load_data_sample_csv(self) -> None:
        """📄 Test loading CSV data samples"""
        csv_file = Path(self.sample_files[0])  # patients.csv
        df = self.detector._load_data_sample(csv_file)
        
        assert df is not None
        assert len(df) > 0
        assert 'PatientId' in df.columns
        assert 'FirstName' in df.columns
        assert 'DateOfBirth' in df.columns
    
    def test_load_data_sample_excel(self) -> None:
        """📊 Test loading Excel data samples"""
        excel_file = Path(self.sample_files[2])  # lab_results.xlsx
        df = self.detector._load_data_sample(excel_file)
        
        assert df is not None
        assert len(df) > 0
        assert 'LabResultId' in df.columns
        assert 'TestName' in df.columns
        assert 'ResultValue' in df.columns
    
    def test_column_analysis(self) -> None:
        """📊 Test individual column analysis"""
        csv_file = Path(self.sample_files[0])  # patients.csv
        df = self.detector._load_data_sample(csv_file)
        
        # Test patient ID column
        patient_id_col = self.detector._analyze_column(df, 'PatientId')
        assert patient_id_col.name == 'PatientId'
        assert patient_id_col.privacy_level == 'sensitive'
        assert patient_id_col.is_primary_key is True
        assert 'UNIQUE' in patient_id_col.constraints
        
        # Test date of birth column
        dob_col = self.detector._analyze_column(df, 'DateOfBirth')
        assert dob_col.privacy_level == 'sensitive'
        assert dob_col.data_type in ['date', 'string']  # Could be either depending on parsing
    
    def test_privacy_safe_samples(self) -> None:
        """🔐 Test privacy-safe sample value generation"""
        csv_file = Path(self.sample_files[0])
        df = self.detector._load_data_sample(csv_file)
        
        # Test with privacy mode enabled
        self.detector.config['privacy_mode'] = True
        samples = self.detector._get_safe_sample_values(df['FirstName'])
        assert all('<' in sample and '>' in sample for sample in samples)
        
        # Test with privacy mode disabled
        self.detector.config['privacy_mode'] = False
        samples = self.detector._get_safe_sample_values(df['FirstName'])
        assert any('<' not in sample for sample in samples)
    
    def test_data_type_inference(self) -> None:
        """🧠 Test data type inference"""
        csv_file = Path(self.sample_files[1])  # visits.csv
        df = self.detector._load_data_sample(csv_file)
        
        # Test integer inference
        duration_type = self.detector._infer_data_type(df['Duration'], 'Duration')
        assert duration_type[0] == 'integer'
        
        # Test float inference
        temp_type = self.detector._infer_data_type(df['Temperature'], 'Temperature')
        assert temp_type[0] == 'float'
        
        # Test string inference
        notes_type = self.detector._infer_data_type(df['Notes'], 'Notes')
        assert notes_type[0] == 'string'
    
    def test_primary_key_detection(self) -> None:
        """🔑 Test primary key detection"""
        csv_file = Path(self.sample_files[0])
        df = self.detector._load_data_sample(csv_file)
        
        # Test obvious primary key
        assert self.detector._could_be_primary_key(df['PatientId'], 'PatientId') is True
        
        # Test non-primary key
        assert self.detector._could_be_primary_key(df['FirstName'], 'FirstName') is False
    
    def test_foreign_key_detection(self) -> None:
        """🔗 Test foreign key detection"""
        # Test obvious foreign key patterns
        assert self.detector._could_be_foreign_key('PatientId') is True
        assert self.detector._could_be_foreign_key('ProviderId') is True
        assert self.detector._could_be_foreign_key('FirstName') is False
    
    def test_table_classification(self) -> None:
        """🏷️ Test table type classification"""
        # Test dimension table (patient data)
        patient_columns = []  # Would need actual column objects
        table_type = self.detector._classify_table_type('Patients', patient_columns)
        assert table_type in ['dimension', 'fact', 'lookup', 'audit']
        
        # Test lookup table
        lookup_type = self.detector._classify_table_type('lookup_codes', [])
        assert lookup_type == 'lookup'
        
        # Test audit table
        audit_type = self.detector._classify_table_type('audit_log', [])
        assert audit_type == 'audit'
    
    def test_analyze_single_dataset(self) -> None:
        """📊 Test analysis of a single dataset"""
        csv_file = Path(self.sample_files[0])  # patients.csv
        schema = self.detector._analyze_single_dataset(csv_file)
        
        assert schema is not None
        assert schema.name == 'SamplePatients'  # Pascal case
        assert len(schema.columns) > 0
        assert schema.table_type in ['dimension', 'fact', 'lookup', 'audit']
        
        # Check that patient ID is identified as primary key
        patient_id_cols = [col for col in schema.columns if 'patient' in col.name.lower()]
        assert len(patient_id_cols) > 0
        assert any(col.is_primary_key for col in patient_id_cols)
    
    def test_analyze_multiple_datasets(self) -> None:
        """📂 Test analysis of multiple datasets"""
        schemas = self.detector.analyze_datasets(self.sample_files)
        
        assert len(schemas) == 3  # Three sample files
        assert all(schema.name for schema in schemas)
        assert all(len(schema.columns) > 0 for schema in schemas)
        
        # Check schema names
        schema_names = [schema.name for schema in schemas]
        assert 'SamplePatients' in schema_names
        assert 'SampleVisits' in schema_names
        assert 'SampleLabResults' in schema_names
    
    def test_sql_generation(self) -> None:
        """🏗️ Test SQL schema generation"""
        schemas = self.detector.analyze_datasets(self.sample_files)
        sql_content = self.detector.generate_sql_schema(schemas)
        
        assert 'CREATE TABLE' in sql_content
        assert 'SamplePatients' in sql_content
        assert 'SampleVisits' in sql_content
        assert 'SampleLabResults' in sql_content
        
        # Check for privacy comments
        assert '-- Privacy:' in sql_content or 'Privacy:' in sql_content
    
    def test_documentation_generation(self) -> None:
        """📚 Test documentation generation"""
        schemas = self.detector.analyze_datasets(self.sample_files)
        doc_content = self.detector.generate_documentation(schemas)
        
        assert '# 📊 Dataset Schema Analysis Report' in doc_content
        assert 'Total Tables' in doc_content
        assert 'Privacy & Security Recommendations' in doc_content
        assert 'SamplePatients' in doc_content
    
    def test_output_generation(self) -> None:
        """💾 Test output file generation"""
        schemas = self.detector.analyze_datasets(self.sample_files)
        self.detector.save_outputs(schemas, self.output_dir)
        
        # Check that files were created
        output_files = list(self.output_dir.glob('*'))
        assert len(output_files) > 0
        
        # Check for SQL file
        sql_files = list(self.output_dir.glob('detected_schema_*.sql'))
        assert len(sql_files) > 0
        
        # Check for JSON file
        json_files = list(self.output_dir.glob('detected_schema_*.json'))
        assert len(json_files) > 0
        
        # Check for documentation
        doc_files = list(self.output_dir.glob('schema_analysis_*.md'))
        assert len(doc_files) > 0
    
    def test_privacy_levels(self) -> None:
        """🔐 Test privacy level classification"""
        schemas = self.detector.analyze_datasets(self.sample_files)
        
        # Find patient schema
        patient_schema = next((s for s in schemas if 'patient' in s.name.lower()), None)
        assert patient_schema is not None
        
        # Check privacy levels
        privacy_levels = [col.privacy_level for col in patient_schema.columns]
        assert 'sensitive' in privacy_levels  # PatientId, DateOfBirth
        assert 'public' in privacy_levels or 'internal' in privacy_levels  # Some columns should be less sensitive
    
    def test_full_workflow(self) -> None:
        """🚀 Test complete schema detection workflow"""
        # Test the main run method
        success = self.detector.run(
            input_paths=self.sample_files,
            output_dir=str(self.output_dir),
            target_database='sqlite',
            privacy_mode=True
        )
        
        assert success is True
        
        # Verify outputs were created
        output_files = list(self.output_dir.glob('*'))
        assert len(output_files) >= 3  # At least SQL, JSON, and documentation
        
        # Verify SQL content
        sql_files = list(self.output_dir.glob('detected_schema_*.sql'))
        assert len(sql_files) > 0
        
        with open(sql_files[0], 'r') as f:
            sql_content = f.read()
            assert 'CREATE TABLE SamplePatients' in sql_content
            assert 'CREATE TABLE SampleVisits' in sql_content
            assert 'CREATE TABLE SampleLabResults' in sql_content
    
    def test_different_databases(self) -> None:
        """🗄️ Test different database targets"""
        # Test SQL Server
        self.detector.config['target_database'] = 'sqlserver'
        schemas = self.detector.analyze_datasets([self.sample_files[0]])
        sql_content = self.detector.generate_sql_schema(schemas)
        assert 'NVARCHAR' in sql_content
        
        # Test PostgreSQL
        self.detector.config['target_database'] = 'postgresql'
        schemas = self.detector.analyze_datasets([self.sample_files[0]])
        sql_content = self.detector.generate_sql_schema(schemas)
        assert 'VARCHAR' in sql_content
    
    def test_naming_conventions(self) -> None:
        """🏷️ Test different naming conventions"""
        # Test snake_case
        self.detector.config['naming_convention'] = 'snake_case'
        csv_file = Path(self.sample_files[0])
        schema = self.detector._analyze_single_dataset(csv_file)
        
        snake_case_names = [col.name for col in schema.columns if '_' in col.name]
        assert len(snake_case_names) > 0  # Should have some snake_case names
        
        # Test pascal_case (default)
        self.detector.config['naming_convention'] = 'pascal_case'
        schema = self.detector._analyze_single_dataset(csv_file)
        
        pascal_case_names = [col.name for col in schema.columns if col.name[0].isupper()]
        assert len(pascal_case_names) > 0  # Should have some PascalCase names


# Additional integration tests
class TestSchemaDetectorIntegration:
    """🔗 Integration tests for schema detector"""
    
    def test_json_schema_export(self) -> None:
        """📄 Test JSON schema export functionality"""
        detector = SchemaDetector()
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create simple test data
            test_data = {
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie'],
                'active': [True, False, True]
            }
            
            test_file = temp_dir / 'test.csv'
            pd.DataFrame(test_data).to_csv(test_file, index=False)
            
            # Analyze and export
            schemas = detector.analyze_datasets([str(test_file)])
            output_dir = temp_dir / 'output'
            output_dir.mkdir()
            
            detector.save_outputs(schemas, output_dir)
            
            # Check JSON output
            json_files = list(output_dir.glob('detected_schema_*.json'))
            assert len(json_files) > 0
            
            with open(json_files[0], 'r') as f:
                json_data = json.load(f)
                assert 'metadata' in json_data
                assert 'schemas' in json_data
                assert len(json_data['schemas']) == 1
                
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 