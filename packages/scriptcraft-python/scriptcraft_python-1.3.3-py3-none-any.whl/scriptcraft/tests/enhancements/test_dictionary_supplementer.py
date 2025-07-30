"""Tests for the Dictionary Supplementer enhancement."""

import pytest
from pathlib import Path
import pandas as pd

from scripts.enhancements.dictionary_supplementer.main import enhancement as supplementer
from scriptcraft.common import load_data


def test_dictionary_supplementer_initialization() -> None:
    """Test dictionary supplementer initialization."""
    assert supplementer.name == "Dictionary Supplementer"
    assert isinstance(supplementer.root, Path)
    assert isinstance(supplementer.supplement_dir, Path)


def test_dictionary_supplementer_with_input_data(tmp_path, mocker) -> None:
    """Test dictionary supplementer with pre-loaded input data."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'},
        'domain2': {'dictionary': tmp_path / 'domain2'}
    }
    mocker.patch('scripts.enhancements.dictionary_supplementer.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create test dictionaries
    dict_data = {
        'domain1': pd.DataFrame({
            'ID': [1, 2],
            'Value': ['A', 'B']
        }),
        'domain2': pd.DataFrame({
            'ID': [3, 4],
            'Value': ['C', 'D']
        })
    }
    
    # Create test supplements
    supplement_data = {
        'domain1': pd.DataFrame({
            'ID': [1, 2],
            'NewValue': ['X', 'Y']
        }),
        'domain2': pd.DataFrame({
            'ID': [3, 4],
            'NewValue': ['Z', 'W']
        })
    }
    
    # Create directory structure and save files
    for domain in ['domain1', 'domain2']:
        # Create and save dictionary
        domain_dir = tmp_path / domain
        domain_dir.mkdir(exist_ok=True)
        dict_path = domain_dir / "cleaned_dictionary.xlsx"
        dict_data[domain].to_excel(dict_path, index=False)
        
        # Create and save supplement
        supplement_dir = tmp_path / "supplements"
        supplement_dir.mkdir(exist_ok=True)
        supplement_path = supplement_dir / f"{domain}_supplement.xlsx"
        supplement_data[domain].to_excel(supplement_path, index=False)
    
    # Mock supplement directory path
    supplementer.supplement_dir = supplement_dir
    
    # Run enhancement
    result = supplementer.enhance(
        kwargs={
            'update_existing': True,
            'output_dir': tmp_path / "output"
        }
    )
    
    # Verify results
    assert isinstance(result, dict)
    assert set(result.keys()) == {'domain1', 'domain2'}
    assert all(isinstance(df, pd.DataFrame) for df in result.values())
    
    # Verify each domain's output
    for domain in result:
        # Check that output contains both original and new columns
        assert 'Value' in result[domain].columns
        assert 'NewValue' in result[domain].columns
        
        # Verify file was saved
        output_path = tmp_path / "output" / f"{domain}_supplemented_dictionary.xlsx"
        assert output_path.exists()
        
        # Verify saved content matches returned content
        saved_df = load_data(output_path)
        pd.testing.assert_frame_equal(saved_df, result[domain])


def test_dictionary_supplementer_missing_supplements(tmp_path, mocker) -> None:
    """Test dictionary supplementer with missing supplement files."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'}
    }
    mocker.patch('scripts.enhancements.dictionary_supplementer.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create dictionary but no supplement
    domain_dir = tmp_path / 'domain1'
    domain_dir.mkdir(exist_ok=True)
    dict_df = pd.DataFrame({'ID': [1, 2], 'Value': ['A', 'B']})
    dict_path = domain_dir / "cleaned_dictionary.xlsx"
    dict_df.to_excel(dict_path, index=False)
    
    with pytest.raises(ValueError, match="No dictionaries were successfully supplemented"):
        supplementer.enhance()


def test_dictionary_supplementer_specific_domains(tmp_path, mocker) -> None:
    """Test dictionary supplementer with specific domain filtering."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'},
        'domain2': {'dictionary': tmp_path / 'domain2'},
        'domain3': {'dictionary': tmp_path / 'domain3'}
    }
    mocker.patch('scripts.enhancements.dictionary_supplementer.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create test data for all domains
    for domain in ['domain1', 'domain2', 'domain3']:
        # Create dictionary
        domain_dir = tmp_path / domain
        domain_dir.mkdir(exist_ok=True)
        dict_df = pd.DataFrame({'ID': [1, 2], 'Value': ['A', 'B']})
        dict_path = domain_dir / "cleaned_dictionary.xlsx"
        dict_df.to_excel(dict_path, index=False)
        
        # Create supplement
        supplement_dir = tmp_path / "supplements"
        supplement_dir.mkdir(exist_ok=True)
        supplement_df = pd.DataFrame({'ID': [1, 2], 'NewValue': ['X', 'Y']})
        supplement_path = supplement_dir / f"{domain}_supplement.xlsx"
        supplement_df.to_excel(supplement_path, index=False)
    
    # Mock supplement directory path
    supplementer.supplement_dir = supplement_dir
    
    # Run enhancement with specific domains
    result = supplementer.enhance(
        kwargs={
            'domains': ['domain1', 'domain3'],
            'output_dir': tmp_path / "output"
        }
    )
    
    # Verify results
    assert isinstance(result, dict)
    assert set(result.keys()) == {'domain1', 'domain3'}
    assert 'domain2' not in result


def test_dictionary_supplementer_update_existing(tmp_path, mocker) -> None:
    """Test dictionary supplementer with update_existing parameter."""
    # Mock domain paths
    mock_domains = {
        'domain1': {'dictionary': tmp_path / 'domain1'}
    }
    mocker.patch('scripts.enhancements.dictionary_supplementer.main.get_domain_paths',
                 return_value=mock_domains)
    
    # Create test data with overlapping column
    domain_dir = tmp_path / 'domain1'
    domain_dir.mkdir(exist_ok=True)
    
    # Dictionary with existing Value
    dict_df = pd.DataFrame({
        'ID': [1, 2],
        'Value': ['A', 'B']
    })
    dict_path = domain_dir / "cleaned_dictionary.xlsx"
    dict_df.to_excel(dict_path, index=False)
    
    # Supplement with new Value
    supplement_dir = tmp_path / "supplements"
    supplement_dir.mkdir(exist_ok=True)
    supplement_df = pd.DataFrame({
        'ID': [1, 2],
        'Value': ['X', 'Y']  # Same column name as in dictionary
    })
    supplement_path = supplement_dir / "domain1_supplement.xlsx"
    supplement_df.to_excel(supplement_path, index=False)
    
    # Mock supplement directory path
    supplementer.supplement_dir = supplement_dir
    
    # Test with update_existing=False
    result_no_update = supplementer.enhance(
        kwargs={
            'update_existing': False,
            'output_dir': tmp_path / "output_no_update"
        }
    )
    
    # Original values should be preserved
    assert result_no_update['domain1']['Value'].tolist() == ['A', 'B']
    
    # Test with update_existing=True
    result_with_update = supplementer.enhance(
        kwargs={
            'update_existing': True,
            'output_dir': tmp_path / "output_with_update"
        }
    )
    
    # Values should be updated
    assert result_with_update['domain1']['Value'].tolist() == ['X', 'Y'] 