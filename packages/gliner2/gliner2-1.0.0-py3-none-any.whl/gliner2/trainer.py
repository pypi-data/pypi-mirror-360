import json
import random
from typing import Union, List

import torch
from torch.utils.data import Dataset
from transformers import Trainer


class ExtractorDataset(Dataset):
    """
    A Dataset for loading JSONL data tailored for the Extractor model.
    Accepts a single file path or a list of file paths.
    """

    def __init__(self, data_paths: Union[str, List[str]]):
        if isinstance(data_paths, str):
            data_paths = [data_paths]  # Ensure it's a list

        # log number of files
        print(f"Loading {len(data_paths)} files for training.")

        self.data = []
        for path in data_paths:
            with open(path, "r", encoding="utf-8") as f:
                self.data.extend([json.loads(line) for line in f])

        # shuffle the data
        random.shuffle(self.data)

        # log number of records
        print(f"Loaded {len(self.data)} records from {len(data_paths)} files.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        record = self.data[idx]
        # Map keys to what your model expects.
        return record["input"], record["output"]


class ExtractorDataCollator:
    """
    Data collator for the Extractor model.
    """

    def __call__(self, batch):
        return batch


class ExtractorTrainer(Trainer):
    """
    A Trainer with customized optimizer and training step tailored for the Extractor model.
    Now supports an option to freeze everything except `model.classifier`.
    """

    def __init__(
        self,
        encoder_lr,
        custom_lr,
        weight_decay,
        finetune_classifier: bool = False,
        **kwargs
    ):
        """
        Args:
            encoder_lr (float): learning rate for encoder parameters (ignored if finetune_classifier=True)
            custom_lr (float): learning rate for non-encoder parameters (e.g., classifier)
            weight_decay (float): weight decay for all parameter groups
            finetune_classifier (bool): if True, freeze all parameters except `model.classifier`
        """
        self.encoder_lr = encoder_lr
        self.custom_lr = custom_lr
        self.custom_weight_decay = weight_decay
        self.finetune_classifier = finetune_classifier

        super().__init__(**kwargs)

        if self.finetune_classifier:
            # Freeze all parameters except classifier
            for name, param in self.model.named_parameters():
                if not name.startswith("classifier"):
                    param.requires_grad = False

    def create_optimizer(self):
        """
        Create an optimizer with separate parameter groups.
        If finetune_classifier=True, only classifier params go into optimizer.
        Otherwise, use two groups: encoder and everything else.
        """
        optimizer_grouped_parameters = []

        if self.finetune_classifier:
            # log
            print("Finetuning classifier only: freezing all other parameters.")
            # Only include classifier parameters in optimizer
            classifier_params = [
                p for n, p in self.model.named_parameters()
                if n.startswith("classifier") and p.requires_grad
            ]
            if not classifier_params:
                raise ValueError("No trainable parameters found in `model.classifier`.")
            optimizer_grouped_parameters = [
                {
                    "params": classifier_params,
                    "lr": self.custom_lr,
                    "weight_decay": self.custom_weight_decay,
                }
            ]
        else:
            # Full fine-tuning: encoder and others separated
            # encoder parameters
            encoder_params = list(self.model.encoder.parameters())
            # everything else (including classifier, count layers, etc.)
            other_params = [
                param
                for name, param in self.model.named_parameters()
                if "encoder" not in name and param.requires_grad
            ]
            optimizer_grouped_parameters = [
                {"params": encoder_params, "lr": self.encoder_lr, "weight_decay": self.custom_weight_decay},
                {"params": other_params, "lr": self.custom_lr, "weight_decay": self.custom_weight_decay},
            ]

        optimizer_cls, optimizer_kwargs = Trainer.get_optimizer_cls_and_kwargs(self.args)
        self.optimizer = optimizer_cls(optimizer_grouped_parameters, **optimizer_kwargs)
        return self.optimizer

    def training_step(self, model, inputs, *args, **kwargs):
        """
        Customized training step to process each record individually.
        """
        model.train()
        model.processor.change_mode(is_training=True)
        losses = []
        try:
            # Each item in the batch is expected to be a tuple (input, output)
            for record in inputs:
                sample_record = {
                    "text": record[0],
                    "schema": record[1]
                }
                output = model.process_record(sample_record)
                losses.append(output["loss"])

            if losses:
                loss = torch.stack(losses).mean()
            else:
                loss = torch.tensor(0.0, device=self.args.device, requires_grad=True)
            loss.backward()

            return loss.detach()
        except Exception as e:
            print(f"Skipping iteration due to error: {e}")
            model.zero_grad(set_to_none=True)
            torch.cuda.empty_cache()
            return torch.tensor(0.0, requires_grad=True).to(model.device)
