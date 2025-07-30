# BorgLLM - LLM Integration and Management

**BorgLLM** is a Python library that facilitates the integration and management of Large Language Models (LLMs). It offers a unified, LangChain-compatible interface, supporting features such as automatic API key rotation, rate limit handling, and configurable provider fallback strategies.

## ✨ Key Features

- **🔄 Unified Interface**: Single API for multiple LLM providers
- **🔑 API Key Rotation**: Automatic round-robin rotation for multiple API keys
- **⚡ Rate Limit Handling**: Built-in 429 error handling with cooldown periods
- **🧠 LangChain Integration**: Seamless integration with LangChain framework
- **📝 Flexible Configuration**: Configure via `borg.yml` file optionally, environment variables, or programmatic API
- **🛡️ Provider Fallback**: Automatic switching to alternative providers/models in case of failures or rate limits
- **🔍 Virtual Providers**: Explicitly choose your fallback strategy or merge multiple providers and call them as a single provider seamlessly in your code

## 🚀 Getting Started

### Installation

```bash
pip install borgllm
```

### Basic Usage: `create_llm` (LangChain Compatible)

You can use BorgLLM with zero configuration with `create_llm`, the primary way to obtain a LangChain-compatible LLM instance from BorgLLM. It handles provider selection, API key management, and rate limiting automatically.

To use `create_llm`, you typically pass the `provider_name` in the format `provider:model`. If a default provider is set (via `borg.yml` or `set_default_provider`), you can omit the argument.

```python
from borgllm import BorgLLM, set_default_provider, create_llm
from langchain_core.messages import HumanMessage

# Explicitly specify provider and model
mistral_llm = create_llm("mistralai:mistral-large-latest", temperature=0.7)

# Choose any provider and model (list of supported models below)
anthropic_llm = create_llm("anthropic:claude-sonnet-4", temperature=0.7)
groq_llm = create_llm("groq:llama-3.3-70b-versatile", temperature=0.7)
openai_llm = create_llm("openai:gpt-4o", temperature=0.7)
featherless_llm = create_llm("featherless:NousResearch/Nous-Hermes-13b", temperature=0.7)

# It's just a ChatOpenAI instance
response = mistral_llm.invoke([HumanMessage(content="Hello, how are you?")])
print(f"Mistral Response: {response.content}")

# Hello, I am doing great! How can I help you today?
```

You can specify a default provider in one place, and then call `create_llm` without an argument to use it.

```py
set_default_provider("deepseek:deepseek-chat")

# And call create_llm without an argument
llm = create_llm()

response = llm.invoke([HumanMessage(content="Hello, how are you?")])
print(f"DeepSeek Response: {response.content}")
```

Or specify a custom configuration declaratively in `borg.yml` (optional).

```py
# use a custom provider, for example Ollama or LM Studio
custom_llm = create_llm("remote_gemma", temperature=0.7)
response = custom_llm.invoke([HumanMessage(content="Hello, how are you?")])
print(f"Remote Gemma Response: {response.content}")

# Or use a virtual provider (from borg.yml)
virtual_llm = create_llm("qwen-auto", temperature=0.7)
response = virtual_llm.invoke([HumanMessage(content="Hello, how are you?")])
print(f"Qwen Auto Response: {response.content}")
```

With `borg.yml` you can use BorgLLM to create a virtual provider that automatically falls back to the best model for the task, and switch providers when you hit a rate limit or exceed the context window. You can also use BorgLLM to create a custom provider for your own model or API. Example:

```yml
llm:
  providers:
    # You can use a local model, for example from Ollama or LM Studio
    - name: "local_qwen"
      base_url: "http://localhost:1234/v1"
      model: "qwen/qwen3-8b"
      temperature: 0.7
      max_tokens: 8192

    # It doesn't have to be local, it can be a cloud server you rented
    - name: "remote_gemma"
      base_url: "http://1.2.3.4:11434/v1"
      model: "google/gemma-2-27b"
      temperature: 0.7
      max_tokens: 32000


  virtual:
    - name: "qwen-auto"
      upstreams:
        # This virtual provider will first use groq which has a max context window of 6k tokens
        - name: "groq:qwen/qwen3-32b"
        # If a request exceeds 6k tokens or groq's rate limit is reached, it will use cerebras
        # which has a max context window of 128k tokens but is limited to 1M tokens per day.
        - name: "cerebras:qwen-3-32b"
        # If both are exhausted, it will use the local qwen model as a fallback until either is available again.
        - name: "local_qwen"
          

```

### Supported Models for `create_llm`

Below is a table of commonly used model names that can be passed to `create_llm`, using the `provider:model` format. You can use the provider's own model identifier for the `model_identifier` argument.

Supported providers:

