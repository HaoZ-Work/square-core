import logging
import time
from functools import lru_cache
from typing import Dict, List

import requests

from skill_manager.routers import client_credentials
from skill_manager.settings import ModelManagementSettings

logger = logging.getLogger(__name__)


class ModelManagementClient:
    def __init__(self) -> None:
        self.settings = ModelManagementSettings()

        # HACK: Check if we are accessing the model api via the docker network, i.e. via
        # the service name, or via the internet.
        # For access via docker network, the requests are not routed via traefik, i.e.
        # the `/models` is not required
        if self.settings.model_api_url.startswith("https://"):
            self.settings.model_api_url += "/models"

    def deploy_model(
        self,
        model_name: str,
        model_type: str,
        identifier: str = None,
        disable_gpu: bool = True,
        batch_size: int = 1,
        max_input: int = 512,
        model_class="from_config",
    ) -> Dict[str, str]:
        """Deploys a model using the models managment api."""

        url = f"{self.settings.model_api_url}/deploy"
        token = client_credentials()
        logger.info(
            "Requesting deployment of model={} of model_type={} via {}".format(
                model_name, model_type, url
            )
        )

        response = requests.post(
            url=url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "identifier": identifier
                if identifier
                else model_name.replace("/", "-"),
                "model_name": model_name,
                "model_type": model_type,
                "disable_gpu": disable_gpu,
                "batch_size": batch_size,
                "max_input": max_input,
                "model_class": model_class,
            },
            verify=False,
        )

        logger.info("deploy model response: {}".format(response.content))
        response.raise_for_status()

        return response.json()

    def get_deployed_models(self) -> Dict[str, str]:
        """Returns a dict mapping model names to types that are currently deployed."""
        token = client_credentials()
        response = requests.get(
            f"{self.settings.model_api_url}/deployed-models",
            headers=dict(Authorization=f"Bearer {token}"),
        )
        logger.debug("get deployed models: {}".format(response.text))

        response.raise_for_status()

        deployed_models = response.json()
        deployed_models = {dm["model_name"]: dm["model_type"] for dm in deployed_models}

        return deployed_models

    def get_models_in_deployment(self) -> Dict[str, str]:
        """Returns dict mapping of model names to types are currently beeing deployed."""
        token = client_credentials()
        response = requests.get(
            f"{self.settings.model_api_url}/task",
            headers=dict(Authorization=f"Bearer {token}"),
        )
        logger.debug("get running tasks {}".format(response.text))

        response.raise_for_status()

        running_tasks = response.json()
        models_in_deployment = {}
        for worker2tasks in running_tasks.values():
            for tasks in worker2tasks.values():
                for task in tasks:
                    if task["name"] == "tasks.tasks.deploy_task":
                        model_name = task["args"][0]["MODEL_NAME"]
                        model_type = task["args"][0]["MODEL_TYPE"]
                        models_in_deployment[model_name] = model_type

        return models_in_deployment

    def deploy_model_if_not_exists(self, default_skill_args: Dict):
        """Deploys a model if it is not deployed and not currently deploying."""
        model_name = default_skill_args.get("base_model")
        if not model_name:
            logger.info("No base_model in the skill args. Nothing to deploy.")
            return
        model_type = "adapter" if "adapter" in default_skill_args else "transformer"
        logger.info(
            "Checking if model={} with model_type={} is already deployed.".format(
                model_name, model_type
            )
        )

        deployed_models = self.get_deployed_models()
        if deployed_models.get(model_name, "") == model_type:
            logger.info(
                "model={} with model_type={} is already deployed.".format(
                    model_name, model_type
                )
            )
            return

        currently_deploying_models = self.get_models_in_deployment()
        if currently_deploying_models.get(model_name, "") == model_type:
            logger.info(
                "model={} with model_type={} is in deployment.".format(
                    model_name, model_type
                )
            )
            return

        logger.info(
            "model={} with model_type={} is not deployed. Starting deployment.".format(
                model_name, model_type
            )
        )
        self.deploy_model(model_name=model_name, model_type=model_type)
