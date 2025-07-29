"""
Tests for embedding retrieval functionality.
"""

import pytest
import torch
from textregress.models import get_model


@pytest.fixture
def lstm_model():
    """Create an LSTM model instance for testing."""
    return get_model("lstm")(
        encoder_output_dim=768,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64
    )


@pytest.fixture
def gru_model():
    """Create a GRU model instance for testing."""
    return get_model("gru")(
        encoder_output_dim=768,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64
    )


def test_sequence_embeddings_lstm(lstm_model):
    """Test sequence embedding retrieval for LSTM model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    sequence_embeddings = lstm_model.get_sequence_embeddings(x)
    
    # LSTM with bidirectional=True, hidden_size=128
    expected_dim = 128 * 2  # bidirectional
    assert sequence_embeddings.shape == (batch_size, seq_len, expected_dim)


def test_sequence_embeddings_gru(gru_model):
    """Test sequence embedding retrieval for GRU model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    sequence_embeddings = gru_model.get_sequence_embeddings(x)
    
    # GRU with bidirectional=True, hidden_size=128
    expected_dim = 128 * 2  # bidirectional
    assert sequence_embeddings.shape == (batch_size, seq_len, expected_dim)


def test_document_embeddings_lstm(lstm_model):
    """Test document embedding retrieval for LSTM model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    document_embeddings = lstm_model.get_document_embedding(x)
    
    # inference_layer_units=64
    assert document_embeddings.shape == (batch_size, 64)


def test_document_embeddings_gru(gru_model):
    """Test document embedding retrieval for GRU model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    document_embeddings = gru_model.get_document_embedding(x)
    
    # inference_layer_units=64
    assert document_embeddings.shape == (batch_size, 64)


def test_document_embeddings_with_exogenous_lstm(lstm_model):
    """Test document embedding retrieval with exogenous features for LSTM model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    exo_dim = 5
    
    # Create model with exogenous features
    model = get_model("lstm")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        exogenous_features=["f1", "f2", "f3", "f4", "f5"]
    )
    
    x = torch.randn(batch_size, seq_len, input_dim)
    exogenous = torch.randn(batch_size, exo_dim)
    document_embeddings = model.get_document_embedding(x, exogenous)
    
    assert document_embeddings.shape == (batch_size, 64)


def test_document_embeddings_with_exogenous_gru(gru_model):
    """Test document embedding retrieval with exogenous features for GRU model."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    exo_dim = 5
    
    # Create model with exogenous features
    model = get_model("gru")(
        encoder_output_dim=input_dim,
        hidden_size=128,
        rnn_layers=1,
        inference_layer_units=64,
        exogenous_features=["f1", "f2", "f3", "f4", "f5"]
    )
    
    x = torch.randn(batch_size, seq_len, input_dim)
    exogenous = torch.randn(batch_size, exo_dim)
    document_embeddings = model.get_document_embedding(x, exogenous)
    
    assert document_embeddings.shape == (batch_size, 64)


def test_embedding_consistency_lstm(lstm_model):
    """Test that embeddings are consistent between forward pass and retrieval."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    
    # Get embeddings through retrieval methods
    sequence_embeddings = lstm_model.get_sequence_embeddings(x)
    document_embeddings = lstm_model.get_document_embedding(x)
    
    # Get embeddings through forward pass (by temporarily removing regressor)
    original_regressor = lstm_model.regressor
    lstm_model.regressor = torch.nn.Identity()
    forward_output = lstm_model(x)
    lstm_model.regressor = original_regressor
    
    # Document embeddings should be the same
    torch.testing.assert_close(document_embeddings, forward_output.squeeze(-1))


def test_embedding_consistency_gru(gru_model):
    """Test that embeddings are consistent between forward pass and retrieval."""
    batch_size = 4
    seq_len = 10
    input_dim = 768
    
    x = torch.randn(batch_size, seq_len, input_dim)
    
    # Get embeddings through retrieval methods
    sequence_embeddings = gru_model.get_sequence_embeddings(x)
    document_embeddings = gru_model.get_document_embedding(x)
    
    # Get embeddings through forward pass (by temporarily removing regressor)
    original_regressor = gru_model.regressor
    gru_model.regressor = torch.nn.Identity()
    forward_output = gru_model(x)
    gru_model.regressor = original_regressor
    
    # Document embeddings should be the same
    torch.testing.assert_close(document_embeddings, forward_output.squeeze(-1)) 