| Provider Name | Prefix  | Environment Variable (Single Key) | Environment Variable (Multiple Keys) |
|---------------|----------------|-----------------------------------|--------------------------------------|
| Anthropic     | `anthropic`    | `ANTHROPIC_API_KEY`               | `ANTHROPIC_API_KEYS`                 |
| Anyscale      | `anyscale`     | `ANYSCALE_API_KEY`                | `ANYSCALE_API_KEYS`                  |
| Cerebras      | `cerebras`     | `CEREBRAS_API_KEY`                | `CEREBRAS_API_KEYS`                  |
| Cohere        | `cohere`       | `COHERE_API_KEY`                  | `COHERE_API_KEYS`                    |
| DeepInfra     | `deepinfra`    | `DEEPINFRA_API_KEY`               | `DEEPINFRA_API_KEYS`                 |
| DeepSeek      | `deepseek`     | `DEEPSEEK_API_KEY`                | `DEEPSEEK_API_KEYS`                  |
| Featherless   | `featherless`  | `FEATHERLESS_API_KEY`             | `FEATHERLESS_API_KEYS`               |
| Fireworks     | `fireworks`    | `FIREWORKS_API_KEY`               | `FIREWORKS_API_KEYS`                 |
| Google        | `google`       | `GOOGLE_API_KEY`                  | `GOOGLE_API_KEYS`                    |
| Groq          | `groq`         | `GROQ_API_KEY`                    | `GROQ_API_KEYS`                      |
| Mistral AI    | `mistralai`    | `MISTRALAI_API_KEY`               | `MISTRALAI_API_KEYS`                 |
| Novita        | `novita`       | `NOVITA_API_KEY`                  | `NOVITA_API_KEYS`                    |
| OpenAI        | `openai`       | `OPENAI_API_KEY`                  | `OPENAI_API_KEYS`                    |
| OpenRouter    | `openrouter`   | `OPENROUTER_API_KEY`              | `OPENROUTER_API_KEYS`                |
| Perplexity    | `perplexity`   | `PERPLEXITY_API_KEY`              | `PERPLEXITY_API_KEYS`                |
| Qwen          | `qwen`         | `QWEN_API_KEY`                    | `QWEN_API_KEYS`                      |
| Together AI   | `togetherai`   | `TOGETHERAI_API_KEY`              | `TOGETHERAI_API_KEYS`                |

This list includes both built-in models and some popular choices available through their respective APIs. You can find the full list of models for each provider on their respective websites.

| Provider      | Model                      | Description                                                          |
| :------------ | :-------------------------------------------- | :------------------------------------------------------------------- |
| `anthropic`   | `anthropic:claude-3-5-sonnet-20240620`        | Specific dated version of Claude 3.5 Sonnet.                         |
| `anthropic`   | `anthropic:claude-3.7-sonnet`                 | A powerful, general-purpose model with hybrid reasoning.             |
| `anthropic`   | `anthropic:claude-sonnet-4`                   | Balanced model with strong capabilities for demanding applications.  |
| `deepseek`    | `deepseek:deepseek-chat`                      | DeepSeek's latest chat model aka V3.                                        |
| `deepseek`    | `deepseek:deepseek-reasoner`                  | DeepSeek's latest reasoning model aka R1.                                  |
| `featherless` | `featherless:meta-llama/Meta-Llama-3.1-8B-Instruct` | Featherless AI's Meta Llama 3.1 8B Instruct model. Featherless supports any public open-weight model from Hugging Face, and private models if loaded in Featherless. |
| `google`      | `google:gemini-2.5-flash-lite`                | Most cost-efficient and fastest in the 2.5 series.                   |
| `google`      | `google:gemini-2.5-flash`                     | Optimized for speed and high-volume, real-time applications.         |
| `google`      | `google:gemini-2.5-pro`                       | Google's most capable model for complex tasks.                       |
| `groq`        | `groq:llama-3.1-8b-instant`                   | Faster, smaller Llama 3.1 model.                                     |
| `groq`        | `groq:llama-3.3-70b-versatile`                | Llama 3.1, optimized for speed on Groq hardware.                     |
| `groq`        | `groq:llama3-8b-8192`                         | Default Llama 3 8B model.                                            |
| `groq`        | `groq:mixtral-8x22b-instruct`                 | Mixture-of-Experts model for efficiency and performance.             |
| `mistralai`   | `mistralai:devstral-small-latest`             | Mistral's agentic model.                                             |
| `mistralai`   | `mistralai:ministral-3b-latest`               | Mistral's tiny model.                                                |
| `mistralai`   | `mistralai:mistral-large-latest`              | Mistral's latest large model.                                        |
| `mistralai`   | `mistralai:mistral-medium-latest`             | Mistral's latest medium model.                                       |
| `mistralai`   | `mistralai:mistral-small-latest`              | Mistral's latest small model.                                        |
| `openai`      | `openai:gpt-4.1-mini`                         | Smaller variant of GPT-4.1.                                          |
| `openai`      | `openai:gpt-4.1-nano`                         | Even smaller, highly efficient GPT-4.1 model.                        |
| `openai`      | `openai:gpt-4.1`                              | A key rolling update/specific version in 2025.                       |
| `openai`      | `openai:gpt-4o-mini`                          | A compact and faster version of GPT-4o.                              |
| `openai`      | `openai:gpt-4o`                               | OpenAI's latest flagship multimodal model.                           |
| `openai`      | `openai:o3-mini`                              | Smaller, faster version of O3.                                       |
| `openai`      | `openai:o3`                                   | Focus on advanced reasoning and complex tasks.                       |
| `openai`      | `openai:o4-mini`                              | High performance, often for advanced tasks.                          |
| `openrouter`  | `openrouter:minimax/minimax-m1`               | MiniMax M1 model available via OpenRouter.                           |
| `openrouter`  | `openrouter:mistralai/mistral-7b-instruct`    | Mistral 7B Instruct model via OpenRouter.                            |
| `openrouter`  | `openrouter:qwen/qwen3-30b-a3b`               | Qwen3 30B A3B model available via OpenRouter.                        |
| `openrouter`  | `openrouter:qwen/qwen3-32b`                   | Qwen3 32B model available via OpenRouter.                            |
| `openrouter`  | `openrouter:qwen/qwq-32b:free`                | Free version of QwQ 32B via OpenRouter.                              |
| `perplexity`  | `perplexity:llama-3-sonar-small-32k-online`   | Default Llama 3 Sonar model with 32k context and online access.      |
| `perplexity`  | `perplexity:llama-3.1-70b-instruct`           | Llama 3.1 70B instruct model from Perplexity.                        |
| `perplexity`  | `perplexity:llama-3.1-sonar-large-online`     | Perplexity's premium research-focused model with web access.         |
| `perplexity`  | `perplexity:llama-3.1-sonar-small-online`     | Smaller, faster online model from Perplexity.                        |

