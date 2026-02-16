# README

## Daten prüfen

```bash
python src/inspect_annoctr.py
```

## AnnoCTR → ReLiK-Format konvertieren

```bash
python src/convert_annoctr_to_relik.py
```


## Span-Sanity-Check

```bash

```

## Windows erzeugen (ReLiK)

```bash
python src/create_windows.py
```


## Mitre documents builden
```bash
python src/build_mitre_documents.py
```
## Index Kreieren

```bash
python -m relik.cli.cli retriever create-index \
  sapienzanlp/relik-retriever-e5-base-v2-aida-blink-encoder \
  data/index/mitre_documents.jsonl \
  data/index/mitre_index \
  --document-file-type jsonl \
  --device cpu \
  --index-device cpu
```

## Candidates hinzufügen (Retriever)

```bash
python src/add_candidates.py
```

## Reader trainieren

```bash
python -m relik.cli.cli reader train \
  base \
  ++data.train_dataset_path=data/candidates/relik/train.window.candidates.jsonl \
  ++data.val_dataset_path=data/candidates/relik/val.window.candidates.jsonl \
  ++data.test_dataset_path=data/candidates/relik/test.window.candidates.jsonl \
  ++data.train_dataset.section_size=null \
  ++training.trainer.devices=1 \
  ++training.trainer.accelerator=cpu

```
3 auswählen
## Eval

```bash
python src/eval.py
```

