import requests
import time
import os
import json
from typing import Optional, Dict, Any, List
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)


def _api(host: str, port: int, path: str) -> str:
    return f"http://{host}:{port}{path}"


def list_models(host="localhost", port=8001) -> list[str]:
    """Return the names served by the vLLM daemon (base + LoRAs)."""
    r = requests.get(_api(host, port, "/v1/models"), timeout=30)
    r.raise_for_status()
    data = r.json()
    return [m["id"] for m in data.get("data", [])]


def unload_lora_adapter(
    lora_name: str, host="localhost", port=8001, silent: bool = False, timeout: int = 120
) -> None:
    """POST /v1/unload_lora_adapter (ignore 404)."""
    r = requests.post(
        _api(host, port, "/v1/unload_lora_adapter"),
        json={"lora_name": lora_name},
        timeout=timeout,
    )
    if r.ok:
        if not silent:
            logger.info(f"[vLLM] unloaded «{lora_name}»")
    else:
        # 404 means not loaded – fine
        if r.status_code != 404:
            raise RuntimeError(f"Could not unload {lora_name}: {r.text}")


def load_lora_adapter(
    lora_name: str, lora_path: str, host="localhost", port=8001, retries: int = 3, timeout: int = 300
) -> None:
    """Ensure *exactly one* copy of <lora_name> is served, then load it."""
    if lora_name in list_models(host, port):
        unload_lora_adapter(lora_name, host, port, silent=True)

    payload = {"lora_name": lora_name, "lora_path": str(lora_path)}
    for i in range(retries):
        r = requests.post(
            _api(host, port, "/v1/load_lora_adapter"), json=payload, timeout=timeout
        )
        if r.ok:
            logger.info(f"[vLLM] loaded «{lora_name}» from {lora_path}")
            return
        logger.info(f"[vLLM] load failed ({i+1}/{retries}): {r.text}")
        time.sleep(2)
        import pdb; pdb.set_trace()

    raise RuntimeError(f"Could not load LoRA {lora_name}")


def load_lora_adapter_safe(
    lora_name: str,
    lora_path: str,
    host: str = "localhost",
    port: int = 8001,
    retries: int = 3,
    verify_load: bool = True,
) -> bool:
    """
    Safely load a LoRA adapter with verification and return success status.

    Args:
        lora_name: Name for the adapter
        lora_path: Path to the adapter
        host: vLLM server host
        port: vLLM server port
        retries: Number of retry attempts
        verify_load: Whether to verify the adapter was loaded successfully

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if path exists and contains required files
        if not os.path.exists(lora_path):
            logger.error(f"Adapter path does not exist: {lora_path}")
            return False

        required_files = ["adapter_config.json"]
        has_model_file = any(
            os.path.exists(os.path.join(lora_path, f))
            for f in ["adapter_model.bin", "adapter_model.safetensors"]
        )

        if not has_model_file or not all(
            os.path.exists(os.path.join(lora_path, f)) for f in required_files
        ):
            logger.error(f"Adapter directory missing required files: {lora_path}")
            return False

        # Use the existing robust load function
        load_lora_adapter(lora_name, lora_path, host, port, retries)

        # Verify the adapter was loaded if requested
        if verify_load:
            models = list_models(host, port)
            if lora_name not in models:
                logger.error(
                    f"Adapter {lora_name} not found in model list after loading"
                )
                return False

        logger.info(f"Successfully loaded adapter {lora_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to load adapter {lora_name}: {e}")
        return False


def get_adapter_from_ppo_output(ppo_output_dir: str, component_name: str) -> Optional[str]:
    """
    Find the best adapter from PPO output directory.

    Args:
        ppo_output_dir: PPO output directory (should contain ppo/component_name subdirectory)
        component_name: Name of the component

    Returns:
        Path to the best adapter, or None if not found
    """
    # Handle both cases: ppo_output_dir is the component dir or contains ppo/component_name
    if os.path.basename(ppo_output_dir) == component_name:
        component_ppo_dir = ppo_output_dir
    else:
        component_ppo_dir = os.path.join(ppo_output_dir, "ppo", component_name)

    if not os.path.exists(component_ppo_dir):
        logger.warning(f"PPO output directory not found: {component_ppo_dir}")
        return None

    # Look for final directory first
    final_dir = os.path.join(component_ppo_dir, "final")
    if os.path.exists(final_dir) and os.path.isdir(final_dir):
        required_files = ["adapter_config.json"]
        has_model_file = any(
            os.path.exists(os.path.join(final_dir, f))
            for f in ["adapter_model.bin", "adapter_model.safetensors"]
        )

        if has_model_file and all(
            os.path.exists(os.path.join(final_dir, f)) for f in required_files
        ):
            logger.info(f"Found final adapter: {final_dir}")
            return final_dir

    # Look for step directories
    step_dirs = []
    try:
        for item in os.listdir(component_ppo_dir):
            if item.startswith("step_"):
                step_dir = os.path.join(component_ppo_dir, item)
                if os.path.isdir(step_dir):
                    try:
                        step_num = int(item.split("step_")[-1])
                        # Check if this step directory has the required files
                        required_files = ["adapter_config.json"]
                        has_model_file = any(
                            os.path.exists(os.path.join(step_dir, f))
                            for f in ["adapter_model.bin", "adapter_model.safetensors"]
                        )

                        if has_model_file and all(
                            os.path.exists(os.path.join(step_dir, f))
                            for f in required_files
                        ):
                            step_dirs.append((step_num, step_dir))
                    except ValueError:
                        continue
    except OSError as e:
        logger.error(f"Error reading directory {component_ppo_dir}: {e}")
        return None

    if step_dirs:
        # Sort by step number and return the latest
        step_dirs.sort(key=lambda x: x[0])
        latest_step_dir = step_dirs[-1][1]
        logger.info(f"Found latest step adapter: {latest_step_dir}")
        return latest_step_dir

    logger.warning(f"No valid adapter found in {component_ppo_dir}")
    return None
