import asyncio
import logging
import time
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException
from ray import serve

from ray_embedding.dto import EmbeddingResponse, EmbeddingRequest, DeployedModel

web_api = FastAPI(title="Ray Embeddings - OpenAI-compatible API")

@serve.deployment
@serve.ingress(web_api)
class EmbeddingService:
    def __init__(self, served_models: Dict[str, DeployedModel]):
        assert served_models, "models cannot be empty"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.served_models = served_models
        self.available_models = [
            {"id": str(item),
             "object": "model",
             "created": int(time.time()),
             "owned_by": "openai",
             "permission": []} for item in self.served_models.keys()
        ]
        self.logger.info(f"Successfully registered models: {self.available_models}")

    async def _compute_embeddings_from_resized_batches(self, model: str, inputs: List[str], dimensions: Optional[int] = None):
        assert model in self.served_models
        model_handle = self.served_models[model].deployment_handle
        self.logger.info(f"Model handle: {model_handle} ")
        batch_size = self.served_models[model].batch_size
        num_retries = self.served_models[model].num_retries

        # Resize the inputs into batch_size items, and dispatch in parallel
        batches = [inputs[i:i+batch_size] for i in range(0, len(inputs), batch_size)]
        if len(inputs) > batch_size:
            self.logger.info(f"Original input is greater than {batch_size}. "
                             f"It was resized to {len(batches)} mini-batches of size {batch_size}")
        tasks = [model_handle.remote(batch, dimensions) for batch in batches]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Retry any failed model calls
        for i, result in enumerate(all_results):
            if isinstance(result, Exception):
                retries = 0
                while retries < num_retries:
                    try:
                        all_results[i] = await model_handle.remote(batches[i], dimensions)
                    except Exception as e:
                        self.logger.warning(e)
                    finally:
                        retries += 1
                    if not isinstance(all_results[i], Exception):
                        break

                if retries >= num_retries and isinstance(all_results[i], Exception):
                    raise all_results[i]

        # Flatten the results because all_results is a list of lists
        self.logger.info(f"Successfully computed embeddings from {len(batches)} mini-batches")
        return [emb for result in all_results for emb in result]

    @web_api.post("/v1/embeddings", response_model=EmbeddingResponse)
    async def compute_embeddings(self, request: EmbeddingRequest):
        try:
            inputs = request.input if isinstance(request.input, list) else [request.input]
            self.logger.info(f"Received input of size {len(inputs)} text chunks")
            embeddings = await self._compute_embeddings_from_resized_batches(request.model, inputs, request.dimensions)
            response_data = [
                {"index": idx, "embedding": emb}
                for idx, emb in enumerate(embeddings)
            ]
            return EmbeddingResponse(object="list", data=response_data, model=request.model)
        except Exception as e:
            self.logger.error(f"Failed to create embeddings: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @web_api.get("/v1/models")
    async def list_models(self):
        """Returns the list of available models in OpenAI-compatible format."""
        return {"object": "list", "data": self.available_models}