import runpod
import torch
from diffusers import NewbiePipeline
from io import BytesIO
import base64

print("Loading model...")

pipe = NewbiePipeline.from_pretrained(
    "NewBie-AI/NewBie-image-Exp0.1",
    torch_dtype=torch.bfloat16,
).to("cuda")

print("Model loaded.")

def handler(event):
    print("Worker Start")
    input = event['input']
    
    prompt = input.get('prompt', '1girl')
    
    print(f"Received prompt: {prompt}")
    print("Generating image...")

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

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
