import logging
import os.path
import time
from typing import Optional, Dict, Any, List, Union

import torch
from pynvml import nvmlInit, nvmlDeviceGetCount
from ray import serve
from sentence_transformers import SentenceTransformer


@serve.deployment
class EmbeddingModel:
    def __init__(self, model: str, served_model_name: Optional[str] = None,
                 device: Optional[str] = None, backend: Optional[str] = "torch",
                 matryoshka_dim: Optional[int] = None, trust_remote_code: Optional[bool] = False,
                 model_kwargs: Dict[str, Any] = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.served_model_name = served_model_name or os.path.basename(self.model)
        self.init_device = device
        if self.init_device is None or self.init_device == "auto":
            self.init_device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.init_device == "cuda":
            self.wait_for_cuda()
        self.torch_device = torch.device(self.init_device)
        self.backend = backend or "torch"
        self.matryoshka_dim = matryoshka_dim
        self.trust_remote_code = trust_remote_code or False
        self.model_kwargs = model_kwargs or {}
        self.logger.info(f"Initializing embedding model: {self.model}")
        self.embedding_model = SentenceTransformer(self.model, device=self.init_device, backend=self.backend,
                                                   trust_remote_code=self.trust_remote_code,
                                                   model_kwargs=self.model_kwargs)

        self.logger.info(f"Successfully initialized embedding model {self.model} using device {self.torch_device}")

    async def __call__(self, text: Union[str, List[str]], dimensions: Optional[int] = None):
        """Compute embeddings for the input text using the loaded model."""
        if isinstance(text, str):
            text = [text]
        truncate_dim = dimensions or self.matryoshka_dim

        # Compute embeddings and convert to a PyTorch tensor on the GPU
        embeddings = self.embedding_model.encode(
            text, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False,
        ).to(self.torch_device)

        if truncate_dim is not None:
            # Truncate and re-normalize the embeddings
            embeddings = embeddings[:, :truncate_dim]
            embeddings = embeddings / torch.norm(embeddings, dim=1, keepdim=True)

        # Move all embeddings to CPU at once before conversion
        embeddings = embeddings.cpu().tolist()
        return embeddings


    def wait_for_cuda(self, wait: int = 10):
        if self.init_device == "cuda" and not torch.cuda.is_available():
            time.sleep(wait)
        self.check_health()

    def check_health(self):
        if self.init_device == "cuda":
            # Even though CUDA was available at init time,
            # CUDA can become unavailable - this is a known problem in AWS EC2
            # https://github.com/ray-project/ray/issues/49594
            try:
                nvmlInit()
                assert nvmlDeviceGetCount() >= 1
            except:
                raise RuntimeError("CUDA device is not available")
