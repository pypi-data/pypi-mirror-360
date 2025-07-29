import os
from crewplus.services.model_load_balancer import ModelLoadBalancer

model_balancer = None

def init_load_balancer():
    global model_balancer
    if model_balancer is None:
        config_path = os.getenv("MODEL_CONFIG_PATH", "config/models_config.json")
        model_balancer = ModelLoadBalancer(config_path)
        model_balancer.load_config()  # Load initial configuration synchronously

def get_model_balancer() -> ModelLoadBalancer:
    if model_balancer is None:
        raise RuntimeError("ModelLoadBalancer not initialized")
    return model_balancer
