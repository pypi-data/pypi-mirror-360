import os
import torch
from huggingface_hub import HfApi
from collections import OrderedDict
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)

STATE_DICT_FILE_NAME = "state_dict.pth"


def save_model_and_tokenizer(model, 
                             tokenizer,
                             output_dir, 
                             repo_name=None, 
                             push_to_hub=False,
                             criteria=lambda x: 'score.weight' in x.lower() or 'lora' in x.lower()
                             ):

    os.makedirs(output_dir, exist_ok=True)
    state_dict_to_save = {k: v for k, v in model.state_dict().items() if criteria(k)}
    state_dict_to_save = OrderedDict(sorted(state_dict_to_save.items(), key=lambda x: x[0]))
    
    torch.save(state_dict_to_save, os.path.join(output_dir, STATE_DICT_FILE_NAME))
    os.makedirs(output_dir, exist_ok=True)
    tokenizer.save_pretrained(output_dir)

    if push_to_hub:
        try:
            merged_model = model.merge_and_unload()
            merged_model.push_to_hub(repo_name, private=True)
            tokenizer.push_to_hub(repo_name, private=True)
           
        except Exception as e:
            logger.error(f"Error pushing model and tokenizer to the hub: {e}")
            return 
