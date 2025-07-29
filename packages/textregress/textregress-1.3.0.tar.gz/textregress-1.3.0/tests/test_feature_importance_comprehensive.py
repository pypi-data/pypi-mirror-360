"""
Comprehensive tests for feature importance functionality in textregress.

Tests:
- Device handling (auto, manual, CPU, GPU)
- Gradient-based feature importance
- Attention-based feature importance (with cross-attention)
- get_feature_importance() method
- Device state preservation
- Error handling
"""

import unittest
import torch
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from textregress import TextRegressor
from textregress.utils.explainability import get_gradient_importance, get_attention_weights


class TestFeatureImportanceComprehensive(unittest.TestCase):
    """Comprehensive tests for feature importance functionality."""
    
    def setUp(self):
        """Set up test data and basic model."""
        # Create test data
        self.test_data = pd.DataFrame({
            'text': [
                "This is a positive review about the product quality.",
                "The service was excellent and I highly recommend it.",
                "Not satisfied with the purchase experience.",
                "Great value for money and fast delivery."
            ],
            'y': [4.5, 4.8, 2.1, 4.2],
            'feature1': [1.0, 1.2, 0.8, 1.1],
            'feature2': [0.5, 0.6, 0.3, 0.7]
        })
        
        # Create test data without exogenous features
        self.test_data_no_exo = pd.DataFrame({
            'text': [
                "This is a positive review about the product quality.",
                "The service was excellent and I highly recommend it.",
                "Not satisfied with the purchase experience.",
                "Great value for money and fast delivery."
            ],
            'y': [4.5, 4.8, 2.1, 4.2]
        })
        
        # Set random seed for reproducibility
        torch.manual_seed(42)
        np.random.seed(42)
    
    def test_device_handling_auto(self):
        """Test automatic device handling."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="auto"
        )
        
        # Test device setup
        device = regressor.get_device()
        self.assertIsInstance(device, torch.device)
        
        # Test that device is either CPU or CUDA
        self.assertIn(device.type, ['cpu', 'cuda'])
        
        # Fit the model
        regressor.fit(self.test_data, max_steps=10)
        
        # Test that model is on the correct device
        model_device = next(regressor.model.parameters()).device
        self.assertEqual(model_device, device)
    
    def test_device_handling_manual(self):
        """Test manual device handling."""
        # Test CPU device
        regressor_cpu = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        self.assertEqual(regressor_cpu.get_device(), torch.device("cpu"))
        
        # Test changing device
        if torch.cuda.is_available():
            regressor_cpu.set_device("cuda")
            self.assertEqual(regressor_cpu.get_device(), torch.device("cuda"))
        
        # Test changing back to CPU
        regressor_cpu.set_device("cpu")
        self.assertEqual(regressor_cpu.get_device(), torch.device("cpu"))
    
    def test_gradient_importance_basic(self):
        """Test basic gradient importance computation."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features
        
        # Check that importance values are non-negative
        self.assertTrue(np.all(importance['text_importance'] >= 0))
        self.assertTrue(np.all(importance['exogenous_importance'] >= 0))
    
    def test_gradient_importance_no_exogenous(self):
        """Test gradient importance without exogenous features."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data_no_exo, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertNotIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        
        # Check that importance values are non-negative
        self.assertTrue(np.all(importance['text_importance'] >= 0))
    
    def test_attention_importance_with_cross_attention(self):
        """Test attention-based importance with cross-attention enabled."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=True,
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test attention importance
        importance = regressor.get_feature_importance(mode="attention")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        
        # Check that importance values are non-negative
        self.assertTrue(np.all(importance['text_importance'] >= 0))
        self.assertTrue(np.all(importance['exogenous_importance'] >= 0))
    
    def test_attention_importance_without_cross_attention(self):
        """Test that attention mode fails when cross-attention is disabled."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=False,
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test that attention mode raises error
        with self.assertRaises(ValueError):
            regressor.get_feature_importance(mode="attention")
    
    def test_attention_importance_without_exogenous(self):
        """Test that attention mode fails without exogenous features."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data_no_exo, max_steps=10)
        
        # Test that attention mode raises error
        with self.assertRaises(ValueError):
            regressor.get_feature_importance(mode="attention")
    
    def test_get_feature_importance_with_custom_data(self):
        """Test get_feature_importance with custom DataFrame."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Create custom test data
        custom_data = pd.DataFrame({
            'text': [
                "This is a test review for feature importance.",
                "Another test review with different content."
            ],
            'feature1': [1.5, 0.9],
            'feature2': [0.8, 0.4]
        })
        
        # Test with custom data
        importance = regressor.get_feature_importance(df=custom_data, mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes (should match custom data)
        self.assertEqual(importance['text_importance'].shape[0], 2)  # 2 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 2)  # 2 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features
    
    def test_get_feature_importance_without_training_data(self):
        """Test get_feature_importance when no training data is available."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        # Test that it fails when model is not fitted
        with self.assertRaises(ValueError):
            regressor.get_feature_importance()
        
        # Fit the model
        regressor.fit(self.test_data, max_steps=10)
        
        # Test that it works with training data
        importance = regressor.get_feature_importance()
        self.assertIn('text_importance', importance)
    
    def test_invalid_mode(self):
        """Test that invalid mode raises error."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test invalid mode
        with self.assertRaises(ValueError):
            regressor.get_feature_importance(mode="invalid_mode")
    
    def test_device_state_preservation(self):
        """Test that model training state is preserved after feature importance computation."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Set model to eval mode
        regressor.model.eval()
        self.assertFalse(regressor.model.training)
        
        # Compute feature importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check that model is back in eval mode
        self.assertFalse(regressor.model.training)
        
        # Set model to train mode
        regressor.model.train()
        self.assertTrue(regressor.model.training)
        
        # Compute feature importance again
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check that model is back in train mode
        self.assertTrue(regressor.model.training)
    
    def test_gradient_importance_direct_function(self):
        """Test the get_gradient_importance function directly."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Get the actual encoder output dimension from the fitted model
        encoder_output_dim = regressor.model.encoder_output_dim
        
        # Create test tensors with correct dimensions
        x = torch.randn(2, 3, encoder_output_dim)  # batch_size=2, seq_len=3, features=encoder_output_dim
        exogenous = torch.randn(2, 2)  # batch_size=2, features=2
        
        # Test gradient importance
        importance = get_gradient_importance(regressor.model, x, exogenous)
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape, (2, 3))  # batch_size, seq_len
        self.assertEqual(importance['exogenous_importance'].shape, (2, 2))  # batch_size, features
    
    def test_attention_weights_direct_function(self):
        """Test the get_attention_weights function directly."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=True,
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Get the actual encoder output dimension from the fitted model
        encoder_output_dim = regressor.model.encoder_output_dim
        
        # Create test tensors with correct dimensions
        x = torch.randn(2, 3, encoder_output_dim)  # batch_size=2, seq_len=3, features=encoder_output_dim
        exogenous = torch.randn(2, 2)  # batch_size=2, features=2
        
        # Test attention weights
        attention_weights = get_attention_weights(regressor.model, x, exogenous)
        
        # Check that attention weights are returned
        self.assertIsNotNone(attention_weights)
        self.assertIsInstance(attention_weights, torch.Tensor)
    
    def test_attention_weights_without_cross_attention(self):
        """Test that get_attention_weights returns None when cross-attention is disabled."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=False,
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Create test tensors
        x = torch.randn(2, 3, 100)
        exogenous = torch.randn(2, 2)
        
        # Test that attention weights returns None
        attention_weights = get_attention_weights(regressor.model, x, exogenous)
        self.assertIsNone(attention_weights)
    
    def test_gru_model_feature_importance(self):
        """Test feature importance with GRU model."""
        regressor = TextRegressor(
            model_name="gru",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features
    
    def test_sentence_transformer_encoder(self):
        """Test feature importance with sentence transformer encoder."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features
    
    def test_chunked_text_feature_importance(self):
        """Test feature importance with chunked text processing."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            chunk_info=(10, 2),  # chunk_size=10, overlap=2
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features
    
    def test_feature_mixer_feature_importance(self):
        """Test feature importance with feature mixer enabled."""
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            exogenous_features=["feature1", "feature2"],
            feature_mixer=True,
            max_steps=10,
            device="cpu"
        )
        
        regressor.fit(self.test_data, max_steps=10)
        
        # Test gradient importance
        importance = regressor.get_feature_importance(mode="gradient")
        
        # Check structure
        self.assertIn('text_importance', importance)
        self.assertIn('exogenous_importance', importance)
        
        # Check shapes
        self.assertEqual(importance['text_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[0], 4)  # 4 samples
        self.assertEqual(importance['exogenous_importance'].shape[1], 2)  # 2 features


if __name__ == '__main__':
    unittest.main() 