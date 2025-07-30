# model-manage-client

A model-manage App Service-API Client, using for build a webapp by request Service-API

## Usage

First, install `model-manage-client` python sdk package:

```
pip install model-manage-client
```

Write your code with sdk:

- completion generate with `blocking` response_mode

```python
from model-manage-client import ModelManageClient

base_url = "model-manage service api url"
client_token = "your_client_token"

# Initialize CompletionClient
m_client = ModelManageClient(base_url, client_token)

# if bast_url and client_token not set, will get from env variable, like:
# base_url = os.getenv("MODEL_MANAGE_URL")
# client_token = os.getenv("CLIENT_TOKEN")

# Create Completion Message using CompletionClient
extra_params = {
    "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {"show_anonymous": False},
        "agent_label": "agent_label",
        "support_models": {
            "translate": ["llm", "text-embedding", "rerank"],
            "qa": ["llm", "text-embedding", "rerank"],
        },
        "multilangs": {"translate": {"zh_CN": "翻译", "en_US": "Translate"}},
}
 m_client.register_agent("agent_name", "agent_id", "agent_url", **extra_params)

 # Update agent
 params = {
        "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {"show_anonymous": True},
        "agent_label": "aaa",
        "support_models": {
            "translate": ["llm", "rerank"],
            "qa": ["llm", "text-embedding"],
        },
        "multilangs": {
            "translate": {"zh_CN": "翻译", "en_US": "Translate"},
            "qa": {"zh_CN": "问答", "en_US": "QA"},
        },
    }
# if don't update agent_url, just set agent_url=None
m_client.update_agent("agent_name", agent_url="http://localhost:8008", **params)

# get agent models
models = m_client.get_agent_models("agent_name", "tenant_id")
if models:
    print(models)

# response
{
  "reason_model": {
    "llm": {
      "provider": "tongyi",
      "model": "qwen-plus",
      "credentials": {
        "dashscope_api_key": "xxxx"
      }
    }
  },
  "embedding_model": {
    "provider": "azure_openai",
      "model": "text-embedding-3-small",
      "credentials": {
        "dashscope_api_key": "xxxx"
      }
  },
  "rerank_model": {
    "provider": "tongyi",
      "model": "gte-rerank",
      "credentials": {
        "dashscope_api_key": "xxxx"
      }
  }
}
```