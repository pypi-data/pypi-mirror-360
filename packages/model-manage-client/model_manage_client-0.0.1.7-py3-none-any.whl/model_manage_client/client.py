import logging
import os
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class AgentDefaults:
    agent_labels: list = None
    support_models: dict = None
    agent_features: dict = None
    agent_icon_url: str = None
    agent_description: str = None
    agent_api_version: str = "v1"
    has_site: bool = False
    multilangs: dict = None

    def __post_init__(self):
        if self.support_models is None:
            self.support_models = {
                "models": {"all": ["llm", "text-embedding", "rerank"]},
                "required": {"all": ["llm"]},
            }
        if self.agent_features is None:
            self.agent_features = {"show_anonymous": True}
        if self.agent_icon_url is None:
            self.agent_icon_url = ""
        if self.agent_description is None:
            self.agent_description = ""
        if self.agent_api_version is None:
            self.agent_api_version = "v1"
        if self.multilangs is None:
            self.multilangs = {}
        if self.has_site is None:
            self.has_site = True


class ModelManageClient:
    def __init__(self, base_url: str, client_token: str):
        if not base_url:
            base_url = os.getenv("MODEL_MANAGE_URL")
        self.base_url = base_url if base_url.endswith("/v1.0") else base_url + "/v1.0"
        if not client_token:
            client_token = os.getenv("CLIENT_TOKEN")
        self.client_token = client_token

    def _send_request(
        self,
        method,
        endpoint,
        headers=None,
        params=None,
        json=None,
        stream=False,
    ):
        new_headers = {
            "Authorization": f"Bearer {self.client_token}",
            "Content-Type": "application/json",
        }

        if headers:
            new_headers.update(headers)

        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=json, params=params, headers=new_headers, stream=stream)

        return response

    def register_agent(self, agent_name, agent_id, agent_url, **kwargs):
        required_params = {"agent_name": agent_name, "agent_id": agent_id, "agent_url": agent_url}
        for param_name, param_value in required_params.items():
            if not param_value:
                raise ValueError(f"{param_name} is required")

        # default values
        defaults = AgentDefaults(**kwargs)

        args = {
            "agent_name": agent_name,
            "agent_id": agent_id,
            "agent_url": agent_url,
            "agent_labels": defaults.agent_labels,
            "support_models": defaults.support_models,
            "agent_features": defaults.agent_features,
            "has_site": defaults.has_site,
            **{k: v for k, v in kwargs.items() if k in AgentDefaults.__dataclass_fields__},
        }
        response = self._send_request("POST", "/agents", json=args)
        if response.status_code != 200:
            raise ValueError(f"register agent failed: {response.text}")
        logger.info("register agent success......")

    def update_agent(self, agent_name, agent_url: str = None, **kwargs):
        """
        update agent info
        """
        if not agent_name:
            raise ValueError("agent_name is required")
        args = {
            **{k: v for k, v in kwargs.items() if k in AgentDefaults.__dataclass_fields__},
        }
        if agent_url:
            args["agent_url"] = agent_url

        response = self._send_request("PUT", f"/agents/{agent_name}", json=args)
        if response.status_code != 200:
            raise ValueError(f"update agent failed: {response.text}")
        logger.info("update agent success......")

    def get_agent_site(self, agent_name) -> dict:
        if not agent_name:
            raise ValueError("agent_name is required")
        response = self._send_request("GET", "/agents/site", params={"agent_name": agent_name})
        if response.status_code != 200:
            raise ValueError(f"get agent site failed: {response.text}")
        return response.json()

    def get_agent(self, agent_name):
        if not agent_name:
            raise ValueError("agent_name is required")

        response = self._send_request("GET", "/agents", params={"agent_name": agent_name})
        if response.status_code != 200 and response.status_code != 404:
            raise ValueError(f"get agent failed: {response.text}")
        if response.status_code == 404:
            return None
        return response.json()

    def get_model_credentials(
        self,
        agent_name: str,
        model: str,
        provider: str,
        model_type: str,
        tenent_id: str,
    ) -> dict:
        required_params = {
            "provider": provider,
            "model_type": model_type,
            "model": model,
            "agent_name": agent_name,
            "tenent_id": tenent_id,
        }
        for param_name, param_value in required_params.items():
            if not param_value:
                raise ValueError(f"{param_name} is required")

        params = {
            "agent_name": agent_name,
            "model": model,
            "model_type": model_type,
        }

        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            "GET",
            f"/agents/model-providers/{provider}/models/credentials",
            params=params,
            headers=header,
        )

        if response.status_code != 200:
            raise ValueError(f"get model credentials failed: {response.text}")
        return response.json()

    def get_provider_credential(
        self,
        agent_name: str,
        provider: str,
        tenent_id: str,
    ) -> dict:
        required_params = {"provider": provider, "agent_name": agent_name, "tenent_id": tenent_id}
        for param_name, param_value in required_params.items():
            if not param_value:
                raise ValueError(f"{param_name} is required")

        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            method="GET",
            endpoint=f"/agents/model-providers/{provider}/credentials",
            headers=header,
            params={"agent_name": agent_name},
        )
        if response.status_code != 200:
            raise ValueError(f"get provider credential failed: {response.text}")
        return response.json()

    def get_provider_or_model_credential(
        self,
        agent_name: str,
        provider: str,
        model: str,
        model_type: str,
        tenent_id: str,
    ) -> dict:
        required_params = {
            "provider": provider,
            "model_type": model_type,
            "model": model,
            "agent_name": agent_name,
            "tenent_id": tenent_id,
        }
        for param_name, param_value in required_params.items():
            if not param_value:
                raise ValueError(f"{param_name} is required")

        params = {
            "provider": provider,
            "agent_name": agent_name,
            "model": model,
            "model_type": model_type,
        }

        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            "GET",
            "/agents/providerOrModel/credentials",
            params=params,
            headers=header,
        )

        if response.status_code != 200:
            raise ValueError(f"get model credentials failed: {response.text}")
        return response.json()

    def get_agent_models(self, agent_name: str, tenent_id: str) -> dict:
        if not agent_name:
            raise ValueError("agent_name is required")
        if not tenent_id:
            raise ValueError("tenent_id is required")

        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            "GET",
            "/agents/model/config",
            params={"agent_name": agent_name},
            headers=header,
        )
        if response.status_code != 200:
            raise ValueError(f"get agent models failed: {response.text}")
        return response.json()
