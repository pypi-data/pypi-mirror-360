# -*- coding: utf-8 -*-

from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

from rwkvfla.models.retnet.configuration_retnet import RetNetConfig
from rwkvfla.models.retnet.modeling_retnet import RetNetForCausalLM, RetNetModel

AutoConfig.register(RetNetConfig.model_type, RetNetConfig, exist_ok=True)
AutoModel.register(RetNetConfig, RetNetModel, exist_ok=True)
AutoModelForCausalLM.register(RetNetConfig, RetNetForCausalLM, exist_ok=True)


__all__ = ['RetNetConfig', 'RetNetForCausalLM', 'RetNetModel']
