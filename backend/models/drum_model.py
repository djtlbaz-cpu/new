from __future__ import annotations

import torch
from torch import nn

INPUT_SIZE = 6
HIDDEN_SIZE = 128
NUM_LAYERS = 2
SEQUENCE_LENGTH = 32


class DrumModel(nn.Module):
    """Simple LSTM model that predicts 32x6 drum grids."""

    def __init__(self) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=INPUT_SIZE,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
        )
        self.output = nn.Linear(HIDDEN_SIZE, INPUT_SIZE)
        self.activation = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 3:
            raise ValueError("Input tensor must have shape (batch, seq_len, features)")
        lstm_out, _ = self.lstm(x)
        logits = self.output(lstm_out)
        return self.activation(logits)

__all__ = [
  "DrumModel",
  "INPUT_SIZE",
  "HIDDEN_SIZE",
  "NUM_LAYERS",
  "SEQUENCE_LENGTH",
]
