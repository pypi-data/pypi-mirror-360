from client import ModelManageClient


def test_register():
    base_url = "http://localhost:5001"
    client_token = ""

    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    agent_info = m_client.get_agent("test")
    if agent_info:
        print(agent_info)

    # Create Completion Message using CompletionClient
    extra_params = {
        "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {"show_anonymous": False},
        "support_models": {
            "models": {
                "translate": ["llm", "text-embedding", "rerank"],
                "qa": ["llm", "text-embedding", "rerank"],
            }
        },
        "multilangs": {"translate": {"zh_CN": "翻译", "en_US": "Translate"}},
        "has_site": False,
    }
    m_client.register_agent("ccbbd", "ccbbd", "test", **extra_params)


def test_update_agent():
    base_url = "http://localhost:5001"
    client_token = ""
    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    agent_info = m_client.get_agent("casdq")
    if agent_info:
        print(agent_info)

    params = {
        "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {"show_anonymous": True},
        "agent_labels": ["label1", "label2"],
        "support_models": {
            "models": {
                "translate": ["llm", "text-embedding", "rerank"],
                "qa": ["llm", "text-embedding", "rerank"],
            }
        },
        "multilangs": {
            "translate": {"zh_CN": "翻译", "en_US": "Translate"},
            "qa": {"zh_CN": "问答", "en_US": "QA"},
        },
        "has_site": True,
    }
    m_client.update_agent("ccbbd", agent_url="http://localhost:8008", **params)


def get_agent_models():
    base_url = ""
    client_token = ""

    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    agent_info = m_client.get_agent("phm")
    if agent_info:
        print(agent_info)

    models = m_client.get_agent_models("phm", "1289a66b-5833-4ccd-830b-4b03ea1fc77a-axa.wise-paas.com.cn")
    if models:
        print(models)


def test_get_provider_credential():
    base_url = "https://api-am-ensaas.axa.wise-paas.com.cn"
    client_token = ""
    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    try:
        credential = m_client.get_provider_credential(
            "test",
            "tongyi",
            "test",
        )
        print(credential)
    except Exception as e:
        print(e)


def test_get_model_credentials():
    base_url = "http://localhost:5001"
    client_token = ""
    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    try:
        credential = m_client.get_model_credentials(
            "test",
            "gpt-4o-mini",
            "azure_openai",
            "llm",
            "test",
        )
        print(credential)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    test_update_agent()