### Configuration Prioritization and `borg.yml`

BorgLLM applies configuration settings in a specific order of precedence, from highest to lowest:

1.  **Programmatic Configuration (`set_default_provider`, `BorgLLM.get_instance()` parameters):** Settings applied directly in your Python code will always override others.
2.  **`borg.yml` File:** This file (by default `borg.yaml` or `borg.yml` in the project root) is used to define and customize providers. It can **override** settings for built-in providers or **define entirely new custom providers**.
3.  **Environment Variables:** If no other configuration is found, BorgLLM will look for API keys in environment variables (e.g., `OPENAI_API_KEY`). Built-in providers automatically pick up keys from these.

#### `borg.yml` Structure and Usage

The `borg.yml` file is powerful for defining your LLM ecosystem. It can configure built-in providers, add custom providers, and set up advanced features like virtual providers and API key rotation.

```yaml
llm:
  providers:
    - name: "custom-provider-1" # Generic name for a custom provider
      base_url: "http://localhost:8000/v1" # Example of a local or internal API endpoint
      model: "/models/your-local-model" # Example of a model identifier (example for vLLM)
      api_key: "sk-example" # Example for a dummy or local API key
      temperature: 0.7
      max_tokens: 4096 # Used to manage virtual provider strategies

    - name: "custom-provider-2" # Another generic custom provider
      base_url: "https://api.example.com/v1" # Example public API endpoint
      model: "example-model-a" # Example model name
      api_key: "${YOUR_EXAMPLE_API_KEY}"
      temperature: 0.7
      max_tokens: 1000000

    - name: "custom-provider-3" # Another generic custom provider
      base_url: "https://api.another-example.com/openai/v1" # Example public API endpoint
      model: "example/model-b" # Example model name
      api_key: "${YOUR_ANOTHER_EXAMPLE_API_KEY}"
      temperature: 0.7
      max_tokens: 6000

    - name: "local_qwen"
      base_url: "http://localhost:1234/v1"
      model: "qwen/qwen3-8b"
      temperature: 0.7
      max_tokens: 8192

    - name: "remote_gemma"
      base_url: "http://1.2.3.4:11434/v1"
      model: "google/gemma-2-27b"
      temperature: 0.7
      max_tokens: 32000

  virtual:
    - name: "auto-fallback-model" # Generic virtual provider name
      upstreams:
        - name: "custom-provider-1" # You can mix both custom and built-in providers
        - name: "openai:gpt-4o"

    - name: "another-auto-fallback" # Another generic virtual provider name
      upstreams:
        - name: "custom-provider-2"
        - name: "custom-provider-3"
  
    - name: "qwen-auto"
      upstreams:
        # This virtual provider will first use groq which has a max context window of 6k tokens
        - name: "groq:qwen/qwen3-32b"
        # If a request exceeds 6k tokens or groq's rate limit is reached, it will use cerebras
        # which has a max context window of 128k tokens but is limited to 1M tokens per day.
        - name: "cerebras:qwen-3-32b"
        # If both are exhausted, it will use the local qwen model as a fallback until either is available again.
        - name: "local_qwen"

    
  # Sets a default model for create_llm(), i.e. if no model is specified
  default_model: "qwen-auto" 
  # you can override this in your code by calling set_default_provider("provider_name")
  # Or on a case-by-case basis by calling create_llm("provider_name", temperature=0.7)
```

