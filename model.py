# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Orenguteng/Llama-3-8B-Lexi-Uncensored")
model = AutoModelForCausalLM.from_pretrained("Orenguteng/Llama-3-8B-Le"
                                             "xi-Uncensored")