import torch
import yaml
import random
import numpy as np

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)

from transformers import DataCollatorForLanguageModeling
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

# Добавьте в начало файла после импортов проверку формата данных
def inspect_dataset():
    """Проверка структуры dataset"""
    import json
    
    with open("train_llm.jsonl", "r") as f:
        first_line = f.readline().strip()
        sample = json.loads(first_line)
        print("📊 Структура данных:", json.dumps(sample, indent=2, ensure_ascii=False))
    
    # Проверяем количество примеров
    with open("train_llm.jsonl", "r") as f:
        lines = f.readlines()
        print(f"📈 Всего примеров: {len(lines)}")
    
    return sample

# Вызовите эту функцию перед загрузкой датасета
sample_data = inspect_dataset()


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
    data_files="train_llm.jsonl"
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
    torch_dtype=torch.float16,
    trust_remote_code=True
)

model = prepare_model_for_kbit_training(model)

model.gradient_checkpointing_enable()
model.config.use_cache = False


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
    """Форматирует сообщения в промпт для обучения"""
    messages = sample["messages"]
    
    prompt = ""
    
    for m in messages:
        role = m["role"]
        content = m["content"]
        
        # Используем формат Qwen
        prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    
    #Не добавляем лишний assistant в конце
    return {"text": prompt}

dataset = dataset.map(format_sample)


# =========================
# Tokenize
# =========================

def tokenize(batch):

    return tokenizer(
        batch["text"],
        truncation=True,
        padding=False,
        max_length=cfg["train"]["max_length"]  # ✅ Берем из config
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
    bf16=False,
    logging_steps=cfg["train"]["logging_steps"],
    save_strategy=cfg["train"]["save_strategy"],
    save_total_limit=cfg["train"]["save_total_limit"],
    report_to=cfg["train"]["report_to"],
    optim="paged_adamw_8bit"
)


# =========================
# Data collator
# =========================

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)


# =========================
# Train
# =========================

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
    data_collator=data_collator
)

trainer.train()


# =========================
# Save
# =========================

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("✅ Training finished")
