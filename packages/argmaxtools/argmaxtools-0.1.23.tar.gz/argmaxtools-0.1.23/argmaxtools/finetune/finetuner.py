#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2024 Argmax, Inc. All Rights Reserved.
#

from abc import ABC, abstractmethod
import torch

from dataclasses import dataclass
from tqdm import trange
from typing import Optional
import wandb

from argmaxtools.utils import get_fastest_device, get_logger

logger = get_logger(__name__)


@dataclass
class FinetuneConfig:
    epochs: int = None
    project_name: str = None
    job_name: str = None
    learning_rate: float = 3e-4
    batch_size: int = 32
    report_iter: int = 10
    eval_iter: int = 100
    num_iter: int = 1000
    grad_accum_steps: int = 1
    report_wandb: bool = True


class Finetuner(ABC):

    def __init__(self,
                 model_version: str,
                 cache_dir: str,
                 config: FinetuneConfig,
                 data: Optional[torch.utils.data.DataLoader] = None,
                 device: Optional[torch.device] = None):

        self.model_version = model_version
        self.cache_dir = cache_dir
        self.config = config
        self.config.model_version = model_version

        self.dev = device or get_fastest_device()
        self.data = data

        self.epochs = self.config.epochs or self.config.num_iter // self.config.eval_iter
        teacher_model, train_model = self.init_teacher_and_train_models()

        if teacher_model is not None:
            self.teacher_model = teacher_model.to(self.default_dtype).to(self.dev)
            self.teacher_model.eval()
        self.train_model = train_model.to(self.default_dtype).to(self.dev)

        self.optimizer = self.init_optimizer()
        self.scheduler = self.init_scheduler()

    def init_optimizer(self):
        optimizer = torch.optim.AdamW(
            [p for p in self.train_model.parameters() if p.requires_grad],
            lr=self.config.learning_rate
        )
        return optimizer

    def init_scheduler(self):
        return None

    @abstractmethod
    def init_teacher_and_train_models(self):
        pass

    def get_batch(self):
        """ Get a batch of data from the data loader or generate a random batch"""
        return next(iter(self.data))

    @property
    def default_dtype(self) -> torch.dtype:
        """ The default weight and activation precision for the model
        """
        return torch.float32

    @abstractmethod
    def forward_pass(self, data_batch):
        '''
        Returns the loss from the forward pass
        '''
        pass

    @abstractmethod
    def get_metrics(self):
        pass

    @abstractmethod
    def report_metrics(self, metrics):
        pass

    def init_wandb(self):
        wandb.init(
            # Set the project where this run will be logged
            project=self.config.project_name,
            # We pass a run name (otherwise it’ll be randomly assigned, like sunshine-lollypop-10)
            name=self.config.job_name,
            # Track hyperparameters and run metadata
            config=self.config.__dict__,
            mode="disabled" if not self.config.report_wandb else "online"
        )

    def train_step(self):
        data_batch = self.get_batch()
        loss = self.forward_pass(data_batch)
        loss = loss / self.config.grad_accum_steps  # Scale the loss
        loss.backward()

        # Only step optimizer and scheduler after grad_accum_steps
        if (self.cur_iter + 1) % self.config.grad_accum_steps == 0:
            self.optimizer.step()
            self.optimizer.zero_grad()
            if self.scheduler is not None:
                self.scheduler.step()

        self.loss = loss.item() * self.config.grad_accum_steps  # Unscale the loss for reporting
        metrics = self.get_metrics()

        return metrics

    def train(self):
        self.init_wandb()

        self.cur_epoch = 0
        self.cur_batch_idx = 0
        self.cur_iter = 0

        # Evaluate the model before training
        val_metrics = self.evaluate()
        self.report_metrics(val_metrics)

        # Training loop
        for epoch in trange(self.epochs, desc="Epoch"):
            self.cur_epoch = epoch
            self.train_model.train()
            for batch in trange(self.config.num_iter // self.epochs, desc="Batch"):
                self.cur_batch_idx = batch
                metrics = self.train_step()

                self.cur_iter += 1
                if self.cur_iter % self.config.report_iter == 0:
                    self.report_metrics(metrics)

            val_metrics = self.evaluate()
            self.report_metrics(val_metrics)

    @abstractmethod
    def evaluate(self):
        pass
