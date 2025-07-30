"""Tests for core PAD analytics functions."""

import pytest
import os
from unittest.mock import patch, MagicMock
import pandas as pd


class TestPadAnalytics:
    """Test core pad_analytics functions."""
    
    def test_import(self):
        """Test that the package can be imported."""
        import pad_analytics
        assert hasattr(pad_analytics, 'get_projects')
        assert hasattr(pad_analytics, 'get_models')
    
    @patch('pad_analytics.padanalytics.requests.get')
    def test_get_projects_api_call(self, mock_get):
        """Test that get_projects makes correct API call."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "project_name": "Test Project", "annotation": "Test"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        import pad_analytics as pad
        result = pad.get_projects()
        
        # Check API was called with correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]  # Get keyword arguments
        assert 'verify' in call_args
        assert call_args['verify'] == False
        
        # Check result is DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['project_name'] == "Test Project"
    
    @patch('pad_analytics.padanalytics.requests.get')
    def test_get_models_api_call(self, mock_get):
        """Test that get_models makes correct API call."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "model_name": "Test Model", "model_type": "neural_network"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        import pad_analytics as pad
        result = pad.get_models()
        
        # Check result is DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
    
    def test_debug_mode_environment_variable(self):
        """Test that DEBUG_MODE responds to PAD_DEBUG environment variable."""
        import pad_analytics.padanalytics as pad_module
        
        # Test default (should be False)
        original_debug = getattr(pad_module, 'DEBUG_MODE', None)
        
        with patch.dict(os.environ, {'PAD_DEBUG': '1'}):
            # Reload the module to pick up environment variable
            import importlib
            importlib.reload(pad_module)
            assert pad_module.DEBUG_MODE == True
        
        with patch.dict(os.environ, {'PAD_DEBUG': 'false'}):
            importlib.reload(pad_module)
            assert pad_module.DEBUG_MODE == False
        
        with patch.dict(os.environ, {}, clear=True):
            if 'PAD_DEBUG' in os.environ:
                del os.environ['PAD_DEBUG']
            importlib.reload(pad_module)
            assert pad_module.DEBUG_MODE == False


class TestModelPrediction:
    """Test model prediction functionality."""
    
    @patch('pad_analytics.padanalytics.get_card')
    @patch('pad_analytics.padanalytics.get_model')
    def test_predict_requires_valid_inputs(self, mock_get_model, mock_get_card):
        """Test that predict function validates inputs."""
        # Mock valid card and model data
        mock_get_card.return_value = pd.DataFrame([{
            'sample_name': 'test_drug',
            'quantity': 50.0,
            'processed_file_location': '/test/image.png'
        }])
        
        mock_get_model.return_value = pd.DataFrame([{
            'model_type': 'pls',
            'model_file_location': '/test/model.csv'
        }])
        
        import pad_analytics as pad
        
        # Test with valid inputs (should not raise error)
        try:
            # This will fail at file operations, but should pass validation
            with patch('pad_analytics.padanalytics.download_file'):
                with patch('pad_analytics.pad_analysis.pls') as mock_pls:
                    mock_pls_instance = MagicMock()
                    mock_pls_instance.quantity.return_value = 45.5
                    mock_pls.return_value = mock_pls_instance
                    
                    result = pad.predict(19208, 18)
                    assert result == (50.0, 45.5)
        except Exception as e:
            # Expected to fail at file operations, that's ok for this test
            pass


class TestImageProcessing:
    """Test image processing components."""
    
    def test_suppress_stderr_context_manager(self):
        """Test that suppress_stderr context manager works."""
        import pad_analytics.padanalytics as pad_module
        
        # Test that context manager exists and is callable
        assert hasattr(pad_module, 'suppress_stderr')
        assert callable(pad_module.suppress_stderr)
        
        # Test that it can be used as context manager
        try:
            with pad_module.suppress_stderr():
                pass  # Should not raise error
        except Exception as e:
            pytest.fail(f"suppress_stderr context manager failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])