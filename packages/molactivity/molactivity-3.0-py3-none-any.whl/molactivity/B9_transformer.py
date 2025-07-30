import numpy as np
from .B16_tensor import Tensor
from .B4_dropout import Dropout
from .B1_activations import ReLU, GELU
from .B8_layers import Linear
from .B7_module import Module, ModuleList
from .B12_normalization import LayerNorm
from . import B13_operations as operations_T  
import math


class AttentionMechanism(Module):
    def __init__(self, embedding_size, head_count):
        super(AttentionMechanism, self).__init__()
        self.embedding_size = embedding_size
        self.head_count = head_count
        self.per_head_dim = embedding_size // head_count
        assert self.per_head_dim * head_count == embedding_size, "Embedding size must divide evenly by head count"
        self.query_key_value = Linear(embedding_size, 3 * embedding_size)
        self.output_projection = Linear(embedding_size, embedding_size)
        self.mask = None
        self.dropout = Dropout(0.1)

    def forward(self, x):

        batch_size, seq_len, d_model = x.shape
        
        qkv = self.query_key_value(x)  # (batch_size, seq_len, 3*d_model)
        
        q = qkv[:, :, :self.embedding_size]
        k = qkv[:, :, self.embedding_size:2*self.embedding_size]
        v = qkv[:, :, 2*self.embedding_size:]
        
        q = operations_T.reshape(q, (batch_size, seq_len, self.head_count, self.per_head_dim))
        k = operations_T.reshape(k, (batch_size, seq_len, self.head_count, self.per_head_dim))
        v = operations_T.reshape(v, (batch_size, seq_len, self.head_count, self.per_head_dim))
        
        q = operations_T.transpose(q, (0, 2, 1, 3))
        k = operations_T.transpose(k, (0, 2, 1, 3))
        v = operations_T.transpose(v, (0, 2, 1, 3))
        
        k_transposed = operations_T.transpose(k, (0, 1, 3, 2))  
        scores = operations_T.matmul(q, k_transposed)
        
        scaling_factor = Tensor(np.array(1.0 / math.sqrt(self.per_head_dim)))
        scores = operations_T.mul(scores, scaling_factor)
        
        if self.mask is not None:
            scores = operations_T.add(scores, self.mask)
            
        attention_weights = operations_T.softmax(scores, dim=-1)
        
        attention_weights = self.dropout(attention_weights)
        
        output = operations_T.matmul(attention_weights, v)
        
        output = operations_T.transpose(output, (0, 2, 1, 3))
        output = operations_T.reshape(output, (batch_size, seq_len, self.embedding_size))
        
        output = self.output_projection(output)
        
        return output

class TransformerBlock(Module):
    def __init__(self, embedding_size, head_count, hidden_size, dropout_rate, activation='gelu'):
        super(TransformerBlock, self).__init__()
        self.attention = AttentionMechanism(embedding_size, head_count)
        self.linear1 = Linear(embedding_size, hidden_size)
        
        if activation.lower() == 'relu':
            self.activation = ReLU()
        elif activation.lower() == 'gelu':
            self.activation = GELU()
        else:
            raise ValueError
        
        self.linear2 = Linear(hidden_size, embedding_size)
        self.dropout1 = Dropout(dropout_rate)
        self.normalization1 = LayerNorm(embedding_size)
        self.normalization2 = LayerNorm(embedding_size)
        self.dropout2 = Dropout(dropout_rate)

    def forward(self, x):
   
        if len(x.shape) == 2:
            batch_size, features = x.shape
            x = operations_T.reshape(x, (batch_size, 1, features))
        
        batch_size, seq_len, features = x.shape
        
        residual = x
        x = self.normalization1(x)
        x = self.attention(x)
        x = self.dropout1(x)
        x = operations_T.add(residual, x) 
        
        residual = x
        x = self.normalization2(x)
        
        x_flat = operations_T.reshape(x, (-1, features))
        x_flat = self.linear1(x_flat)
        x_flat = self.activation(x_flat)
        x_flat = self.linear2(x_flat)
        
        x = operations_T.reshape(x_flat, (batch_size, seq_len, features))
        
        x = self.dropout2(x)
        x = operations_T.add(residual, x)  
        
        return x

class TransformerStack(Module):
    def __init__(self, embedding_size, layer_count, head_count, hidden_size, dropout_rate, activation='gelu'):
        super(TransformerStack, self).__init__()
        self.layers = ModuleList([
            TransformerBlock(embedding_size, head_count, hidden_size, dropout_rate, activation)
            for _ in range(layer_count)
        ])
        self.final_normalization = LayerNorm(embedding_size)

    def forward(self, x):
            
        for layer in self.layers:
            x = layer(x)
            
        x = self.final_normalization(x)
        return x

class MolecularTransformer(Module):
    def __init__(self, input_features, output_features, embedding_size, layer_count, head_count, hidden_size, dropout_rate, activation='gelu'):
        super(MolecularTransformer, self).__init__()
        self.embedding_size = embedding_size
        self.activation_type = activation 
        self.feature_embedding = Linear(input_features, embedding_size)
        self.transformer = TransformerStack(embedding_size, layer_count, head_count, hidden_size, dropout_rate, activation)
        self.output_layer = Linear(embedding_size, output_features)
        
    def forward(self, x):
            
        x = self.feature_embedding(x)
        x = self.transformer(x)
        
        x_pooled = operations_T.mean(x, dim=1) 
        
        x_pooled = self.output_layer(x_pooled)
        return x_pooled