from .registry import download_model, create_model, get_model, list_models
from .update_checker import check_latest_version

check_latest_version("aipmodel")
version = "0.2.8"
__description__ = "SDK for model registration, versioning, and storage"
