import os
MODEL_DIR = "./model/mistral7b"
BASE_MODEL = "someone13574/mixtral-8x7b-32kseqlen"

def download_model_to_folder():
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        BASE_MODEL,
        local_dir=MODEL_DIR,
        token=os.environ["HF_TOKEN"],
    )
    move_cache()

download_model_to_folder()