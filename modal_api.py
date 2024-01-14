import os
import io
import modal
from modal import Image, Secret, Stub, method

MODEL_DIR = "./mistral"
# BASE_MODEL = "mistralai/Mistral-7B-v0.1"
# HF_TOKEN=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
BASE_MODEL = "mistralai/Mixtral-8x7B-v0.1"

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

image = (
    Image.from_registry(
        "nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10"
    )
    .pip_install("vllm==0.2.5", "huggingface_hub==0.19.4", "hf-transfer==0.1.4")
    # Use the barebones hf-transfer package for maximum download speeds. No progress bar, but expect 700MB/s.
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_folder,
        secret=Secret.from_name("huggingface"),
        timeout=60 * 20,
    )
)

stub = Stub("example-vllm-inference", image=image)

@stub.cls(gpu="A100", secret=Secret.from_name("huggingface"))
class Model:
    def __enter__(self):
        from vllm import LLM

        # Load the model. Tip: MPT models may require `trust_remote_code=true`.
        self.llm = LLM(MODEL_DIR)
        self.template = """<s>[INST] <<SYS>>
{system}
<</SYS>>

{user} [/INST] """

    @method()
    def generate(self, user_questions):
        from vllm import SamplingParams

        prompts = [
            self.template.format(system="", user=q) for q in user_questions
        ]

        sampling_params = SamplingParams(
            temperature=0.75,
            top_p=1,
            max_tokens=800,
            presence_penalty=1.15,
        )
        result = self.llm.generate(prompts, sampling_params)
        num_tokens = 0
        for output in result:
            num_tokens += len(output.outputs[0].token_ids)
            print(output.prompt, output.outputs[0].text, "\n\n", sep="")
        print(f"Generated {num_tokens} tokens")

@stub.local_entrypoint()
def main():
    model = Model()
    questions = [
        # Coding questions
        "Implement a Python function to compute the Fibonacci numbers.",
        "Write a Rust function that performs binary exponentiation.",
        "How do I allocate memory in C?",
    ]
    model.generate.remote(questions)

main()


#### IMAGE INFERENCE EXAMPLE

# stub = modal.Stub()


# @stub.function(
#     image=modal.Image.debian_slim().pip_install("torch", "diffusers[torch]", "transformers", "ftfy"),
#     secret=modal.Secret.from_name("cardi_secret"),
#     gpu="any",
# )
# async def run_stable_diffusion(prompt: str):
#     from diffusers import StableDiffusionPipeline

#     pipe = StableDiffusionPipeline.from_pretrained(
#         "runwayml/stable-diffusion-v1-5",
#         use_auth_token=os.environ["HF_TOKEN"],
#     ).to("cuda")

#     image = pipe(prompt, num_inference_steps=10).images[0]

#     buf = io.BytesIO()
#     image.save(buf, format="PNG")
#     img_bytes = buf.getvalue()

#     return img_bytes


# @stub.local_entrypoint()
# def main():
#     img_bytes = run_stable_diffusion.remote("Wu-Tang Clan climbing Mount Everest")
#     with open("/tmp/output.png", "wb") as f:
#         f.write(img_bytes)
