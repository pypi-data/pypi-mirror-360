from typing import Dict, Any, Optional
from ray.serve import Application
from ray.serve.handle import DeploymentHandle

from ray_embedding.dto import AppConfig, ModelDeploymentConfig
from ray_embedding.embedding_model import EmbeddingModel
import torch

from ray_embedding.model_router import ModelRouter


def build_model(model_config: ModelDeploymentConfig) -> DeploymentHandle:
    deployment_name = model_config.deployment
    model = model_config.model
    device = model_config.device
    backend = model_config.backend or "torch"
    matryoshka_dim = model_config.matryoshka_dim
    trust_remote_code = model_config.trust_remote_code or False
    model_kwargs = model_config.model_kwargs or {}
    if "torch_dtype" in model_kwargs:
        torch_dtype = model_kwargs["torch_dtype"].strip()
        if torch_dtype == "float16":
            model_kwargs["torch_dtype"] = torch.float16
        elif torch_dtype == "bfloat16":
            model_kwargs["torch_dtype"] = torch.bfloat16
        elif torch_dtype == "float32":
            model_kwargs["torch_dtype"] = torch.float32
        else:
            raise ValueError(f"Invalid torch_dtype: '{torch_dtype}'")

    deployment = EmbeddingModel.options(name=deployment_name).bind(model=model,
                                                                   device=device,
                                                                   backend=backend,
                                                                   matryoshka_dim=matryoshka_dim,
                                                                   trust_remote_code=trust_remote_code,
                                                                   model_kwargs=model_kwargs
                                                                   )
    return deployment

def build_app(args: AppConfig) -> Application:
    model_router, models = args.model_router, args.models
    assert model_router and models

    served_models = {model_config.model: build_model(model_config) for model_config in models}
    router = ModelRouter.options(name=model_router.deployment).bind(served_models)
    return router
