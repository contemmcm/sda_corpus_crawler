from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel

# Load the trained model and tokenizer
model_dir = "./gpt2-scratch"  # Replace with your actual model directory

tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
model = GPT2LMHeadModel.from_pretrained(model_dir)

# Create a text generation pipeline
text_generator = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
)

# Define the prompt
prompt = "Jesus é o caminho, a"

# Generate text
output = text_generator(
    prompt,
    max_length=100,
    num_return_sequences=1,
    no_repeat_ngram_size=2,
    top_k=50,
    top_p=0.95,
    temperature=1.0,
)

# Print the generated text
print(output[0]["generated_text"])
