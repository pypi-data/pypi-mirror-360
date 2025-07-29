import os
from .model_load_balancer import ModelLoadBalancer

model_balancer = None

def init_load_balancer(config_path: str = None):
    global model_balancer
    if model_balancer is None:
        # Use parameter if provided, otherwise check env var, then default
        final_config_path = config_path or os.getenv(
            "MODEL_CONFIG_PATH", 
            "config/models_config.json"  # Fixed default path
        )
        model_balancer = ModelLoadBalancer(final_config_path)
        model_balancer.load_config()  # Load initial configuration synchronously

def get_model_balancer() -> ModelLoadBalancer:
    if model_balancer is None:
        raise RuntimeError("ModelLoadBalancer not initialized")
    return model_balancer
