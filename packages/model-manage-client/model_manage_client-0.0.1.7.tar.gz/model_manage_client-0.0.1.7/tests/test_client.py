from model_manage_client.client import ModelManageClient


def test_register():
    base_url = "test_url"
    client_token = "test_token"

    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    # Create Completion Message using CompletionClient
    extra_params = {
        "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {},
    }
    m_client.register_agent("license", "license123", "test", **extra_params)


if __name__ == "__main__":
    test_register()
