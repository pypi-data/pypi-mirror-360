import os
import torch
from peft import PeftModel, PeftConfig, get_peft_model
from trl import AutoModelForCausalLMWithValueHead
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from omegaconf import OmegaConf
import sys
import os.path as osp
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)

def infer_output_dim(state_dict):
    for key in state_dict.keys():
        if 'score.weight' in key:
            return state_dict[key].shape[0]
        if 'classifier.weight' in key:
            return state_dict[key].shape[0]
    raise ValueError('Cannot infer output dimension from state_dict')


def load_model_and_tokenizer(model_name,
                             bnb_config=None,
                             peft_config=None,
                             model_class=AutoModelForSequenceClassification,
                             is_trainable=True,
                             device='cuda',
                             state_dict_path=None,
                             **kwargs
                             ):

    if state_dict_path is not None:
        logger.info(f'Load model from state_dict {state_dict_path}')
        state_dict = torch.load(state_dict_path, weights_only=True)

        kwargs.update({"num_labels": infer_output_dim(state_dict)})
        logger.info(f'Infer output dimension: {kwargs["num_labels"]}')

    if is_trainable:
        logger.info('Load model in **training** mode')
        device = f"cuda:{os.getenv('LOCAL_RANK', 0)}"
    else:
        logger.info('Load model in **inference** mode')

    if bnb_config is not None:
        kwargs['quantization_config'] = bnb_config

    if os.path.exists(model_name):
        logger.info(f'Load peft model from local {model_name}')
        config = AutoConfig.from_pretrained(model_name)
        if model_class == AutoModelForCausalLM:
            model = model_class.from_pretrained(config._name_or_path,
                                                device_map={'': device},
                                                **kwargs)
            if os.path.exists(osp.join(model_name, 'adapter_config.json')):
                model = PeftModel.from_pretrained(model, model_name, is_trainable=is_trainable)
        else:
            logger.info(kwargs)
            model = model_class.from_pretrained(model_name,
                                                device_map={'': device},
                                                local_files_only=True,
                                                use_cache=False,
                                                **kwargs
                                                )
        tokenizer = AutoTokenizer.from_pretrained(config._name_or_path)
    else:
        logger.info(f'Loading {model_class}: {model_name}')
        model = model_class.from_pretrained(
            model_name,
            trust_remote_code=True,
            use_cache=False,
            device_map={'': device},
            **kwargs
        )
        if peft_config is not None:
            model = get_peft_model(model, peft_config)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    if model_class == AutoModelForCausalLM:
        tokenizer.padding_side = 'right' if is_trainable else 'left'
    else:
        tokenizer.padding_side = 'right'

    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.pad_token_id

    if state_dict_path is not None:
        assert set(state_dict.keys()).issubset(set(model.state_dict().keys()))
        model.load_state_dict(state_dict, strict=False)

    logger.info(f'is_trainable={is_trainable} | padding_side={tokenizer.padding_side} | device={device}')
    return model, tokenizer


def load_system_config(config_file):
    config = OmegaConf.load(config_file)
    if len(sys.argv) > 1 and sys.argv[1].endswith('.yaml'):
        new_config_file = sys.argv[1]
        new_config = OmegaConf.load(new_config_file)
        config = OmegaConf.merge(config, new_config)
        sys.argv.pop(1)

    # Can be overwritten by command line arguments
    cli_config = OmegaConf.from_cli()
    config = OmegaConf.merge(config, cli_config)

    return config

if __name__ == '__main__':

    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=False,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    from peft import LoraConfig
    peft_config = LoraConfig(
        r=32,
        lora_alpha=16,
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
        init_lora_weights="gaussian",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"]
    )
    model, tokenizer = load_model_and_tokenizer("meta-llama/Llama-3.1-8B-Instruct",
                                                peft_config=peft_config,
                                                bnb_config=bnb_config,
                                                model_class=AutoModelForSequenceClassification,
                                                num_labels=1)
    logger.info(model)

