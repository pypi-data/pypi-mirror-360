# Oai2Ollama

This is a CLI tool that starts a server that wraps an OpenAI-compatible API and expose an Ollama-compatible API,
which is useful for providing custom models for coding agents that don't support custom OpenAI APIs but do support Ollama
(like GitHub Copilot for VS Code).

## Usage

Use can use `uvx` or `pipx` to directly use it:

```sh
uvx oai2ollama --help
```

```text
usage: oai2ollama.exe [-h] [--api-key str] [--base-url str]
options:
  -h, --help      show this help message and exit
  --api-key str   (required)
  --base-url str  (required)
```

Or you can use a `.env` file to set the environment variables:

```properties
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
```
