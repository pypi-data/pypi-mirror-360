from transformers import pipeline

# pip install transformers
# https://pytorch.org/get-started/locally/
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pipe = pipeline("text-generation", model="ibm-granite/granite-3b-code-base-128k")

# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("ibm-granite/granite-3b-code-base-128k")
model = AutoModelForCausalLM.from_pretrained("ibm-granite/granite-3b-code-base-128k")
model.eval()

device = "cpu"
input_text = "def generate():"
# tokenize the text
input_tokens = tokenizer(input_text, return_tensors="pt")
# transfer tokenized inputs to the device
for i in input_tokens:
    input_tokens[i] = input_tokens[i].to(device)
# generate output tokens
output = model.generate(**input_tokens)
# decode output tokens into text
output = tokenizer.batch_decode(output)
# loop over the batch to print, in this example the batch size is 1
for i in output:
    print(i)

