"""Example of importing and analyzing laboratory test data.

This example demonstrates how to:
1. Import lab test data from CSV
2. Query and analyze test results
3. Generate trend reports
"""
from pathlib import Path
from datetime import date, timedelta
from essencia.models import Patient, LabTestAnalyzer, LabTestCategory
from essencia.utils import LabCSVImporter


def import_lab_data_example():
    """Example of importing lab data from CSV."""
    
    # Assume we have a patient
    patient_key = "patient_123"  # Replace with actual patient key
    
    # Create importer
    importer = LabCSVImporter(patient_key=patient_key, doctor_key="dr_smith")
    
    # Import from CSV file
    csv_path = Path("lab.csv")
    if csv_path.exists():
        success_count, errors = importer.import_csv(csv_path, laboratory="Laboratório Central")
        
        print(f"Imported {success_count} test results")
        if errors:
            print(f"Errors encountered: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
    
    # Alternative: Import from dictionary
    lab_data = {
        'date': '2024-01-15',
        'tests': [
            {'name': 'Hemoglobina', 'value': '12.5', 'unit': 'g/dL'},
            {'name': 'Glicemia Jejum', 'value': '95', 'unit': 'mg/dL'},
            {'name': 'Colesterol Total', 'value': '180', 'unit': 'mg/dL'},
        ]
    }
    
    success_count, errors = importer.import_from_dict(lab_data, laboratory="Lab Express")
    print(f"\nImported {success_count} tests from dictionary")


def analyze_lab_data_example():
    """Example of analyzing lab test data."""
    
    patient_key = "patient_123"  # Replace with actual patient key
    
    # 1. Get patient's complete lab history
    print("\n=== Complete Lab History ===")
    history = LabTestAnalyzer.get_patient_history(patient_key)
    print(f"Total tests: {len(history)}")
    
    # 2. Get history for specific test
    print("\n=== Hemoglobin History ===")
    hb_history = LabTestAnalyzer.get_patient_history(
        patient_key, 
        test_name="Hemoglobina",
        start_date=date.today() - timedelta(days=365)
    )
    for test in hb_history[:5]:  # Show last 5 results
        print(f"{test.collection_date}: {test.value.decrypt()} {test.unit}")
    
    # 3. Get test trend analysis
    print("\n=== Glucose Trend Analysis ===")
    glucose_trend = LabTestAnalyzer.get_test_trend(patient_key, "Glicemia Jejum", limit=20)
    if 'error' not in glucose_trend:
        print(f"Test: {glucose_trend['test_name']}")
        print(f"Latest value: {glucose_trend['latest']} {glucose_trend['unit']}")
        print(f"Range: {glucose_trend['min']} - {glucose_trend['max']}")
        print(f"Mean: {glucose_trend['mean']:.2f}")
        print(f"Trend: {glucose_trend.get('trend', 'N/A')}")
    
    # 4. Get abnormal results
    print("\n=== Recent Abnormal Results ===")
    abnormal_results = LabTestAnalyzer.get_abnormal_results(patient_key, limit=10)
    for test in abnormal_results:
        print(f"{test.collection_date} - {test.test_name}: {test.value.decrypt()} {test.unit}")
    
    # 5. Get tests by category
    print("\n=== Lipid Panel Results ===")
    lipid_tests = LabTestAnalyzer.get_tests_by_category(
        patient_key, 
        LabTestCategory.LIPIDS,
        start_date=date.today() - timedelta(days=180)
    )
    for test_name, results in lipid_tests.items():
        latest = results[0] if results else None
        if latest:
            print(f"{test_name}: {latest.value.decrypt()} {latest.unit} ({latest.collection_date})")
    
    # 6. Generate summary report
    print("\n=== Annual Summary Report ===")
    summary = LabTestAnalyzer.generate_summary_report(patient_key, days=365)
    print(f"Period: {summary['period']['start']} to {summary['period']['end']}")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Unique test types: {summary['unique_test_types']}")
    print(f"Abnormal results: {summary['abnormal_count']}")
    
    # Show top 5 most frequent tests
    print("\nMost frequent tests:")
    sorted_tests = sorted(
        summary['test_summaries'].items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )
    for test_name, data in sorted_tests[:5]:
        print(f"  {test_name}: {data['count']} tests, latest: {data['latest_value']} {data['unit']}")


def create_reference_ranges_example():
    """Example of creating test types with reference ranges."""
    from essencia.models import LabTestType, ReferenceRange
    
    # Create Hemoglobin test type with gender-specific ranges
    hemoglobin = LabTestType(
        code="HB",
        name="Hemoglobina",
        category=LabTestCategory.HEMATOLOGY,
        unit="g/dL",
        sample_type="Sangue",
        fasting_required=False,
        turnaround_days=1,
        reference_ranges=[
            ReferenceRange(
                min_value=13.5,
                max_value=17.5,
                unit="g/dL",
                gender="M",
                notes="Valores de referência para homens adultos"
            ),
            ReferenceRange(
                min_value=12.0,
                max_value=15.5,
                unit="g/dL",
                gender="F",
                notes="Valores de referência para mulheres adultas"
            ),
            ReferenceRange(
                min_value=11.0,
                max_value=16.0,
                unit="g/dL",
                age_min=2,
                age_max=12,
                notes="Valores de referência para crianças"
            )
        ]
    )
    
    # Save to database
    hemoglobin = hemoglobin.save_self()
    print(f"Created test type: {hemoglobin}")
    
    # Create Glucose test type
    glucose = LabTestType(
        code="GLU",
        name="Glicemia Jejum",
        category=LabTestCategory.GLUCOSE,
        unit="mg/dL",
        sample_type="Sangue",
        fasting_required=True,
        turnaround_days=1,
        reference_ranges=[
            ReferenceRange(
                min_value=70,
                max_value=99,
                unit="mg/dL",
                notes="Valores normais em jejum"
            )
        ]
    )
    
    glucose = glucose.save_self()
    print(f"Created test type: {glucose}")


if __name__ == "__main__":
    # Run examples
    print("Laboratory Test Data Examples\n")
    
    # Note: These examples assume you have:
    # 1. MongoDB connection configured
    # 2. A patient record with key "patient_123"
    # 3. A CSV file named "lab.csv" in the current directory
    
    # Uncomment to run:
    # create_reference_ranges_example()
    # import_lab_data_example()
    # analyze_lab_data_example()
    
    print("\nNote: Uncomment the function calls above to run the examples")