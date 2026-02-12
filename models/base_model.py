from __future__ import annotations

import torch
import torch.nn as nn


class GrooveTransformer(nn.Module):
    """Lightweight transformer used for both drum and melodic generation."""

    def __init__(self, input_dim: int = 128, hidden_dim: int = 256, num_layers: int = 4, num_heads: int = 4):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=num_heads, batch_first=True)
        self.embedding = nn.Linear(input_dim, hidden_dim)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.embedding(x)
        x = self.encoder(x)
        return torch.sigmoid(self.output(x))
