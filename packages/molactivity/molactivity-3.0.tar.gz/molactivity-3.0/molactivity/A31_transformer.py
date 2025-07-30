from . import A2_arrays as arrays
from .A26_tensor import Tensor
from .A8_dropout import Dropout
from .A1_activations import ReLU, GELU
from .A12_layers import Linear
from .A15_module import Module, ModuleList
from .A17_normalization import LayerNorm
from . import A16_operations as operations
from . import A20_math as math


class AttentionMechanism(Module):
    def __init__(self, embedding_size, head_count):
        super(AttentionMechanism, self).__init__()
        self.embedding_size = embedding_size
        self.head_count = head_count
        self.per_head_dim = embedding_size // head_count
        assert self.per_head_dim * head_count == embedding_size
        self.query_key_value = Linear(embedding_size, 3 * embedding_size)
        self.output_projection = Linear(embedding_size, embedding_size)
        self.mask = None
        self.dropout = Dropout(0.1)

    def forward(self, x):
        if not isinstance(x, Tensor):
            x = Tensor(x)
        
        if hasattr(x, 'shape') and len(x.shape) == 1:
   
            total_size = x.shape[0]
            if total_size == self.embedding_size:
                x = operations.reshape(x, (1, 1, self.embedding_size))
            elif total_size % self.embedding_size == 0:
                batch_size = total_size // self.embedding_size
                x = operations.reshape(x, (batch_size, 1, self.embedding_size))
            
        if not hasattr(x, 'shape') or len(x.shape) == 0:
            raise ValueError
        if len(x.shape) == 3:
            batch_size, seq_len, d_model = x.shape
        elif len(x.shape) == 2:
            batch_size, d_model = x.shape
            seq_len = 1
            x = operations.reshape(x, (batch_size, seq_len, d_model))
            batch_size, seq_len, d_model = x.shape
        else:
            raise ValueError
        
        qkv = self.query_key_value(x)  
    
        q = qkv[:, :, :self.embedding_size]
        k = qkv[:, :, self.embedding_size:2*self.embedding_size]
        v = qkv[:, :, 2*self.embedding_size:]
        
        q = operations.reshape(q, (batch_size, seq_len, self.head_count, self.per_head_dim))
        k = operations.reshape(k, (batch_size, seq_len, self.head_count, self.per_head_dim))
        v = operations.reshape(v, (batch_size, seq_len, self.head_count, self.per_head_dim))
        
        q = operations.transpose(q, (0, 2, 1, 3))
        k = operations.transpose(k, (0, 2, 1, 3))
        v = operations.transpose(v, (0, 2, 1, 3))
        
        k_transposed = operations.transpose(k, (0, 1, 3, 2)) 
        scores = operations.matmul(q, k_transposed)
        
        scaling_factor = Tensor(arrays.array(1.0 / math.sqrt(self.per_head_dim)))
        scores = operations.mul(scores, scaling_factor)
        
        if self.mask is not None:
            scores = operations.add(scores, self.mask)
            
        attention_weights = operations.softmax(scores, dim=-1)
        
        attention_weights = self.dropout(attention_weights)
        
        output = operations.matmul(attention_weights, v)
        
        output = operations.transpose(output, (0, 2, 1, 3))
        
        total_size = 1
        for dim in output.shape:
            total_size *= dim
        actual_seq_len = total_size // (batch_size * self.embedding_size)
        
        output = operations.reshape(output, (batch_size, actual_seq_len, self.embedding_size))
        
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
        if not isinstance(x, Tensor):
            x = Tensor(x)
        
        if len(x.shape) == 2:
            batch_size, features = x.shape
            x = operations.reshape(x, (batch_size, 1, features))
        
        if not hasattr(x, 'shape') or len(x.shape) == 0:
            raise ValueError
        
        if len(x.shape) == 3:
            batch_size, seq_len, features = x.shape
        elif len(x.shape) == 2:
            batch_size, features = x.shape
            seq_len = 1
            x = operations.reshape(x, (batch_size, seq_len, features))
        else:
            raise ValueError
        
        residual = x
        x = self.normalization1(x)
        x = self.attention(x)
        x = self.dropout1(x)
        x = operations.add(residual, x)  
        
        residual = x
        x = self.normalization2(x)
        
        x_flat = operations.reshape(x, (-1, features))
        x_flat = self.linear1(x_flat)
        x_flat = self.activation(x_flat)
        x_flat = self.linear2(x_flat)
        
        actual_batch_seq_size = x_flat.shape[0] if hasattr(x_flat, 'shape') else len(x_flat.data) // features
        if actual_batch_seq_size == batch_size * seq_len:
            x = operations.reshape(x_flat, (batch_size, seq_len, features))
        else:
            total_elements = x_flat.shape[0] * features if hasattr(x_flat, 'shape') else len(x_flat.data)
            if total_elements == batch_size * seq_len * features:
                x = operations.reshape(x_flat, (batch_size, seq_len, features))
            else:
                new_batch_size = total_elements // (seq_len * features)
                if new_batch_size * seq_len * features == total_elements:
                    x = operations.reshape(x_flat, (new_batch_size, seq_len, features))
                else:
                    x = x_flat
                    if len(x.shape) == 2 and x.shape[1] == features:
                        batch_size = x.shape[0] // seq_len
                        if batch_size * seq_len == x.shape[0]:
                            x = operations.reshape(x, (batch_size, seq_len, features))
                        else:
                            x = operations.reshape(x, (x.shape[0], 1, features))
                            batch_size, seq_len, features = x.shape
        
        x = self.dropout2(x)
        x = operations.add(residual, x) 
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
        if not isinstance(x, Tensor):
            x = Tensor(x)
            
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
        if not isinstance(x, Tensor):
            x = Tensor(x)
            
        x = self.feature_embedding(x)
        x = self.transformer(x)

        if hasattr(x, 'shape') and len(x.shape) == 1:
            x_pooled = x
        elif hasattr(x, 'shape') and len(x.shape) == 2:
            x_pooled = x
        elif hasattr(x, 'shape') and len(x.shape) == 3:
            x_pooled = operations.mean(x, dim=1)  
        else:
            x_pooled = x
        
        x_pooled = self.output_layer(x_pooled)
        return x_pooled