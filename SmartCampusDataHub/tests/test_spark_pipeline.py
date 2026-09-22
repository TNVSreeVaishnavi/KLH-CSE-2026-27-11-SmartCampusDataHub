from pathlib import Path

from processing.spark.pipeline import process_dataset


def test_students_pipeline_counts_and_outputs():
    result = process_dataset('students', output_root='data/lake')

    assert result['dataset'] == 'students'
    assert result['input_records'] == 7
    assert result['cleaned_records'] == 7
    assert result['valid_records'] == 6
    assert result['rejected_records'] == 1
    assert result['output_records'] == 6
    assert result['pipeline_status'] == 'COMPLETED'

    lake_root = Path(result['lake_root'])
    bronze = Path(result['bronze_path'])
    silver = Path(result['silver_path'])
    gold = Path(result['gold_path'])

    assert lake_root.exists()
    assert bronze.exists()
    assert silver.exists()
    assert gold.exists()
