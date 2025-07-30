# TLDR

The simplest way to run: using uvx (you need to `pip install uv` first):

For local model (will install torch and transformers, can be slow):

```
uvx --from 'photoprism_captioner[local]' photoprism_captioner --backend local --auth-token MY_PHOTOPRISM_AUTH_TOKEN --model Salesforce/blip-image-captioning-large --photoprism-url="https://my.photoprism.qwe.org"
```

For Ollama model (self-hosted LLM models provider):

```
uvx --from 'photoprism_captioner[remote]' photoprism_captioner --backend remote --auth-token MY_PHOTOPRISM_AUTH_TOKEN --model ollama/gemma3 --api-base http://my-ollama-instance:11434 --photoprism-url="https://my.photoprism.qwe.org"
```

For OpenAI model (Don't forget to set OPENAI_API_KEY environment variable):

```
uvx --from 'photoprism_captioner[remote]' photoprism_captioner --backend remote --auth-token MY_PHOTOPRISM_AUTH_TOKEN --model gpt-4o-2024-08-06 --api-base https://api.openai.com/v1/chat/completions --photoprism-url="https://my.photoprism.qwe.org"
```
