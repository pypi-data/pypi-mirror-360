import torch
import torch.nn as nn
from typing import Optional, Dict, Any, Tuple
from .moe_layer import MoELayer

class MoEModel(nn.Module):
    """
    Main Mixture of Experts model implementation.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_experts: int,
        num_layers: int,
        num_heads: int = 8,
        dropout: float = 0.1,
        expert_dropout: float = 0.1,
        k: int = 2,
        capacity_factor: float = 1.0,
        use_aux_loss: bool = True,
        use_noisy_gate: bool = True
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.k = k

        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.input_norm = nn.LayerNorm(hidden_dim)

        # MoE layers
        self.moe_layers = nn.ModuleList([
            MoELayer(
                input_dim=hidden_dim,
                num_experts=num_experts,
                expert_dim=hidden_dim * 4,  # FFN expansion factor
                k=k,
                capacity_factor=capacity_factor,
                dropout=expert_dropout,
                use_aux_loss=use_aux_loss,
                use_noisy_gate=use_noisy_gate
            ) for _ in range(num_layers)
        ])

        # Layer norms
        self.layer_norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(num_layers)
        ])

        # Output projection
        self.output_proj = nn.Linear(hidden_dim, input_dim)
        self.output_norm = nn.LayerNorm(input_dim)

        # Dropout
        self.dropout = nn.Dropout(dropout)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(
        self,
        x: torch.Tensor,
        return_aux_loss: bool = False
    ) -> Tuple[torch.Tensor, Optional[Dict[str, torch.Tensor]]]:
        """
        Forward pass through the MoE model.
        
        Args:
            x: Input tensor of shape [batch_size, seq_len, input_dim]
            return_aux_loss: Whether to return auxiliary losses
            
        Returns:
            Tuple of (output tensor, auxiliary losses if requested)
        """
        # Input projection
        x = self.input_proj(x)
        x = self.input_norm(x)
        x = self.dropout(x)

        # Track auxiliary losses
        aux_losses = {}
        total_aux_loss = 0.0

        # Process through MoE layers
        for i, (moe_layer, layer_norm) in enumerate(zip(self.moe_layers, self.layer_norms)):
            # Layer norm
            residual = x
            x = layer_norm(x)

            # MoE layer
            x, aux_loss = moe_layer(x, return_aux_loss)
            if aux_loss is not None:
                aux_losses[f'moe_layer_{i}_aux_loss'] = aux_loss
                total_aux_loss = total_aux_loss + aux_loss

            # Residual connection
            x = residual + x
            x = self.dropout(x)

        # Output projection
        x = self.output_proj(x)
        x = self.output_norm(x)

        if return_aux_loss:
            aux_losses['total_aux_loss'] = total_aux_loss
            return x, aux_losses
        return x, None

    def get_expert_usage(self) -> Dict[int, torch.Tensor]:
        """Get expert usage statistics for all layers."""
        return {
            i: layer.get_expert_usage()
            for i, layer in enumerate(self.moe_layers)
        }

    def reset_expert_usage(self):
        """Reset expert usage statistics for all layers."""
        for layer in self.moe_layers:
            layer.reset_expert_usage()

    def get_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            'input_dim': self.input_dim,
            'hidden_dim': self.hidden_dim,
            'num_experts': self.num_experts,
            'num_layers': self.num_layers,
            'num_heads': self.num_heads,
            'k': self.k,
            'dropout': self.dropout.p,
            'use_aux_loss': self.moe_layers[0].use_aux_loss,
            'use_noisy_gate': self.moe_layers[0].use_noisy_gate
        } 