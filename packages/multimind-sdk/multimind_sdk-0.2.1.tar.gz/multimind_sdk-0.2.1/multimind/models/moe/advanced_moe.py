import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Tuple
import math
from .moe_layer import MoELayer

class AdvancedMoELayer(MoELayer):
    """
    Advanced MoE layer with additional features:
    - Dynamic expert capacity
    - Expert specialization
    - Adaptive routing
    - Expert pruning
    - Gradient checkpointing
    """
    def __init__(
        self,
        input_dim: int,
        num_experts: int,
        expert_dim: int,
        k: int = 2,
        capacity_factor: float = 1.0,
        dropout: float = 0.1,
        use_aux_loss: bool = True,
        use_noisy_gate: bool = True,
        use_gradient_checkpointing: bool = False,
        expert_specialization: bool = False,
        min_expert_capacity: int = 4,
        max_expert_capacity: int = 256,
        pruning_threshold: float = 0.1
    ):
        super().__init__(
            input_dim=input_dim,
            num_experts=num_experts,
            expert_dim=expert_dim,
            k=k,
            capacity_factor=capacity_factor,
            dropout=dropout,
            use_aux_loss=use_aux_loss,
            use_noisy_gate=use_noisy_gate
        )
        
        self.use_gradient_checkpointing = use_gradient_checkpointing
        self.expert_specialization = expert_specialization
        self.min_expert_capacity = min_expert_capacity
        self.max_expert_capacity = max_expert_capacity
        self.pruning_threshold = pruning_threshold
        
        # Expert specialization parameters
        if expert_specialization:
            self.expert_embeddings = nn.Parameter(
                torch.randn(num_experts, input_dim)
            )
            self.specialization_router = nn.Linear(input_dim, num_experts)
        
        # Expert pruning parameters
        self.register_buffer("expert_importance", torch.ones(num_experts))
        self.register_buffer("expert_usage_count", torch.zeros(num_experts))
        
        # Dynamic capacity parameters
        self.register_buffer("current_capacity", torch.ones(num_experts) * min_expert_capacity)

    def _compute_dynamic_capacity(self, batch_size: int) -> torch.Tensor:
        """Compute dynamic capacity for each expert based on usage."""
        if not self.training:
            return self.current_capacity
        
        # Update capacity based on expert usage
        usage_ratio = self.expert_usage / (self.expert_usage.sum() + 1e-6)
        target_capacity = torch.clamp(
            usage_ratio * batch_size,
            min=self.min_expert_capacity,
            max=self.max_expert_capacity
        )
        
        # Smooth capacity updates
        self.current_capacity = (
            0.9 * self.current_capacity +
            0.1 * target_capacity
        )
        
        return self.current_capacity

    def _compute_specialization_weights(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:
        """Compute expert specialization weights."""
        if not self.expert_specialization:
            return None
        
        # Compute similarity between input and expert embeddings
        similarity = F.cosine_similarity(
            x.unsqueeze(1),
            self.expert_embeddings.unsqueeze(0),
            dim=-1
        )
        
        # Combine with router weights
        router_weights = self.specialization_router(x)
        combined_weights = F.softmax(
            similarity + router_weights,
            dim=-1
        )
        
        return combined_weights

    def _prune_experts(self) -> None:
        """Prune experts based on importance and usage."""
        if not self.training:
            return
        
        # Update expert importance
        self.expert_importance = (
            0.9 * self.expert_importance +
            0.1 * (self.expert_usage / (self.expert_usage.sum() + 1e-6))
        )
        
        # Mark experts for pruning
        prune_mask = self.expert_importance < self.pruning_threshold
        if prune_mask.any():
            logger.info(f"Pruning {prune_mask.sum()} experts")
            self.expert_importance[prune_mask] = 0.0

    def _apply_gradient_checkpointing(
        self,
        expert_idx: int,
        x: torch.Tensor
    ) -> torch.Tensor:
        """Apply gradient checkpointing to expert computation."""
        if not self.use_gradient_checkpointing:
            return self.experts[expert_idx](x)
        
        def create_custom_forward(module):
            def custom_forward(*inputs):
                return module(inputs[0])
            return custom_forward
        
        return torch.utils.checkpoint.checkpoint(
            create_custom_forward(self.experts[expert_idx]),
            x
        )

    def forward(
        self,
        x: torch.Tensor,
        return_aux_loss: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass with advanced features.
        """
        batch_size, seq_len, _ = x.shape
        x_reshaped = x.view(-1, self.input_dim)
        
        # Compute dynamic capacity
        capacity = self._compute_dynamic_capacity(batch_size * seq_len)
        
        # Get routing weights with specialization
        router_logits = self.router(x_reshaped)
        if self.expert_specialization:
            spec_weights = self._compute_specialization_weights(x_reshaped)
            router_logits = router_logits + spec_weights
        
        router_logits = self._noisy_gate(router_logits)
        router_probs = F.softmax(router_logits, dim=-1)
        
        # Apply expert pruning
        if self.training:
            self._prune_experts()
            router_probs = router_probs * self.expert_importance
        
        # Select top-k experts
        top_k_weights, top_k_indices = torch.topk(router_probs, self.k)
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)
        
        # Apply experts with gradient checkpointing
        expert_outputs = []
        for i in range(self.k):
            expert_idx = top_k_indices[:, i]
            expert_output = torch.stack([
                self._apply_gradient_checkpointing(
                    idx.item(),
                    x_reshaped[j]
                ) for j, idx in enumerate(expert_idx)
            ])
            expert_outputs.append(
                expert_output * top_k_weights[:, i].unsqueeze(-1)
            )
        
        # Combine expert outputs
        output = sum(expert_outputs)
        output = output.view(batch_size, seq_len, self.input_dim)
        
        # Update expert usage statistics
        if self.training:
            with torch.no_grad():
                for i in range(self.k):
                    self.expert_usage.scatter_add_(
                        0,
                        top_k_indices[:, i],
                        top_k_weights[:, i]
                    )
                    self.expert_usage_count.scatter_add_(
                        0,
                        top_k_indices[:, i],
                        torch.ones_like(top_k_weights[:, i])
                    )
        
        # Calculate auxiliary losses
        aux_loss = None
        if return_aux_loss and self.use_aux_loss:
            load_balancing_loss = self._load_balancing_loss(
                router_probs,
                top_k_indices
            )
            capacity_loss = self._capacity_loss(
                router_probs,
                top_k_indices
            )
            specialization_loss = 0.0
            if self.expert_specialization:
                specialization_loss = F.mse_loss(
                    router_probs,
                    spec_weights
                )
            
            aux_loss = (
                load_balancing_loss +
                capacity_loss +
                0.1 * specialization_loss
            )
        
        return output, aux_loss

    def get_expert_stats(self) -> Dict[str, Any]:
        """Get detailed expert statistics."""
        return {
            'usage': self.expert_usage.tolist(),
            'importance': self.expert_importance.tolist(),
            'usage_count': self.expert_usage_count.tolist(),
            'capacity': self.current_capacity.tolist()
        } 