import torch
import yaml

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)


# =========================
# Load config
# =========================

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

MODEL_NAME = cfg["model_name"]
OUTPUT_DIR = cfg["output_dir"]


# =========================
# Load dataset
# =========================

dataset = load_dataset(
    "json",
    data_files="train.jsonl"
)


# =========================
# Tokenizer
# =========================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

tokenizer.pad_token = tokenizer.eos_token


# =========================
# Quant config (QLoRA)
# =========================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)


# =========================
# Load model
# =========================

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model = prepare_model_for_kbit_training(model)


# =========================
# LoRA config
# =========================

lora_cfg = LoraConfig(
    r=cfg["lora"]["r"],
    lora_alpha=cfg["lora"]["alpha"],
    lora_dropout=cfg["lora"]["dropout"],
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=cfg["lora"]["target_modules"]
)

model = get_peft_model(model, lora_cfg)

model.print_trainable_parameters()


# =========================
# Formatting function
# =========================

def format_sample(sample):

    messages = sample["messages"]

    text = ""

    for m in messages:
        role = m["role"]
        content = m["content"]

        if role == "system":
            text += f"<|system|>{content}\n"
        elif role == "user":
            text += f"<|user|>{content}\n"
        elif role == "assistant":
            text += f"<|assistant|>{content}\n"

    text += "<|end|>"

    return {"text": text}


dataset = dataset.map(format_sample)


# =========================
# Tokenize
# =========================

def tokenize(batch):

    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )


dataset = dataset.map(
    tokenize,
    batched=True,
    remove_columns=dataset["train"].column_names
)


# =========================
# Training args
# =========================

args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=cfg["train"]["per_device_train_batch_size"],
    gradient_accumulation_steps=cfg["train"]["gradient_accumulation_steps"],
    learning_rate=cfg["train"]["learning_rate"],
    num_train_epochs=cfg["train"]["num_train_epochs"],
    fp16=cfg["train"]["fp16"],
    logging_steps=cfg["train"]["logging_steps"],
    save_strategy=cfg["train"]["save_strategy"],
    save_total_limit=cfg["train"]["save_total_limit"],
    report_to=cfg["train"]["report_to"],
    optim="paged_adamw_8bit"
)


# =========================
# Trainer
# =========================

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
)


# =========================
# Train
# =========================

trainer.train()


# =========================
# Save
# =========================

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("✅ Training finished")