### Advanced Usage

#### Accessing BorgLLM Instance

`BorgLLM` is designed as a singleton, ensuring a single, globally accessible instance throughout your application.

```python
from borgllm import BorgLLM

# Get the BorgLLM singleton instance
borgllm_instance = BorgLLM.get_instance()

# You can access providers and models configured through borg.yml or environment variables
# For example, to get a specific provider's configuration:
openai_provider_config = borgllm_instance.get_provider_config("openai")
if openai_provider_config:
    print(f"OpenAI Provider Base URL: {openai_provider_config.base_url}")

# To create an LLM without explicitly specifying the provider if a default is set:
# (Assuming 'openai' is set as default in borg.yml or programmatically)
default_llm = borgllm_instance.create_llm("gpt-4o", temperature=0.5) # Uses default provider
```

#### Programmatic Default Provider

You can programmatically set a default provider using `set_default_provider`. This programmatic setting takes the highest precedence over `borg.yml` and environment variables.

```python
from borgllm import set_default_provider, create_llm

# Set 'anthropic' as the default provider programmatically
set_default_provider("anthropic:claude-sonnet-4")

# Now, create_llm will use 'anthropic' as the default provider
# when a provider is not explicitly specified in the model_name.
default_llm = create_llm()
print(f"Default LLM created for: {llm.model_name}") # Should be 'anthropic:claude-sonnet-4'

# You can still explicitly request other providers:
openai_llm = create_llm("openai:gpt-4o")
print(f"Explicit LLM created for: {openai_llm_explicit.model_name}") # Should be 'openai:gpt-4o'
```

#### API Key Management and Rotation (Multiple Keys)

BorgLLM automatically handles API key rotation for providers where you've configured multiple keys in `borg.yml`.

```yaml
# borg.yml example with multiple keys for a generic API provider
providers:
  - name: "generic-api-provider" # Generic provider name
    base_url: "https://api.generic-provider.com/v1" # Example base URL
    model: "model-alpha" # Example model name directly under provider
    api_keys:
      - "sk-generic-key-prod-1"
      - "sk-generic-key-prod-2"
      - "sk-generic-key-prod-3" # BorgLLM will rotate between these keys
    temperature: 0.7
    max_tokens: 4096
```

When you make successive calls to `create_llm` (or `borgllm.get()`) for the same provider, BorgLLM will cycle through the available API keys in a round-robin fashion. This distributes the load and provides resilience against individual key rate limits.

#### Rate Limit Handling (429 Errors) and Provider Fallback

BorgLLM includes robust built-in handling for HTTP 429 (Too Many Requests) errors and a flexible fallback mechanism:

1.  **Individual Key Cooldown**: When a 429 error is encountered for a specific API key, that key is temporarily put on a cooldown period.
2.  **Key Rotation**: BorgLLM automatically switches to the next available API key for that provider.
3.  **Request Retry**: The original request is retried after a short delay or after switching keys.
4.  **Virtual Provider Fallback**: If you've defined `virtual` providers in `borg.yml`, and the primary upstream provider fails (e.g., due to persistent 429 errors, general unavailability, or other configuration issues), BorgLLM will automatically attempt to use the next provider/model in the `upstreams` list. This provides a powerful way to build highly resilient applications.

This comprehensive approach ensures your application gracefully handles rate limits and provider outages, maintaining service continuity and optimizing cost/performance by leveraging multiple configurations.

For example, you can choose a cheap provider who provides a small context window, and use a more expensive provider who provides a larger context window as a fallback if the request is too large. Or a cheap and unreliable provider coupled with a more reliable one.

You can also use virtual providers recursively to create an even more complex fallback strategy declaratively without modifying your application code.

### License

The BorgLLM project is planned to be open-sourced soon under MIT license, explicit permission is currently required for any use, distribution, or modification of the code. Permission is granted to use this package for personal and non-commercial use, no support and no warranty provided.

### Copyright

Copyright © 2025 [Omar Kamali](https://omarkama.li). All rights reserved.

---

**Happy coding with BorgLLM!** 🚀 