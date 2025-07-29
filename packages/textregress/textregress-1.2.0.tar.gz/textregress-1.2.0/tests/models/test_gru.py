"""
Tests for the GRU text regression model.
"""

import pytest
import torch
from textregress.models import get_model

@pytest.fixture
def model():
    """Create a GRU model instance for testing."""
    return get_model("gru")(
        encoder_output_dim=768,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64
    )

def test_gru_forward_shape(model):
    """Test that the forward pass produces the expected output shape."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    # Test without exogenous features
    x = torch.randn(batch_size, seq_len, input_dim)
    output = model(x)
    assert output.shape == (batch_size, 1)
    
    # Test with exogenous features
    exo_dim = 5
    exogenous = torch.randn(batch_size, exo_dim)
    model = get_model("gru")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        exogenous_features=["f1", "f2", "f3", "f4", "f5"]
    )
    output = model(x, exogenous)
    assert output.shape == (batch_size, 1)

def test_gru_cross_attention(model):
    """Test that cross attention works correctly."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    exo_dim = 5
    
    # Create model with cross attention
    model = get_model("gru")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        exogenous_features=["f1", "f2", "f3", "f4", "f5"],
        cross_attention_enabled=True
    )
    
    x = torch.randn(batch_size, seq_len, input_dim)
    exogenous = torch.randn(batch_size, exo_dim)
    output = model(x, exogenous)
    assert output.shape == (batch_size, 1)

def test_gru_feature_mixer(model):
    """Test that feature mixing works correctly."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    exo_dim = 5
    
    # Create model with feature mixing
    model = get_model("gru")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        exogenous_features=["f1", "f2", "f3", "f4", "f5"],
        feature_mixer=True
    )
    
    x = torch.randn(batch_size, seq_len, input_dim)
    exogenous = torch.randn(batch_size, exo_dim)
    output = model(x, exogenous)
    assert output.shape == (batch_size, 1)

def test_gru_se_layer(model):
    """Test that the squeeze-and-excitation layer works correctly."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    # Create model with SE layer
    model = get_model("gru")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        se_layer=True
    )
    
    x = torch.randn(batch_size, seq_len, input_dim)
    output = model(x)
    assert output.shape == (batch_size, 1) 