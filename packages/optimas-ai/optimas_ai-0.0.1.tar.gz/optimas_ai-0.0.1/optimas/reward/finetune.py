from optimas.external.reward_trainer import RewardTrainer
from optimas.external.reward_config import RewardConfig
from peft import LoraConfig
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import DatasetDict
from optimas.reward.metrics import compute_accuracy_and_margin
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)

def run_finetune(
    dataset: DatasetDict,
    model: AutoModelForSequenceClassification,
    tokenizer: AutoTokenizer,
    training_args: RewardConfig,
    peft_config: LoraConfig = None,
    train_last_layer: bool = False,
    **kwargs
):
    model.train()
    trainer = RewardTrainer(
        model=model,
        processing_class=tokenizer,
        args=training_args,
        train_dataset=dataset.get('train', dataset),
        eval_dataset=dataset.get('test', None) if training_args.eval_strategy != "no" else None,
        peft_config=peft_config,
        compute_metrics=compute_accuracy_and_margin,
        **kwargs
    )

    if train_last_layer:
        # Unfreeze only the last layer of the model
        for name, param in list(trainer.model.named_parameters())[-1:]:
            logger.info(f'Unfreezing layer: {name}')
            param.requires_grad = True

    def count_parameters(model):
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        return trainable_params, total_params

    n_trainable_params, n_params = count_parameters(trainer.model)
    logger.info(f'Trainable parameters: {n_trainable_params} / {n_params} ({n_trainable_params / n_params * 100:.2f}%)')

    trainer.train()
    return trainer
