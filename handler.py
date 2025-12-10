import runpod
import torch
from modelscope import NewbiePipeline
from io import BytesIO
import base64

print("Loading model...")

pipe = NewbiePipeline.from_pretrained(
    "NewBieAi-lab/NewBie-image-Exp0.1",
    torch_dtype=torch.bfloat16,
).to("cuda")

print("Model loaded.")

def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "1girl")

    image = pipe(
        prompt,
        height=1024,
        width=1024,
        num_inference_steps=28,
    ).images[0]

    buf = BytesIO()
    image.save(buf, format="PNG")

    return {
        "image": base64.b64encode(buf.getvalue()).decode()
    }

runpod.serverless.start({"handler": handler})
