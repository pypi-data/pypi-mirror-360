"""
Test base pipeline functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from scriptcraft.common.pipeline import BasePipeline, PipelineStep


def test_pipeline_initialization() -> None:
    """Test pipeline initialization."""
    pipeline = BasePipeline("test", "Test pipeline")
    assert pipeline.name == "test"
    assert pipeline.description == "Test pipeline"
    assert isinstance(pipeline.steps, list)
    assert len(pipeline.steps) == 0
    assert isinstance(pipeline.root, Path)


def test_pipeline_step_validation() -> None:
    """Test pipeline step validation."""
    # Valid step
    valid_step = PipelineStep(
        name="test",
        log_filename="test.log",
        qc_func=lambda: None,
        input_key="raw_data",
        run_mode="domain"
    )
    assert valid_step.tags == []
    
    # Test run mode validation warnings
    with patch('scriptcraft.common.log_and_print') as mock_log:
        # Domain mode with global input
        PipelineStep(
            name="test",
            log_filename="test.log",
            qc_func=lambda: None,
            input_key="rhq_inputs",
            run_mode="domain"
        )
        mock_log.assert_called_with("⚠️ Warning: Step 'test' uses domain mode with global input_key 'rhq_inputs'.")
        
        # Single domain mode with non-domain input
        PipelineStep(
            name="test",
            log_filename="test.log",
            qc_func=lambda: None,
            input_key="rhq_inputs",
            run_mode="single_domain"
        )
        mock_log.assert_called_with("⚠️ Warning: Step 'test' uses single_domain mode with possible mismatch input_key 'rhq_inputs'.")


def test_pipeline_step_management() -> None:
    """Test adding and managing pipeline steps."""
    pipeline = BasePipeline("test")
    step1 = PipelineStep("step1", "log1.log", lambda: None, "raw_data")
    step2 = PipelineStep("step2", "log2.log", lambda: None, "raw_data")
    
    # Test adding steps
    pipeline.add_step(step1)
    assert len(pipeline.steps) == 1
    assert pipeline.steps[0].name == "step1"
    
    # Test inserting steps
    pipeline.insert_step(0, step2)
    assert len(pipeline.steps) == 2
    assert pipeline.steps[0].name == "step2"
    
    # Test getting steps with tag filter
    step3 = PipelineStep("step3", "log3.log", lambda: None, "raw_data", tags=["test_tag"])
    pipeline.add_step(step3)
    
    filtered_steps = pipeline.get_steps(tag_filter="test_tag")
    assert len(filtered_steps) == 1
    assert filtered_steps[0].name == "step3"


def test_pipeline_validation() -> None:
    """Test pipeline validation."""
    pipeline = BasePipeline("test")
    
    # Empty pipeline
    assert not pipeline.validate()
    
    # Invalid step (no callable)
    invalid_step = PipelineStep("invalid", "log.log", None, "raw_data")
    pipeline.add_step(invalid_step)
    assert not pipeline.validate()
    
    # Valid step
    valid_step = PipelineStep("valid", "log.log", lambda: None, "raw_data")
    pipeline = BasePipeline("test")
    pipeline.add_step(valid_step)
    assert pipeline.validate()


def test_pipeline_execution(tmp_path) -> None:
    """Test pipeline execution."""
    pipeline = BasePipeline("test")
    mock_func = Mock()
    
    # Create test domain structure
    domain_dir = tmp_path / "domain1"
    domain_dir.mkdir(parents=True)
    (domain_dir / "raw_data").mkdir()
    (domain_dir / "qc_output").mkdir()
    
    # Mock domain paths
    mock_paths = {
        "domain1": {
            "raw_data": domain_dir / "raw_data",
            "qc_output": domain_dir / "qc_output"
        }
    }
    
    with patch('scriptcraft.common.get_domain_paths', return_value=mock_paths):
        # Test domain mode
        domain_step = PipelineStep(
            "domain_test",
            "test.log",
            mock_func,
            "raw_data",
            run_mode="domain"
        )
        pipeline.add_step(domain_step)
        pipeline.run()
        mock_func.assert_called_once()
        
        # Test single domain mode
        mock_func.reset_mock()
        single_domain_step = PipelineStep(
            "single_domain_test",
            "test.log",
            mock_func,
            "raw_data",
            run_mode="single_domain"
        )
        pipeline = BasePipeline("test")
        pipeline.add_step(single_domain_step)
        pipeline.run(domain="domain1")
        mock_func.assert_called_once()
        
        # Test global mode
        mock_func.reset_mock()
        global_step = PipelineStep(
            "global_test",
            "test.log",
            mock_func,
            "global_data",
            run_mode="global"
        )
        pipeline = BasePipeline("test")
        pipeline.add_step(global_step)
        pipeline.run()
        mock_func.assert_called_once()


def test_pipeline_error_handling(caplog) -> None:
    """Test pipeline error handling and logging."""
    pipeline = BasePipeline("test")
    
    # Step that raises an exception
    def failing_func():
        raise ValueError("Test error")
    
    error_step = PipelineStep(
        "error_test",
        "test.log",
        failing_func,
        "raw_data",
        run_mode="global"
    )
    pipeline.add_step(error_step)
    
    # Run pipeline and check error handling
    pipeline.run()
    assert "❌ Error in error_test" in caplog.text
    assert "Test error" in caplog.text
    
    # Check timing information
    pipeline.print_summary()
    assert "🧾 Step Timing Summary:" in caplog.text
    assert "error_test" in caplog.text 