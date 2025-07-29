# toksum

A comprehensive Python library for counting tokens across 300+ Large Language Models (LLMs) from 34+ providers.

[![PyPI version](https://badge.fury.io/py/toksum.svg)](https://badge.fury.io/py/toksum)
[![Python Support](https://img.shields.io/pypi/pyversions/toksum.svg)](https://pypi.org/project/toksum/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features


- **🎯 Production Ready v1.0.1**: Comprehensive support for 300+ models across 34+ providers including OpenAI, Anthropic, Google, Meta, Mistral, Microsoft, Amazon, Nvidia, IBM, Salesforce, BigCode, Databricks, Voyage AI, and many more
- **Comprehensive Multi-LLM Support**: Count tokens for 300+ models across 34 providers including OpenAI, Anthropic, Google, Meta, Mistral, Microsoft, Amazon, Nvidia, IBM, Salesforce, BigCode, Databricks, Voyage AI, and many more
- **Accurate Tokenization**: Uses official tokenizers (tiktoken for OpenAI) and optimized approximations for all other providers
- **Chat Message Support**: Count tokens in chat/conversation format with proper message overhead calculation
- **Cost Estimation**: Estimate API costs based on token counts and current pricing
- **Easy to Use**: Simple API with both functional and object-oriented interfaces
- **Well Tested**: Comprehensive test suite with high coverage
- **Type Hints**: Full type annotation support for better IDE experience
- **Global Model Coverage**: Support for models optimized for Chinese, Russian, and other languages
- **Enterprise & Code Models**: Specialized support for enterprise AI models and code generation models

## Supported Models

### OpenAI Models (49 models)
- GPT-4 (all variants including gpt-4, gpt-4-32k, gpt-4-turbo, gpt-4o, gpt-4o-mini, etc.)
- **O1 Models** (o1-preview, o1-mini, o1-preview-2024-09-12, o1-mini-2024-09-12)
- **NEW: Vision Models** (gpt-4-vision, gpt-4-vision-preview-0409, gpt-4-vision-preview-1106)
- GPT-3.5 Turbo (all variants including instruct)
- Legacy models (text-davinci-003, text-davinci-002, gpt-3, etc.)
- Embedding models (text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large)

### Anthropic Models (27 models)
- Claude-3 (Opus, Sonnet, Haiku with full and short names)
- Claude-3.5 (Sonnet, Haiku 3.5, Computer Use models)
- Claude-2 (2.1, 2.0, **NEW: 2.1-200k, 2.1-100k**)
- Claude-1 (legacy models including 1.3, 1.3-100k)
- Claude Instant (all variants including **NEW: instant-2, instant-2.0**)

### Google Models (16 models)
- Gemini Pro, Gemini Pro Vision
- Gemini 1.5 Pro, Gemini 1.5 Flash (including latest variants)
- Gemini 2.0 (gemini-2.0-flash-exp, gemini-2.0-flash, gemini-exp-1206, gemini-exp-1121)
- Gemini 1.0 Pro, Gemini 1.0 Pro Vision
- Gemini Ultra
- **NEW: PaLM Models** (palm-2, palm-2-chat, palm-2-codechat)

### Meta Models (12 models)
- LLaMA-2 (7B, 13B, 70B)
- LLaMA-3 (8B, 70B)
- LLaMA-3.1 (8B, 70B, 405B)
- LLaMA-3.2 (1B, 3B)
- LLaMA-3.3 (70B, 70B-instruct)

### Mistral Models (10 models)
- Mistral (7B, Large, Medium, Small, Tiny)
- Mistral Large 2 (mistral-large-2, mistral-large-2407)
- Mixtral (8x7B, 8x22B)
- Legacy Mistral 8x7B

### Cohere Models (9 models)
- Command (standard, light, nightly)
- Command-R (standard, plus, **NEW: with 2024 variants**)

### xAI Models (4 models)
- Grok (1, 1.5, 2, beta)

### Alibaba Models (20 models)
- Qwen-1.5 series (0.5B to 110B parameters)
- Qwen-2 series (0.5B to 72B parameters)
- **NEW: Qwen-2.5** (qwen-2.5-72b, qwen-2.5-32b, qwen-2.5-14b, qwen-2.5-7b)
- Qwen-VL (vision-language variants)

### Baidu Models (8 models)
- ERNIE (4.0, 3.5, 3.0, Speed, Lite, Tiny)
- ERNIE Bot (standard and 4.0)

### Huawei Models (5 models)
- PanGu-α (2.6B, 13B, 200B)
- PanGu-Coder (15B and base)

### Yandex Models (4 models)
- YaLM (100B, 200B)
- YaGPT (1, 2)

### Stability AI Models (7 models)
- StableLM Alpha (3B, 7B base and tuned)
- StableLM Zephyr (3B)

### TII Models (6 models)
- Falcon (7B, 40B, 180B with instruct and chat variants)

### EleutherAI Models (12 models)
- GPT-Neo (125M, 1.3B, 2.7B)
- GPT-NeoX (20B)
- Pythia (70M to 12B)

### MosaicML/Databricks Models (8 models)
- MPT (7B, 30B with chat and instruct variants)
- DBRX (base and instruct)

### Replit Models (3 models)
- Replit Code (v1, v1.5, v2 - 3B parameters)

### MiniMax Models (5 models)
- ABAB (5.5 to 6.5 chat variants)

### Aleph Alpha Models (4 models)
- Luminous (Base, Extended, Supreme, Supreme Control)

### DeepSeek Models (10 models)
- DeepSeek-Coder (1.3B to 33B, instruct)
- DeepSeek-VL (1.3B, 7B)
- DeepSeek-LLM (7B, 67B)
- **NEW: DeepSeek V3** (deepseek-v3, deepseek-v3-base)

### Tsinghua KEG Lab Models (5 models)
- ChatGLM (6B variants: ChatGLM, ChatGLM2, ChatGLM3)
- GLM-4 (standard and vision)

### RWKV Models (7 models)
- RWKV-4 (169M to 14B parameters)
- RWKV-5 World

### Community Fine-tuned Models (13 models)
- Vicuna (7B, 13B, 33B)
- Alpaca (7B, 13B)
- WizardLM (7B, 13B, 30B)
- Orca Mini (3B, 7B, 13B)
- Zephyr (7B Alpha, Beta)

### Perplexity Models (5 models)
- PPLX (7B, 70B online and chat variants)
- CodeLlama 34B Instruct

### Hugging Face Models (5 models)
- Microsoft DialoGPT (medium, large)
- Facebook BlenderBot (400M, 1B, 3B variants)

### AI21 Models (4 models)
- Jurassic-2 (Light, Mid, Ultra, Jumbo Instruct)

### Together AI Models (3 models)
- RedPajama INCITE Chat (3B, 7B)
- Nous Hermes LLaMA2 13B

### Microsoft Models (4 models)
- **NEW: Phi Models** (phi-3-mini, phi-3-small, phi-3-medium, phi-3.5-mini)
- Optimized for coding and reasoning tasks
- Enterprise-ready AI models

### Amazon Models (3 models)
- **NEW: Titan Models** (titan-text-express, titan-text-lite, titan-embed-text)
- Enterprise-focused text generation and embedding
- AWS Bedrock integration

### Nvidia Models (2 models)
- **NEW: Nemotron Models** (nemotron-4-340b, nemotron-3-8b)
- Technical and scientific content optimization
- GPU-accelerated training

### IBM Models (3 models)
- **NEW: Granite Models** (granite-13b-chat, granite-13b-instruct, granite-20b-code)
- Enterprise AI with security and compliance focus
- Code generation and business applications

### Salesforce Models (3 models)
- **NEW: CodeGen Models** (codegen-16b, codegen-6b, codegen-2b)
- Specialized for code generation across multiple programming languages
- Open-source code understanding

### BigCode Models (3 models)
- **NEW: StarCoder Models** (starcoder, starcoder2-15b, starcoderbase)
- Multi-language code generation and understanding
- Trained on diverse programming languages

### Databricks Models (5 models)
- **NEW: Databricks Models** (dbrx-instruct, dbrx-base, dolly-v2-12b, dolly-v2-7b, dolly-v2-3b)
- High-quality instruction-following and base models

### Voyage AI Models (6 models)
- **NEW: Voyage AI Models** (voyage-2, voyage-large-2, voyage-code-2, voyage-finance-2, voyage-law-2, voyage-multilingual-2)
- State-of-the-art embedding models for various domains


**Total: 300+ models across 34+ providers**

## Installation

```bash
pip install toksum
```

### Optional Dependencies

For OpenAI models, you'll need `tiktoken`:
```bash
pip install tiktoken
```

For Anthropic models, the library uses built-in approximation (no additional dependencies required).

## Quick Start

```python
from toksum import count_tokens, TokenCounter

# Quick token counting
tokens = count_tokens("Hello, world!", "gpt-4")
print(f"Token count: {tokens}")

# Using TokenCounter class
counter = TokenCounter("gpt-4")
tokens = counter.count("Hello, world!")
print(f"Token count: {tokens}")
```

## Usage Examples

### Basic Token Counting

```python
from toksum import count_tokens

# Count tokens for different models
text = "The quick brown fox jumps over the lazy dog."

gpt4_tokens = count_tokens(text, "gpt-4")
gpt35_tokens = count_tokens(text, "gpt-3.5-turbo")
claude_tokens = count_tokens(text, "claude-3-opus-20240229")

print(f"GPT-4: {gpt4_tokens} tokens")
print(f"GPT-3.5: {gpt35_tokens} tokens") 
print(f"Claude-3 Opus: {claude_tokens} tokens")
```

### Using TokenCounter Class

```python
from toksum import TokenCounter

# Create a counter for a specific model
counter = TokenCounter("gpt-4")

# Count tokens for multiple texts
texts = [
    "Short text",
    "This is a longer text with more words and complexity.",
    "Very long text..." * 100
]

for text in texts:
    tokens = counter.count(text)
    print(f"'{text[:30]}...': {tokens} tokens")
```

### Chat Message Token Counting

```python
from toksum import TokenCounter

counter = TokenCounter("gpt-4")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."}
]

total_tokens = counter.count_messages(messages)
print(f"Total conversation tokens: {total_tokens}")
```

### Cost Estimation

```python
from toksum import count_tokens, estimate_cost

text = "Your text here..." * 1000  # Large text
model = "gpt-4"

tokens = count_tokens(text, model)
input_cost = estimate_cost(tokens, model, input_tokens=True)
output_cost = estimate_cost(tokens, model, input_tokens=False)

print(f"Tokens: {tokens}")
print(f"Estimated input cost: ${input_cost:.4f}")
print(f"Estimated output cost: ${output_cost:.4f}")
```

### List Supported Models

```python
from toksum import get_supported_models

models = get_supported_models()
print("Supported models:")
for provider, model_list in models.items():
    print(f"\n{provider.upper()}:")
    for model in model_list:
        print(f"  - {model}")
```

## API Reference

### Functions

#### `count_tokens(text: str, model: str) -> int`
Count tokens in text for a specific model.

**Parameters:**
- `text`: The text to count tokens for
- `model`: The model name (e.g., "gpt-4", "claude-3-opus-20240229")

**Returns:** Number of tokens as integer

#### `get_supported_models() -> Dict[str, List[str]]`
Get dictionary of supported models by provider.

**Returns:** Dictionary with provider names as keys and model lists as values

#### `estimate_cost(token_count: int, model: str, input_tokens: bool = True) -> float`
Estimate cost for given token count and model.

**Parameters:**
- `token_count`: Number of tokens
- `model`: Model name
- `input_tokens`: Whether tokens are input (True) or output (False)

**Returns:** Estimated cost in USD

### Classes

#### `TokenCounter(model: str)`
Token counter for a specific model.

**Methods:**
- `count(text: str) -> int`: Count tokens in text
- `count_messages(messages: List[Dict[str, str]]) -> int`: Count tokens in chat messages

### Exceptions

#### `UnsupportedModelError`
Raised when an unsupported model is specified.

#### `TokenizationError`
Raised when tokenization fails.

## How It Works

### OpenAI Models
Uses the official `tiktoken` library to get exact token counts using the same tokenizer as OpenAI's API.

### Anthropic Models
Uses a smart approximation algorithm based on:
- Character count analysis
- Whitespace and punctuation detection
- Anthropic's guidance of ~4 characters per token
- Adjustments for different text patterns

The approximation is typically within 10-20% of actual token counts for English text.

## Development

### Setup Development Environment

```bash
git clone https://github.com/kactlabs/toksum.git
cd toksum
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=toksum --cov-report=html
```

### Code Formatting

```bash
black toksum tests examples
```

### Type Checking

```bash
mypy toksum
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0 - 2025-01-06
- **🎯 MAJOR MILESTONE**: Achieved production-ready v1.0.0 status with 50+ additional models
- **Total Models**: Expanded to 300+ models across 32+ providers
- **New Model Categories Added:**
  - **GPT-4 Turbo & Embedding Series**: gpt-4-turbo-preview, gpt-4-0125-preview, text-embedding-ada-002, text-embedding-3-small/large, text-similarity models
  - **Claude 3 Opus & Sonnet Series**: claude-3-opus-20240229, claude-3-sonnet-20240229, with latest and short-name variants
  - **Gemini Pro Comprehensive Series**: gemini-pro, gemini-pro-vision, gemini-1.0-pro variants with vision support
  - **Llama 2 Chat & Llama 3 Instruct Series**: Complete chat and instruct model families including HuggingFace variants
  - **Mistral Instruct Series**: mistral-7b-instruct with version variants, mixtral-8x7b/8x22b-instruct
  - **Extended BigCode StarCoder**: starcoder2-3b/7b, starcoder-plus, starcoderbase variants
- **Enhanced Model Support**: Updated model counts - OpenAI (60), Anthropic (33), Google (22), Meta (25), Mistral (16), BigCode (9)
- **Production Quality**: 1000+ comprehensive test cases covering all model types, edge cases, and error scenarios
- **Specialized Tokenization**: Optimized approximations for reasoning, code, embedding, multilingual, and instruction-following models
- **Enterprise Ready**: Full backward compatibility, comprehensive error handling, and extensive documentation

### v0.9.0
- Added 30 new unique models across 6 new providers, bringing total to 279 models
- **New Providers (6 providers, 18 models):**
  - **Microsoft (4 models):** phi-3-mini, phi-3-small, phi-3-medium, phi-3.5-mini
  - **Amazon (3 models):** titan-text-express, titan-text-lite, titan-embed-text
  - **Nvidia (2 models):** nemotron-4-340b, nemotron-3-8b
  - **IBM (3 models):** granite-13b-chat, granite-13b-instruct, granite-20b-code
  - **Salesforce (3 models):** codegen-16b, codegen-6b, codegen-2b
  - **BigCode (3 models):** starcoder, starcoder2-15b, starcoderbase
- **Extended Existing Providers (12 models):**
  - **Anthropic (4 models):** claude-2.1-200k, claude-2.1-100k, claude-instant-2, claude-instant-2.0
  - **OpenAI (3 models):** gpt-4-vision, gpt-4-vision-preview-0409, gpt-4-vision-preview-1106
  - **Cohere (2 models):** command-r-plus-04-2024, command-r-plus-08-2024
  - **Google (3 models):** palm-2, palm-2-chat, palm-2-codechat
- **Comprehensive Testing:** Added 500+ new test cases for all new models
- **Provider-Specific Approximations:** Optimized tokenization for enterprise and code models
- **Enhanced Model Detection:** Improved provider detection logic for all new model categories
- **Enterprise & Code Model Support:** Specialized support for business AI and code generation models
- Updated model counts: OpenAI (49), Anthropic (27), Google (16), Cohere (9), Microsoft (4), Amazon (3), Nvidia (2), IBM (3), Salesforce (3), BigCode (3)

### v0.8.0
- Added 22 new cutting-edge models across 8 model categories, bringing total to 249 models
- **Latest Model Releases:**
  - **OpenAI O1 Models (4 models):** o1-preview, o1-mini, o1-preview-2024-09-12, o1-mini-2024-09-12
  - **Anthropic Claude 3.5 Haiku (2 models):** claude-3.5-haiku-20241022, claude-3-5-haiku-20241022
  - **Anthropic Computer Use (2 models):** claude-3-5-sonnet-20241022, claude-3.5-sonnet-computer-use
  - **Google Gemini 2.0 (4 models):** gemini-2.0-flash-exp, gemini-2.0-flash, gemini-exp-1206, gemini-exp-1121
  - **Meta Llama 3.3 (2 models):** llama-3.3-70b, llama-3.3-70b-instruct
  - **Mistral Large 2 (2 models):** mistral-large-2, mistral-large-2407
  - **DeepSeek V3 (2 models):** deepseek-v3, deepseek-v3-base
  - **Qwen 2.5 (4 models):** qwen-2.5-72b, qwen-2.5-32b, qwen-2.5-14b, qwen-2.5-7b
- **OpenAI O1 Support:** Full tokenization support using cl100k_base encoding for accurate token counting
- **Advanced Model Detection:** Enhanced provider detection logic to handle all new model categories
- **Comprehensive Testing:** Added 200+ new test cases specifically for v0.8.0 models
- **Technical Improvements:**
  - Provider-specific approximations for new model families
  - Chinese language optimization for Qwen 2.5 models
  - Code understanding for DeepSeek V3 models
  - Multimodal support for Gemini 2.0 models
  - Computer use model handling for Anthropic models
- Updated model counts: OpenAI (46), Anthropic (23), Google (13), Meta (12), Mistral (10), Alibaba (20), DeepSeek (10)

### v0.7.0
- Added 139 new models across 16 new providers, bringing total to 212+ models
- **New Providers:**
  - xAI: grok-1, grok-1.5, grok-2, grok-beta
  - Alibaba: qwen-1.5 series (0.5b to 110b), qwen-2 series, qwen-vl variants
  - Baidu: ernie-4.0, ernie-3.5, ernie-3.0, ernie-speed, ernie-lite, ernie-tiny, ernie-bot, ernie-bot-4
  - Huawei: pangu-alpha series (2.6b, 13b, 200b), pangu-coder variants
  - Yandex: yalm-100b, yalm-200b, yagpt, yagpt-2
  - Stability AI: stablelm-alpha, stablelm-base-alpha, stablelm-tuned-alpha, stablelm-zephyr variants
  - TII: falcon series (7b, 40b, 180b) with instruct and chat variants
  - EleutherAI: gpt-neo series, gpt-neox-20b, pythia series (70m to 12b)
  - MosaicML/Databricks: mpt series (7b, 30b) with chat/instruct variants, dbrx models
  - Replit: replit-code series (v1, v1.5, v2)
  - MiniMax: abab series (5.5 to 6.5) chat models
  - Aleph Alpha: luminous series (base, extended, supreme, supreme-control)
  - DeepSeek: deepseek-coder series, deepseek-vl series, deepseek-llm series
  - Tsinghua KEG Lab: chatglm series (6b variants), glm-4, glm-4v
  - RWKV: rwkv-4 series (169m to 14b), rwkv-5-world
  - Community Fine-tuned: vicuna, alpaca, wizardlm, orca-mini, zephyr variants
- Enhanced provider-specific tokenization approximations for all new providers
- Optimized approximations for Chinese models (Alibaba, Baidu, Huawei, MiniMax, Tsinghua)
- Optimized approximations for Russian models (Yandex)
- Specialized approximations for code models (Replit, DeepSeek-Coder, Huawei PanGu-Coder)
- Expanded to 26 total providers
- Total model support increased from 112 to 212+ models

### v0.6.0
- Type safety improvements and mypy compliance
- Enhanced exception handling with proper type annotations
- Improved conditional imports using TYPE_CHECKING pattern
- Added runtime checks for tokenizer initialization
- Full mypy compliance with better type hints throughout codebase

### v0.5.0
- Added 28 more models across 4 new providers:
  - Perplexity: pplx-7b-online, pplx-70b-online, pplx-7b-chat, pplx-70b-chat, codellama-34b-instruct
  - Hugging Face: microsoft/DialoGPT-medium, microsoft/DialoGPT-large, facebook/blenderbot variants
  - AI21: j2-light, j2-mid, j2-ultra, j2-jumbo-instruct
  - Together AI: RedPajama INCITE Chat models, Nous Hermes LLaMA2
  - Additional OpenAI legacy and embedding models
  - Additional Anthropic legacy models (Claude-1 series)
  - Additional Cohere model variants
- Enhanced case-insensitive model matching
- Expanded to 10 total providers
- Total model support increased to 112 models

### v0.4.0
- Added 30 more models across all providers:
  - OpenAI: gpt-4o-2024-08-06, gpt-4o-2024-11-20, gpt-4-1106-vision-preview, gpt-3.5-turbo-instruct
  - Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-instant (short names)
  - Google: gemini-1.5-pro-latest, gemini-1.5-flash-latest, gemini-1.0-pro, gemini-1.0-pro-vision, gemini-ultra
  - Meta: llama-3-8b, llama-3-70b, llama-3.1-8b, llama-3.1-70b, llama-3.1-405b, llama-3.2-1b, llama-3.2-3b
  - Mistral: mistral-large, mistral-medium, mistral-small, mistral-tiny, mixtral-8x7b, mixtral-8x22b
  - Cohere: command-light, command-nightly, command-r, command-r-plus
- Enhanced provider-specific tokenization approximations
- Total model support increased to 84 models

### v0.3.0
- Added 10 more models from new providers:
  - Google: gemini-pro, gemini-pro-vision, gemini-1.5-pro, gemini-1.5-flash
  - Meta: llama-2-7b, llama-2-13b, llama-2-70b
  - Mistral: mistral-7b, mistral-8x7b
  - Cohere: command
- Expanded to 6 total providers (OpenAI, Anthropic, Google, Meta, Mistral, Cohere)
- Enhanced approximation algorithms with provider-specific adjustments
- Total model support increased to 54 models

### v0.2.0
- Added 10 new models:
  - OpenAI: gpt-4-turbo, gpt-4-turbo-2024-04-09, gpt-4o, gpt-4o-2024-05-13, gpt-4o-mini, gpt-4o-mini-2024-07-18
  - Anthropic: claude-3.5-sonnet-20240620, claude-3.5-sonnet-20241022, claude-3.5-haiku-20241022, claude-3-5-sonnet-20240620
- Updated cost estimation for new models
- Enhanced model support (now 43 total models)

### v0.1.0
- Initial release
- Support for OpenAI GPT models and Anthropic Claude models
- Token counting for text and chat messages
- Cost estimation functionality
- Comprehensive test suite

## Acknowledgments

- [tiktoken](https://github.com/openai/tiktoken) for OpenAI tokenization
- [Anthropic](https://www.anthropic.com/) for Claude model guidance
- The open-source community for inspiration and best practices
