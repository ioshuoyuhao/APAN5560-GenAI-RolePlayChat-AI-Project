#!/usr/bin/env python
# coding: utf-8

# In[2]:


from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
import torch


# In[3]:


MODEL_NAME = "gpt2"        
OUTPUT_DIR = "./models/gpt2-roleplay"
MAX_LENGTH = 512


# In[4]:

#load the dataset from the Hugging Face dataset hub
dataset = load_dataset("hieunguyenminh/roleplay")

#split the dataset into train and test sets
split_dataset = dataset["train"].train_test_split(test_size=0.1, seed=42)

train_raw = split_dataset["train"]
eval_raw  = split_dataset["test"]

print("Train samples:", len(train_raw))
print("Eval samples:", len(eval_raw))
print(train_raw[0])


# In[5]:


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

tokenizer.pad_token = tokenizer.eos_token


# In[6]:

#tokenize the dataset
def tokenize_function(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
    )

#tokenize the train dataset
tokenized_train = train_raw.map(
    tokenize_function,
    batched=True,
    remove_columns=train_raw.column_names,
)

#tokenize the test dataset
tokenized_eval = eval_raw.map(
    tokenize_function,
    batched=True,
    remove_columns=eval_raw.column_names,
)

tokenized_train[0]


# In[7]:

#create a data collator for language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)


# In[8]:

#load the model for causal language modeling
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
#set the pad token id to the eos token id
model.config.pad_token_id = tokenizer.pad_token_id


# In[9]:


#set the training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=2,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    logging_steps=200,
    save_total_limit=2,
    prediction_loss_only=True,  
)


# In[10]:

#create a trainer for the model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

trainer


# In[11]:


trainer.train()


# In[12]:

#save the model and tokenizer
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Model saved to:", OUTPUT_DIR)


# In[13]:

#convert the notebook to a python script
get_ipython().system('jupyter nbconvert --to python Generative_AI_models.ipynb')


# In[ ]:




