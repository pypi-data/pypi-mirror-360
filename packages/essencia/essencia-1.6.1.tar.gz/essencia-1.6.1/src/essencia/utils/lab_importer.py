"""Laboratory test CSV importer utility.

Provides functionality to import laboratory test results from CSV files
with the format: dates as columns, test names as rows.
"""
import csv
import datetime
import logging
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from ..models.laboratory import LabTest, LabTestBatch, LabTestType, LabTestCategory
from ..models.people import Patient

logger = logging.getLogger(__name__)


class LabCSVImporter:
    """Import laboratory test results from CSV files.
    
    Handles CSV format where:
    - First row contains dates in DD.MM.YYYY format
    - First column contains test names
    - Cells contain test results with optional units
    """
    
    # Common test name mappings to standardize names
    TEST_MAPPINGS = {
        'hemácias': {'name': 'Hemácias', 'unit': 'milhões/mm³', 'category': LabTestCategory.HEMATOLOGY},
        'hematócrito': {'name': 'Hematócrito', 'unit': '%', 'category': LabTestCategory.HEMATOLOGY},
        'hemoglobina': {'name': 'Hemoglobina', 'unit': 'g/dL', 'category': LabTestCategory.HEMATOLOGY},
        'leucócitos totais': {'name': 'Leucócitos', 'unit': '/mm³', 'category': LabTestCategory.HEMATOLOGY},
        'plaquetas': {'name': 'Plaquetas', 'unit': 'mil/mm³', 'category': LabTestCategory.HEMATOLOGY},
        'glicemia jj': {'name': 'Glicemia Jejum', 'unit': 'mg/dL', 'category': LabTestCategory.GLUCOSE},
        'hemoglobina glicada': {'name': 'Hemoglobina Glicada', 'unit': '%', 'category': LabTestCategory.GLUCOSE},
        'triglicérides': {'name': 'Triglicérides', 'unit': 'mg/dL', 'category': LabTestCategory.LIPIDS},
        'colesterol total': {'name': 'Colesterol Total', 'unit': 'mg/dL', 'category': LabTestCategory.LIPIDS},
        'hdl': {'name': 'HDL Colesterol', 'unit': 'mg/dL', 'category': LabTestCategory.LIPIDS},
        'ldl': {'name': 'LDL Colesterol', 'unit': 'mg/dL', 'category': LabTestCategory.LIPIDS},
        'tgo': {'name': 'AST/TGO', 'unit': 'U/L', 'category': LabTestCategory.HEPATIC},
        'tgp': {'name': 'ALT/TGP', 'unit': 'U/L', 'category': LabTestCategory.HEPATIC},
        'ggt': {'name': 'Gama GT', 'unit': 'U/L', 'category': LabTestCategory.HEPATIC},
        'uréia': {'name': 'Ureia', 'unit': 'mg/dL', 'category': LabTestCategory.RENAL},
        'creatinina': {'name': 'Creatinina', 'unit': 'mg/dL', 'category': LabTestCategory.RENAL},
        'ácido úrico': {'name': 'Ácido Úrico', 'unit': 'mg/dL', 'category': LabTestCategory.RENAL},
        'tsh': {'name': 'TSH', 'unit': 'µUI/mL', 'category': LabTestCategory.THYROID},
        't4 livre': {'name': 'T4 Livre', 'unit': 'ng/dL', 'category': LabTestCategory.THYROID},
        'vitamina d': {'name': 'Vitamina D', 'unit': 'ng/mL', 'category': LabTestCategory.VITAMINS},
        'vitamina b12': {'name': 'Vitamina B12', 'unit': 'pg/mL', 'category': LabTestCategory.VITAMINS},
        'ferritina': {'name': 'Ferritina', 'unit': 'ng/mL', 'category': LabTestCategory.HEMATOLOGY},
        'sódio': {'name': 'Sódio', 'unit': 'mEq/L', 'category': LabTestCategory.ELECTROLYTES},
        'potássio': {'name': 'Potássio', 'unit': 'mEq/L', 'category': LabTestCategory.ELECTROLYTES},
        'cálcio': {'name': 'Cálcio', 'unit': 'mg/dL', 'category': LabTestCategory.ELECTROLYTES},
        'fósforo': {'name': 'Fósforo', 'unit': 'mg/dL', 'category': LabTestCategory.ELECTROLYTES},
        'magnésio': {'name': 'Magnésio', 'unit': 'mg/dL', 'category': LabTestCategory.ELECTROLYTES},
        'pcr ultra sensível': {'name': 'PCR Ultrassensível', 'unit': 'mg/L', 'category': LabTestCategory.IMMUNOLOGY},
    }
    
    def __init__(self, patient_key: str, doctor_key: str = 'admin'):
        """Initialize importer with patient and doctor context.
        
        Args:
            patient_key: Patient identifier
            doctor_key: Doctor identifier (default: 'admin')
        """
        self.patient_key = patient_key
        self.doctor_key = doctor_key
        self.test_type_cache: Dict[str, LabTestType] = {}
        
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date from DD.MM.YYYY format.
        
        Args:
            date_str: Date string in DD.MM.YYYY format
            
        Returns:
            date: Parsed date or None if invalid
        """
        try:
            parts = date_str.strip().split('.')
            if len(parts) == 3:
                day, month, year = map(int, parts)
                return date(year, month, day)
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def parse_value(self, value_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse test value and extract numeric part and unit.
        
        Args:
            value_str: Raw value from CSV
            
        Returns:
            Tuple of (value, unit) or (None, None) if empty
        """
        if not value_str or value_str.strip() in ['', '#DIV/0!']:
            return None, None
            
        value_str = value_str.strip()
        
        # Replace comma with dot for decimal
        value_str = value_str.replace(',', '.')
        
        # Check for quoted values (keep as string)
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str.strip('"'), None
            
        return value_str, None
    
    def normalize_test_name(self, raw_name: str) -> Tuple[str, str, LabTestCategory]:
        """Normalize test name and get standard unit and category.
        
        Args:
            raw_name: Raw test name from CSV
            
        Returns:
            Tuple of (normalized_name, unit, category)
        """
        # Clean the name
        clean_name = raw_name.strip().lower()
        
        # Remove units from name if present
        unit_patterns = [
            r'\s*\(.*?\)\s*$',  # Remove anything in parentheses
            r'\s*\[.*?\]\s*$',  # Remove anything in brackets
        ]
        for pattern in unit_patterns:
            clean_name = re.sub(pattern, '', clean_name)
        
        # Look up in mappings
        if clean_name in self.TEST_MAPPINGS:
            mapping = self.TEST_MAPPINGS[clean_name]
            return mapping['name'], mapping['unit'], mapping['category']
        
        # Default fallback
        return raw_name.strip(), '', LabTestCategory.BIOCHEMISTRY
    
    def get_or_create_test_type(self, test_name: str, unit: str, category: LabTestCategory) -> Optional[LabTestType]:
        """Get existing or create new test type.
        
        Args:
            test_name: Normalized test name
            unit: Unit of measurement
            category: Test category
            
        Returns:
            LabTestType instance or None if error
        """
        cache_key = f"{test_name}:{unit}"
        
        if cache_key in self.test_type_cache:
            return self.test_type_cache[cache_key]
        
        try:
            # Try to find existing
            test_type = LabTestType.find_one({'name': test_name, 'unit': unit})
            
            if not test_type:
                # Create new test type
                code = re.sub(r'[^A-Z0-9]', '', test_name.upper())[:10]
                test_type = LabTestType(
                    code=code,
                    name=test_name,
                    category=category,
                    unit=unit
                )
                test_type = test_type.save_self()
                logger.info(f"Created new test type: {test_name}")
            
            self.test_type_cache[cache_key] = test_type
            return test_type
            
        except Exception as e:
            logger.error(f"Error getting/creating test type {test_name}: {e}")
            return None
    
    def import_csv(self, file_path: Path, laboratory: Optional[str] = None) -> Tuple[int, List[str]]:
        """Import laboratory tests from CSV file.
        
        Args:
            file_path: Path to CSV file
            laboratory: Laboratory name (optional)
            
        Returns:
            Tuple of (success_count, error_messages)
        """
        success_count = 0
        errors = []
        
        # Create batch record
        batch = LabTestBatch(
            patient_key=self.patient_key,
            source_file=file_path.name,
            laboratory=laboratory,
            status=LabTestBatch.Status.PROCESSING
        )
        batch = batch.save_self()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 2:
                    raise ValueError("CSV file must have at least 2 rows")
                
                # Parse header row for dates
                header = rows[0]
                dates = []
                for i, cell in enumerate(header[1:], 1):  # Skip first column
                    parsed_date = self.parse_date(cell)
                    if parsed_date:
                        dates.append((i, parsed_date))
                
                logger.info(f"Found {len(dates)} date columns")
                
                # Process each test row
                for row_idx, row in enumerate(rows[1:], 1):
                    if not row or not row[0].strip():
                        continue
                    
                    raw_test_name = row[0]
                    test_name, unit, category = self.normalize_test_name(raw_test_name)
                    
                    # Get or create test type
                    test_type = self.get_or_create_test_type(test_name, unit, category)
                    if not test_type:
                        errors.append(f"Row {row_idx}: Could not create test type for {test_name}")
                        continue
                    
                    # Process each date column
                    for col_idx, test_date in dates:
                        if col_idx >= len(row):
                            continue
                            
                        value_str = row[col_idx]
                        parsed_value, _ = self.parse_value(value_str)
                        
                        if parsed_value is None:
                            continue
                        
                        try:
                            # Create lab test record
                            lab_test = LabTest(
                                doctor_key=self.doctor_key,
                                patient_key=self.patient_key,
                                test_type_key=test_type.key,
                                test_name=test_name,
                                value=parsed_value,
                                unit=unit,
                                collection_date=test_date,
                                date=test_date,
                                laboratory=laboratory,
                                batch_key=batch.key
                            )
                            
                            # Check if abnormal (would need reference ranges)
                            lab_test.is_abnormal = lab_test.check_abnormal()
                            
                            lab_test = lab_test.save_self()
                            success_count += 1
                            
                        except Exception as e:
                            errors.append(f"Row {row_idx}, Date {test_date}: {str(e)}")
                
                # Update batch
                batch.test_count = success_count
                batch.status = LabTestBatch.Status.COMPLETED if not errors else LabTestBatch.Status.PARTIAL
                batch.notes = f"Imported {success_count} tests" + (f", {len(errors)} errors" if errors else "")
                batch.update_self()
                
        except Exception as e:
            logger.error(f"Import failed: {e}")
            batch.status = LabTestBatch.Status.ERROR
            batch.notes = str(e)
            batch.update_self()
            errors.append(f"Import failed: {str(e)}")
        
        return success_count, errors
    
    def import_from_dict(self, data: Dict[str, Any], laboratory: Optional[str] = None) -> Tuple[int, List[str]]:
        """Import laboratory tests from dictionary format.
        
        Args:
            data: Dictionary with test data
            laboratory: Laboratory name (optional)
            
        Returns:
            Tuple of (success_count, error_messages)
        """
        success_count = 0
        errors = []
        
        # Expected format: {'date': '2024-01-15', 'tests': [{'name': 'Hemoglobina', 'value': '12.5', 'unit': 'g/dL'}, ...]}
        try:
            test_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            for test_data in data.get('tests', []):
                test_name = test_data.get('name')
                value = test_data.get('value')
                unit = test_data.get('unit', '')
                
                if not test_name or not value:
                    continue
                
                # Normalize and get test type
                norm_name, norm_unit, category = self.normalize_test_name(test_name)
                if unit:
                    norm_unit = unit
                    
                test_type = self.get_or_create_test_type(norm_name, norm_unit, category)
                if not test_type:
                    errors.append(f"Could not create test type for {norm_name}")
                    continue
                
                try:
                    lab_test = LabTest(
                        doctor_key=self.doctor_key,
                        patient_key=self.patient_key,
                        test_type_key=test_type.key,
                        test_name=norm_name,
                        value=str(value),
                        unit=norm_unit,
                        collection_date=test_date,
                        date=test_date,
                        laboratory=laboratory
                    )
                    
                    lab_test = lab_test.save_self()
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Error saving {test_name}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Import failed: {str(e)}")
            
        return success_count, errors