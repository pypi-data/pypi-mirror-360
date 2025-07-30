# -*- coding: utf-8 -*-

from transformers import AutoConfig, AutoModel, AutoModelForCausalLM, AutoTokenizer

from rwkvfla.models.rodimus.configuration_rodimus import RodimusConfig
from rwkvfla.models.rodimus.modeling_rodimus import RodimusForCausalLM, RodimusModel
from rwkvfla.models.rodimus.tokenization_rodimus_fast import RodimusTokenizer

AutoConfig.register(RodimusConfig.model_type, RodimusConfig)
AutoModel.register(RodimusConfig, RodimusModel)
AutoModelForCausalLM.register(RodimusConfig, RodimusForCausalLM)
AutoTokenizer.register(RodimusConfig, slow_tokenizer_class=None, fast_tokenizer_class=RodimusTokenizer)


__all__ = ['RodimusConfig', 'RodimusForCausalLM', 'RodimusModel', 'RodimusTokenizer']
