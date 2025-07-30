# -*- coding: utf-8 -*-

from rwkvfla.modules.convolution import ImplicitLongConvolution, LongConvolution, ShortConvolution
from rwkvfla.modules.fused_bitlinear import BitLinear, FusedBitLinear
from rwkvfla.modules.fused_cross_entropy import FusedCrossEntropyLoss
from rwkvfla.modules.fused_kl_div import FusedKLDivLoss
from rwkvfla.modules.fused_linear_cross_entropy import FusedLinearCrossEntropyLoss
from rwkvfla.modules.fused_norm_gate import (
    FusedLayerNormGated,
    FusedLayerNormSwishGate,
    FusedLayerNormSwishGateLinear,
    FusedRMSNormGated,
    FusedRMSNormSwishGate,
    FusedRMSNormSwishGateLinear
)
from rwkvfla.modules.l2norm import L2Norm
from rwkvfla.modules.layernorm import GroupNorm, GroupNormLinear, LayerNorm, LayerNormLinear, RMSNorm, RMSNormLinear
from rwkvfla.modules.mlp import GatedMLP
from rwkvfla.modules.rotary import RotaryEmbedding
from rwkvfla.modules.token_shift import TokenShift

__all__ = [
    'ImplicitLongConvolution', 'LongConvolution', 'ShortConvolution',
    'BitLinear', 'FusedBitLinear',
    'FusedCrossEntropyLoss', 'FusedLinearCrossEntropyLoss', 'FusedKLDivLoss',
    'L2Norm',
    'GroupNorm', 'GroupNormLinear', 'LayerNorm', 'LayerNormLinear', 'RMSNorm', 'RMSNormLinear',
    'FusedLayerNormGated', 'FusedLayerNormSwishGate', 'FusedLayerNormSwishGateLinear',
    'FusedRMSNormGated', 'FusedRMSNormSwishGate', 'FusedRMSNormSwishGateLinear',
    'GatedMLP',
    'RotaryEmbedding',
    'TokenShift'
]
