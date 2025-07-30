"""Tests for the Supplement Splitter enhancement."""

import pytest
from pathlib import Path
import pandas as pd

from scripts.enhancements.supplement_splitter.main import enhancement as splitter
from scriptcraft.common import load_data


def test_supplement_splitter_initialization() -> None:
    """Test supplement splitter initialization."""
    assert splitter.name == "Supplement Splitter"
    assert isinstance(splitter.root, Path)
    assert isinstance(splitter.default_supplement_path, Path)
    assert isinstance(splitter.default_output_dir, Path)


def test_supplement_splitter_with_input_data(tmp_path, mocker) -> None:
    """Test supplement splitter with pre-loaded input data."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'},
        'domain2': {'dictionary': tmp_path / 'domain2'}
    }
    mocker.patch('scripts.enhancements.supplement_splitter.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create test data
    supplement_df = pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Value': ['A', 'B', 'C', 'D'],
        'Domain': ['domain1', 'domain1', 'domain2', 'domain2']
    })
    
    # Create mock cleaned dictionaries
    for domain in ['domain1', 'domain2']:
        domain_dir = tmp_path / domain
        domain_dir.mkdir(exist_ok=True)
        dict_df = pd.DataFrame({'ID': [1, 2], 'Value': ['X', 'Y']})
        dict_path = domain_dir / "cleaned_dictionary.xlsx"
        dict_df.to_excel(dict_path, index=False)
    
    output_dir = tmp_path / "split_supplements"
    output_dir.mkdir(exist_ok=True)
    
    # Run enhancement
    result = splitter.enhance(
        input_data=supplement_df,
        kwargs={
            'output_dir': output_dir
        }
    )
    
    # Verify results
    assert isinstance(result, dict)
    assert set(result.keys()) == {'domain1', 'domain2'}
    assert all(isinstance(df, pd.DataFrame) for df in result.values())
    
    # Verify output files
    for domain in ['domain1', 'domain2']:
        output_path = output_dir / f"{domain}_supplement.xlsx"
        assert output_path.exists()
        output_df = load_data(output_path)
        pd.testing.assert_frame_equal(output_df, result[domain])


def test_supplement_splitter_missing_supplement() -> None:
    """Test supplement splitter with missing supplement file."""
    with pytest.raises(FileNotFoundError):
        splitter.enhance(
            kwargs={
                'supplement_path': Path('nonexistent.xlsx')
            }
        )


def test_supplement_splitter_invalid_input() -> None:
    """Test supplement splitter with invalid input data."""
    with pytest.raises(ValueError):
        splitter.enhance(input_data=pd.DataFrame())  # Empty DataFrame


def test_supplement_splitter_specific_domains(tmp_path, mocker) -> None:
    """Test supplement splitter with specific domain filtering."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'},
        'domain2': {'dictionary': tmp_path / 'domain2'},
        'domain3': {'dictionary': tmp_path / 'domain3'}
    }
    mocker.patch('scripts.enhancements.supplement_splitter.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create test data
    supplement_df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5, 6],
        'Value': ['A', 'B', 'C', 'D', 'E', 'F'],
        'Domain': ['domain1', 'domain1', 'domain2', 'domain2', 'domain3', 'domain3']
    })
    
    # Create mock cleaned dictionaries
    for domain in ['domain1', 'domain2', 'domain3']:
        domain_dir = tmp_path / domain
        domain_dir.mkdir(exist_ok=True)
        dict_df = pd.DataFrame({'ID': [1, 2], 'Value': ['X', 'Y']})
        dict_path = domain_dir / "cleaned_dictionary.xlsx"
        dict_df.to_excel(dict_path, index=False)
    
    output_dir = tmp_path / "split_supplements"
    output_dir.mkdir(exist_ok=True)
    
    # Run enhancement with specific domains
    result = splitter.enhance(
        input_data=supplement_df,
        kwargs={
            'output_dir': output_dir,
            'domains': ['domain1', 'domain3']
        }
    )
    
    # Verify results
    assert isinstance(result, dict)
    assert set(result.keys()) == {'domain1', 'domain3'}
    assert 'domain2' not in result 