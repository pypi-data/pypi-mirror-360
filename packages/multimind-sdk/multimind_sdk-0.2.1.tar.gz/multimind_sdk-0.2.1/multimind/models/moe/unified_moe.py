from typing import Dict, List, Any, Optional, Union, Type
import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from .moe_layer import MoELayer
from .moe_model import MoEModel
from .moe import Expert, MoEBase, ExpertRouter
from ..base import BaseLLM
import logging

logger = logging.getLogger(__name__)

class UnifiedMoE(nn.Module):
    """
    Unified interface for both neural and modality-based MoE implementations.
    """
    def __init__(
        self,
        mode: str = "neural",  # "neural" or "modality"
        config: Dict[str, Any] = None,
        experts: Optional[Dict[str, Expert]] = None
    ):
        super().__init__()
        self.mode = mode
        self.config = config or {}
        
        if mode == "neural":
            self.model = self._create_neural_moe()
        else:
            self.model = self._create_modality_moe(experts)
            
        # Initialize metrics
        self.metrics = {
            'expert_usage': {},
            'routing_weights': {},
            'performance_metrics': {}
        }

    def _create_neural_moe(self) -> MoEModel:
        """Create neural network-based MoE model."""
        return MoEModel(
            input_dim=self.config.get('input_dim', 768),
            hidden_dim=self.config.get('hidden_dim', 1024),
            num_experts=self.config.get('num_experts', 8),
            num_layers=self.config.get('num_layers', 6),
            num_heads=self.config.get('num_heads', 8),
            k=self.config.get('k', 2),
            dropout=self.config.get('dropout', 0.1),
            expert_dropout=self.config.get('expert_dropout', 0.1),
            use_aux_loss=self.config.get('use_aux_loss', True),
            use_noisy_gate=self.config.get('use_noisy_gate', True)
        )

    def _create_modality_moe(self, experts: Optional[Dict[str, Expert]]) -> MoEBase:
        """Create modality-based MoE model."""
        if not experts:
            raise ValueError("Experts must be provided for modality-based MoE")
        return MoEBase(
            experts=experts,
            hidden_size=self.config.get('hidden_size', 768),
            num_experts=len(experts)
        )

    async def process(
        self,
        input_data: Union[torch.Tensor, Dict[str, Any]],
        return_aux_loss: bool = False
    ) -> Dict[str, Any]:
        """
        Process input through the MoE model.
        
        Args:
            input_data: Input tensor or dictionary of modality inputs
            return_aux_loss: Whether to return auxiliary losses
            
        Returns:
            Dictionary containing model outputs and optional metrics
        """
        if self.mode == "neural":
            return await self._process_neural(input_data, return_aux_loss)
        else:
            return await self._process_modality(input_data)

    async def _process_neural(
        self,
        input_data: torch.Tensor,
        return_aux_loss: bool
    ) -> Dict[str, Any]:
        """Process input through neural MoE model."""
        output, aux_loss = self.model(input_data, return_aux_loss)
        
        # Update metrics
        self._update_neural_metrics()
        
        return {
            'output': output,
            'aux_loss': aux_loss,
            'metrics': self.metrics
        }

    async def _process_modality(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input through modality-based MoE model."""
        result = await self.model.process(input_data)
        
        # Update metrics
        self._update_modality_metrics(result)
        
        return {
            **result,
            'metrics': self.metrics
        }

    def _update_neural_metrics(self):
        """Update metrics for neural MoE model."""
        if isinstance(self.model, MoEModel):
            self.metrics['expert_usage'] = self.model.get_expert_usage()
            # Add more neural-specific metrics here

    def _update_modality_metrics(self, result: Dict[str, Any]):
        """Update metrics for modality-based MoE model."""
        if 'expert_weights' in result:
            self.metrics['routing_weights'] = result['expert_weights']
            # Add more modality-specific metrics here

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            'expert_usage': {},
            'routing_weights': {},
            'performance_metrics': {}
        }
        if isinstance(self.model, MoEModel):
            self.model.reset_expert_usage()

    def save_checkpoint(self, path: str):
        """Save model checkpoint."""
        checkpoint = {
            'mode': self.mode,
            'config': self.config,
            'model_state_dict': self.model.state_dict(),
            'metrics': self.metrics
        }
        torch.save(checkpoint, path)

    @classmethod
    def load_checkpoint(cls, path: str) -> 'UnifiedMoE':
        """Load model from checkpoint."""
        checkpoint = torch.load(path)
        model = cls(
            mode=checkpoint['mode'],
            config=checkpoint['config']
        )
        model.model.load_state_dict(checkpoint['model_state_dict'])
        model.metrics = checkpoint['metrics']
        return model

    def add_expert(
        self,
        expert_id: str,
        expert: Expert,
        modality: Optional[str] = None
    ):
        """Add a new expert to the model."""
        if self.mode == "modality":
            if not isinstance(self.model, MoEBase):
                raise ValueError("Cannot add expert to neural MoE model")
            self.model.experts[expert_id] = expert
        else:
            raise ValueError("Cannot add expert to neural MoE model")

    def remove_expert(self, expert_id: str):
        """Remove an expert from the model."""
        if self.mode == "modality":
            if not isinstance(self.model, MoEBase):
                raise ValueError("Cannot remove expert from neural MoE model")
            if expert_id in self.model.experts:
                del self.model.experts[expert_id]
        else:
            raise ValueError("Cannot remove expert from neural MoE model")

    def get_expert_info(self) -> Dict[str, Any]:
        """Get information about all experts."""
        if self.mode == "neural":
            return {
                'num_experts': self.model.num_experts,
                'expert_dim': self.model.hidden_dim * 4,
                'usage': self.model.get_expert_usage()
            }
        else:
            return {
                'experts': list(self.model.experts.keys()),
                'modalities': list(set(
                    expert.__class__.__name__.lower().replace('expert', '')
                    for expert in self.model.experts.values()
                ))
            } 