!pip install -U langchain langgraph datasets pandas torch transformers[torch] python-dotenv peft
import os
from getpass import getpass
os.environ["HF_TOKEN"]=getpass("Enter hugging face api key:")

HF_TOKEN=os.environ.get("HF_TOKEN")
from transformers import AutoModelForCausalLM,AutoTokenizer
from huggingface_hub import login
login(token=HF_TOKEN)
model_name="distilgpt2"
tokenizer=AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token=tokenizer.eos_token
tokenizer.padding_side="right"
model=AutoModelForCausalLM.from_pretrained(model_name)
model

text="ஒரு நாள்"
inputs=tokenizer(text,return_tensors="pt")
output=model.generate(inputs.input_ids,max_new_tokens=100)
print(tokenizer.decode(output[0],skip_special_tokens=True))

from datasets import load_dataset
raw_data=load_dataset("tniranjan/aitamilnadu_tamil_stories_no_instruct", split="train[:1000]")
data=raw_data.train_test_split(train_size=0.95)
data

tokenizer.pad_token=tokenizer.eos_token
def preprocess_batch(batch):
  return tokenizer(batch["text"],truncation=True,padding=True,max_length=200)
tokenized_dataset=data.map(preprocess_batch,batched=True,batch_size=4,remove_columns=data["train"].column_names)

from transformers import DataCollatorForLanguageModeling
data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False)

from peft import get_peft_model,LoraConfig,TaskType
lora_config=LoraConfig(
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model=get_peft_model(model,lora_config)
model.print_trainable_parameters()
model.train()

from torch.optim import AdamW
optimizer=AdamW(model.parameters(),lr=1e-5)
from transformers import TrainingArguments,Trainer
training_args=TrainingArguments(
output_dir="./output",
save_steps=500,
learning_rate=1e-5,
weight_decay=0.01,
num_train_epochs=20,
per_device_train_batch_size=2,
per_device_eval_batch_size=2,
logging_steps=50,
logging_dir="./logs",
resume_from_checkpoint=True
)
trainer=Trainer(
    model=model,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    args=training_args,
    data_collator=data_collator,
    optimizers=(optimizer,None))
trainer.train()

text = "ஒரு நாள்"
inputs = tokenizer(text, return_tensors="pt")
# Generate story
output = model.generate(inputs.input_ids, max_new_tokens=100)
print(tokenizer.decode(output[0], skip_special_tokens=True))

from google.colab import drive
drive.mount('/content/drive')

from transformers import AutoTokenizer,AutoModelForCausalLM
trainer.save_model("/content/drive/My Drive/fine_tuned_distilgpt2_tamil")
tokenizer.save_pretrained("/content/drive/My Drive/fine_tuned_distilgpt2_tamil")

