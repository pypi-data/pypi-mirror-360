# ray-embedding

A Python library for deploying SentenceTransformers models to a ray cluster. 
This tool encapsulates inference logic that uses SentenceTransformers 
to load any compatible embedding model from the Hugging Face hub and 
compute embeddings for input text.

This library is meant to be used with the [embedding-models Ray cluster](https://bitbucket.org/docorto/embedding-models/src/dev/).

Refer to this [Ray Serve deployment config](https://bitbucket.org/docorto/embedding-models/src/dev/serve-config/dev/serve-config.yaml) 
to see how this library is used.

### Supports the following backends

- pytorch-gpu
- pytorch-cpu

### Planned:
- onnx-gpu
- onnx-cpu
- openvino-cpu
- fastembed-onnx-cpu


