"""
Test pipeline utilities functionality.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from scriptcraft.common.pipeline import (
    make_step,
    validate_pipelines,
    add_supplement_steps,
    run_qc_for_each_domain,
    run_qc_for_single_domain,
    run_qc_single_step,
    run_global_tool,
    run_pipeline_from_steps,
    timed_pipeline,
    list_pipelines,
    preview_pipeline,
    run_pipeline,
    BasePipeline,
    PipelineStep
)


def test_add_supplement_steps() -> None:
    """Test adding supplement steps to pipeline."""
    pipeline = BasePipeline("test")
    
    # Test adding prepper only
    add_supplement_steps(pipeline, prepare=True, merge=False)
    assert len(pipeline.steps) == 1
    assert pipeline.steps[0].name == "Supplement Prepper"
    
    # Test adding both steps
    pipeline = BasePipeline("test")
    add_supplement_steps(pipeline, prepare=True, merge=True)
    assert len(pipeline.steps) == 2
    assert pipeline.steps[0].name == "Supplement Prepper"
    assert pipeline.steps[1].name == "Supplement Splitter"
    
    # Test adding neither step
    pipeline = BasePipeline("test")
    add_supplement_steps(pipeline, prepare=False, merge=False)
    assert len(pipeline.steps) == 0


def test_run_global_tool(tmp_path) -> None:
    """Test running a global tool."""
    mock_func = Mock()
    
    # Mock config and paths
    mock_config = {"tool_input_file": "test.xlsx"}
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    with patch('scripts.pipelines.pipeline_utils.cu.get_config', return_value=mock_config), \
         patch('scripts.pipelines.pipeline_utils.cu.get_input_dir', return_value=input_dir), \
         patch('scripts.pipelines.pipeline_utils.cu.get_output_dir', return_value=output_dir):
        
        # Test with tool name
        run_global_tool(mock_func, tool_name="test_tool")
        mock_func.assert_called_once()
        args = mock_func.call_args[1]
        assert args["input_path"] == input_dir / "test.xlsx"
        assert args["output_path"] == output_dir
        assert args["config"] == mock_config
        
        # Test without tool name
        mock_func.reset_mock()
        run_global_tool(mock_func)
        mock_func.assert_called_once()
        args = mock_func.call_args[1]
        assert args["input_path"] == input_dir
        assert args["output_path"] == output_dir


def test_parse_args() -> None:
    """Test command line argument parsing."""
    # Test default arguments
    with patch('sys.argv', ['script.py']):
        args = parse_args()
        assert args.pipeline == "test"
        assert not args.time
        assert not args.prepare_supplement
        assert not args.merge_supplement
        assert not args.list
        assert not args.dry_run
        assert args.tag is None
        assert args.domain is None
        assert args.tool is None
        assert args.mode is None
    
    # Test custom arguments
    with patch('sys.argv', [
        'script.py',
        '--pipeline=custom',
        '--time',
        '--prepare-supplement',
        '--merge-supplement',
        '--list',
        '--dry-run',
        '--tag=test',
        '--domain=domain1',
        '--tool=comparer',
        '--mode=standard'
    ]):
        args = parse_args()
        assert args.pipeline == "custom"
        assert args.time
        assert args.prepare_supplement
        assert args.merge_supplement
        assert args.list
        assert args.dry_run
        assert args.tag == "test"
        assert args.domain == "domain1"
        assert args.tool == "comparer"
        assert args.mode == "standard"


def test_list_pipelines(caplog) -> None:
    """Test pipeline listing functionality."""
    pipelines = {
        "test": BasePipeline(
            name="test",
            description="Test pipeline"
        ),
        "prod": BasePipeline(
            name="prod",
            description="Production pipeline"
        )
    }
    
    # Add some steps
    step = PipelineStep(
        name="test_step",
        log_filename="test.log",
        qc_func=lambda: None,
        input_key="raw_data",
        tags=["test"]
    )
    pipelines["test"].add_step(step)
    
    list_pipelines(pipelines)
    
    assert "📋 Available Pipelines:" in caplog.text
    assert "🔷 test" in caplog.text
    assert "📝 Test pipeline" in caplog.text
    assert "🔷 prod" in caplog.text
    assert "📝 Production pipeline" in caplog.text
    assert "test_step [test]" in caplog.text


def test_preview_pipeline(caplog) -> None:
    """Test pipeline preview functionality."""
    pipeline = BasePipeline("test", "Test pipeline")
    step = PipelineStep(
        name="test_step",
        log_filename="test.log",
        qc_func=lambda: None,
        input_key="raw_data",
        output_filename="output.xlsx",
        tags=["test"]
    )
    pipeline.add_step(step)
    
    preview_pipeline(pipeline)
    
    assert "🔍 Preview of test pipeline" in caplog.text
    assert "📝 Test pipeline" in caplog.text
    assert "1. test_step [test]" in caplog.text
    assert "Mode: domain" in caplog.text
    assert "Input: raw_data" in caplog.text
    assert "Output: output.xlsx" in caplog.text


def test_run_pipeline() -> None:
    """Test pipeline running functionality."""
    pipeline = BasePipeline("test")
    mock_func = Mock()
    step = PipelineStep(
        name="test_step",
        log_filename="test.log",
        qc_func=mock_func,
        input_key="raw_data"
    )
    pipeline.add_step(step)
    
    # Test dry run
    args = argparse.Namespace(
        dry_run=True,
        prepare_supplement=False,
        merge_supplement=False,
        tag=None,
        domain=None,
        time=False
    )
    with patch('scripts.pipelines.pipeline_utils.preview_pipeline') as mock_preview:
        run_pipeline(pipeline, args)
        mock_preview.assert_called_once()
        mock_func.assert_not_called()
    
    # Test normal run
    args.dry_run = False
    run_pipeline(pipeline, args)
    mock_func.assert_called_once()
    
    # Test with supplements
    args.prepare_supplement = True
    args.merge_supplement = True
    pipeline = BasePipeline("test")
    run_pipeline(pipeline, args)
    assert len(pipeline.steps) == 2  # Should have added supplement steps 