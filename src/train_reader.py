#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from omegaconf import OmegaConf
from relik.reader.reader import Reader
from lightning.pytorch import Trainer

ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = ROOT / "reader/base.yaml"

TRAIN = ROOT / "data/candidates/relik/train.window.candidates.jsonl"
VAL = ROOT / "data/candidates/relik/val.window.candidates.jsonl"
TEST = ROOT / "data/candidates/relik/test.window.candidates.jsonl"

print("Loading config:", CONFIG_PATH)
cfg = OmegaConf.load(CONFIG_PATH)

# Override dataset paths
cfg.data.train_dataset_path = str(TRAIN)
cfg.data.val_dataset_path = str(VAL)
cfg.data.test_dataset_path = str(TEST)

print("Initializing model...")
model = Reader(cfg)

print("Starting training...")
trainer = Trainer(
    max_epochs=cfg.trainer.max_epochs,
    accelerator="cpu",
    devices=1,
)

trainer.fit(model)
