from model_registry_sdk import download_model, create_model, get_model, list_models

def test_all():
    download_model("model-123")
    create_model("my-awesome-model")
    get_model("model-123")
    list_models()

if __name__ == "__main__":
    test_all()
