"""
Test pipeline steps and factory functionality.
"""

import pytest
from unittest.mock import patch, Mock

from scriptcraft.common.pipeline import (
    PipelineFactory,
    build_step,
    import_function,
    get_pipeline_steps,
    BasePipeline,
    PipelineStep
)


def test_import_function() -> None:
    """Test dynamic function importing."""
    # Test importing a real function
    func = import_function("scriptcraft.common.get_project_root")
    assert callable(func)
    
    # Test importing nonexistent function
    with pytest.raises(ImportError):
        import_function("nonexistent.module.function")
    
    # Test importing invalid path
    with pytest.raises(ValueError):
        import_function("invalid_path")


def test_build_step() -> None:
    """Test pipeline step building from config."""
    # Test normal step
    step_def = {
        "name": "test_step",
        "log": "test.log",
        "func": "scriptcraft.common.get_project_root",
        "input_key": "raw_data",
        "check_exists": True,
        "run_mode": "domain",
        "tags": ["test"]
    }
    
    step = build_step(step_def)
    assert isinstance(step, PipelineStep)
    assert step.name == "test_step"
    assert step.log_filename == "test.log"
    assert callable(step.qc_func)
    assert step.input_key == "raw_data"
    assert step.check_exists is True
    assert step.run_mode == "domain"
    assert step.tags == ["test"]
    
    # Test data comparer special case
    comparer_def = {
        "name": "data_comparer",
        "log": "comparer.log",
        "func": "scripts.tools.data_content_comparer.main.run_content_comparer"
    }
    
    step = build_step(comparer_def)
    assert isinstance(step, PipelineStep)
    assert step.name == "data_comparer"
    assert callable(step.qc_func)


def test_pipeline_factory() -> None:
    """Test pipeline factory functionality."""
    factory = PipelineFactory()
    
    # Mock config
    mock_config = {
        "pipelines": {
            "test": [
                {
                    "name": "step1",
                    "log": "step1.log",
                    "func": "scripts.common.get_project_root"
                }
            ],
            "composite": [
                {"ref": "test"},
                {
                    "name": "step2",
                    "log": "step2.log",
                    "func": "scripts.common.get_project_root"
                }
            ]
        },
        "pipeline_descriptions": {
            "test": "Test pipeline",
            "composite": "Composite pipeline"
        }
    }
    
    with patch('scripts.pipelines.pipeline_steps.cu.get_config', return_value=mock_config):
        # Create pipelines
        pipelines = factory.create_pipelines()
        
        # Check basic pipeline
        assert "test" in pipelines
        test_pipeline = pipelines["test"]
        assert isinstance(test_pipeline, BasePipeline)
        assert test_pipeline.name == "test"
        assert test_pipeline.description == "Test pipeline"
        assert len(test_pipeline.steps) == 1
        
        # Check composite pipeline
        assert "composite" in pipelines
        composite_pipeline = pipelines["composite"]
        assert isinstance(composite_pipeline, BasePipeline)
        assert composite_pipeline.name == "composite"
        assert composite_pipeline.description == "Composite pipeline"
        assert len(composite_pipeline.steps) == 2


def test_get_pipeline_steps() -> None:
    """Test getting pipeline steps."""
    # Mock config
    mock_config = {
        "pipelines": {
            "test": [
                {
                    "name": "step1",
                    "log": "step1.log",
                    "func": "scripts.common.get_project_root"
                }
            ]
        }
    }
    
    with patch('scripts.pipelines.pipeline_steps.cu.get_config', return_value=mock_config):
        steps = get_pipeline_steps()
        
        assert "test" in steps
        assert isinstance(steps["test"], list)
        assert len(steps["test"]) == 1
        assert isinstance(steps["test"][0], PipelineStep)
        assert steps["test"][0].name == "step1"


def test_pipeline_factory_error_handling() -> None:
    """Test pipeline factory error handling."""
    factory = PipelineFactory()
    
    # Test circular reference
    mock_config = {
        "pipelines": {
            "test1": [{"ref": "test2"}],
            "test2": [{"ref": "test1"}]
        }
    }
    
    with patch('scripts.pipelines.pipeline_steps.cu.get_config', return_value=mock_config):
        pipelines = factory.create_pipelines()
        assert "test1" in pipelines
        assert "test2" in pipelines
        assert len(pipelines["test1"].steps) == 0  # Should handle circular ref gracefully
        assert len(pipelines["test2"].steps) == 0
    
    # Test invalid reference
    mock_config = {
        "pipelines": {
            "test": [{"ref": "nonexistent"}]
        }
    }
    
    with patch('scripts.pipelines.pipeline_steps.cu.get_config', return_value=mock_config):
        pipelines = factory.create_pipelines()
        assert "test" in pipelines
        assert len(pipelines["test"].steps) == 0  # Should handle missing ref gracefully 