# Copyright 2025 Tencent Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from abc import ABCMeta, abstractmethod

import torch
from safetensors.torch import save_file as safe_save

from ....utils import print_info
from ..modules import QDQSingleModule
from .quant_func import tensor_quant

__all__ = ["PTQvLLMSaveHF"]


class PTQSaveBase(metaclass=ABCMeta):
    def __init__(self, quant_model):
        self.quant_model = quant_model

    @abstractmethod
    def save(self, save_path):
        pass


class PTQvLLMSaveHF(PTQSaveBase):
    def __init__(self, quant_model):
        super(PTQvLLMSaveHF, self).__init__(quant_model=quant_model.model)

    def save(self, save_path):
        """save quantized model and configs to local disk"""
        os.makedirs(save_path, exist_ok=True)

        state_dict = self.quant_model.state_dict()
        for name in list(state_dict.keys()):
            if "qweight" in name:
                pop_name = name.replace("qweight", "layer.weight")
                if pop_name in state_dict.keys():
                    state_dict.pop(pop_name)
                pop_name = name.replace("qweight", "layer.bias")
                if pop_name in state_dict.keys():
                    state_dict[name.replace("qweight", "bias")] = state_dict[pop_name]
                    state_dict.pop(pop_name)
        print_info("state_dict:{}".format(state_dict.keys()))
        model_base_name = "quant_model"
        model_save_name = model_base_name + ".safetensors"
        safetensors_metadata = {}
        safetensors_metadata["format"] = "pt"
        safe_save(
            state_dict, os.path.join(save_path, model_save_name), safetensors_metadata
        )
        self.quant_model.config.save_pretrained(save_path)


class PTQVLMSaveVllmHF(PTQSaveBase):
    def __init__(self, quant_model):
        super().__init__(quant_model=quant_model)

    def save(self, save_path):
        a_quant_algo = self.quant_model.quant_config.quant_algo_info["a"]

        static_q_dict = {
            "quantization_config": {
                "quant_method": "fp8",
                "activation_scheme": (
                    "dynamic" if "dynamic" in a_quant_algo else "static"
                ),
                "ignored_layers": ["visual.patch_embed.proj", "lm_head"],
            }
        }
        self.quant_model.get_model().config.update(static_q_dict)

        os.makedirs(save_path, exist_ok=True)

        if self.quant_model.quant_config.quant_algo == "int8":
            for _, sub_layer in self.quant_model.quant_config.quant_layers_dict.items():
                if isinstance(sub_layer, QDQSingleModule):
                    sub_layer.weight = tensor_quant(
                        sub_layer.weight, sub_layer.weight_scales
                    )

        self.quant_model.get_model().save_pretrained(save_path)


class PTQSaveVllmHF(PTQSaveBase):
    def __init__(self, quant_model):
        super().__init__(quant_model=quant_model)

    def save(self, save_path):
        w_quant_algo = self.quant_model.quant_config.quant_algo_info["w"]
        a_quant_algo = self.quant_model.quant_config.quant_algo_info["a"]
        ignore_layers = self.quant_model.quant_config.quant_algo_info["ignore_layers"]
        if "fp8" in self.quant_model.quant_config.quant_algo:
            static_q_dict = {
                "quantization_config": {
                    "quant_method": "fp8",
                    "activation_scheme": (
                        "dynamic" if "dynamic" in a_quant_algo else "static"
                    ),
                    "ignored_layers": ignore_layers,
                }
            }
        elif "int8" in self.quant_model.quant_config.quant_algo:
            assert "per-channel" in w_quant_algo
            assert "per-token" in a_quant_algo
            static_q_dict = {
                "quantization_config": {
                    "config_groups": {
                        "group_0": {
                            "input_activations": {
                                "block_structure": None,
                                "dynamic": "dynamic" in a_quant_algo,
                                "group_size": None,
                                "num_bits": 8,
                                "observer": "memoryless",
                                "observer_kwargs": {},
                                "strategy": "token",
                                "symmetric": True,
                                "type": "int",
                            },
                            "output_activations": None,
                            "targets": ["Linear"],
                            "weights": {
                                "block_structure": None,
                                "dynamic": False,
                                "group_size": None,
                                "num_bits": 8,
                                "observer": "minmax",
                                "observer_kwargs": {},
                                "strategy": "channel",
                                "symmetric": True,
                                "type": "int",
                            },
                        }
                    },
                    "format": "int-quantized",
                    "ignored_layers": ignore_layers,
                    "kv_cache_scheme": None,
                    "quant_method": "compressed-tensors",
                },
            }
        else:
            raise ValueError(
                f"{self.quant_model.quant_config.quant_algo} not supported"
            )
        self.quant_model.get_model().config.update(static_q_dict)
        print_info("Save quantization_config: {}".format(static_q_dict))

        os.makedirs(save_path, exist_ok=True)
        self.quant_model.get_model().save_pretrained(save_path)


class PTQTorchSave(PTQSaveBase):
    def __init__(self, quant_model):
        super(PTQTorchSave, self).__init__(quant_model=quant_model)

    def save(self, save_path):
        """save quantized model and configs to local disk"""
        os.makedirs(save_path, exist_ok=True)

        if self.quant_model.act_scales_dict:
            for k, v in self.quant_model.act_scales_dict.items():
                _save_path = os.path.join(save_path, "{}.act_scales.pt".format(k))
                torch.save(v, _save_path)
            print_info("save act scales done.")
        else:
            print_info("no act scales found.")

        if self.quant_model.weight_scales_dict:
            for k, v in self.quant_model.weight_scales_dict.items():
                _save_path = os.path.join(save_path, "{}.weight_scales.pt".format(k))
                torch.save(v, _save_path)
            print_info("save weight scales done.")
        else:
            print_info("no act scales found.")


class PTQPTMSave(PTQSaveBase):
    def __init__(self, quant_model):
        super(PTQPTMSave, self).__init__(quant_model=quant_model)

    def save(self, save_path):
        """save quantized model and configs to local disk"""
        os.makedirs(save_path, exist_ok=True)
        _index = torch.distributed.get_rank()
        if self.quant_model.act_scales_dict:
            for k, v in self.quant_model.act_scales_dict.items():
                _save_path = os.path.join(save_path, "{}.act_scales.pt".format(k))
                torch.distributed.all_reduce(v, op=torch.distributed.ReduceOp.MAX)
                if _index == 0:
                    torch.save(v, _save_path)
            print_info("save act scales done.")

        if self.quant_model.weight_scales_dict:
            for k, v in self.quant_model.weight_scales_dict.items():
                torch.distributed.all_reduce(v, op=torch.distributed.ReduceOp.MAX)
                _save_path = os.path.join(save_path, "{}.weight_scales.pt".format(k))
                if _index == 0:
                    torch.save(v, _save_path)
            print_info("save weight scales done.")
