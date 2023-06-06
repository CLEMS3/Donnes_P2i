import openai

openai.api_key = "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"

print(openai.ChatCompletion.create(
  model = "gpt-3.5-turbo",
  temperature = 0.5,
  max_tokens = 1000,
  messages = [
    {"role": "user", "content": "Génère un texte sur l'INSA de Lyon"},
  ]
))
