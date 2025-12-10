#!/usr/bin/env python3
"""
Simple test script to POST to a RunPod endpoint and save the returned base64 image.

Usage examples:

# Using environment variables
setx RUNPOD_API_KEY "your_key_here"
python test.py --url https://api.runpod.ai/v2/k6e5etdyq3p81s/run --prompt "1girl, anime" --out out.png

# Or pass API key on the command line (careful: shows in history)
python test.py --url https://api.runpod.ai/v2/k6e5etdyq3p81s/run --api-key YOUR_API_KEY --prompt "1girl" --out result.png
"""

import os
import sys
import argparse
import base64
import json

try:
    import requests
except Exception:
    print("This script requires the 'requests' package. Run: pip install requests")
    sys.exit(2)


def main():
    p = argparse.ArgumentParser(description="Post a prompt to a RunPod endpoint and save returned image")
    p.add_argument('--url', required=False, default='https://api.runpod.ai/v2/k6e5etdyq3p81s/run', help='RunPod endpoint URL')
    p.add_argument('--api-key', required=False, help='RunPod API key (or set RUNPOD_API_KEY env var)')
    p.add_argument('--prompt', required=False, default='1girl', help='Prompt to send')
    p.add_argument('--prompt-file', required=False, help='Path to a file (.txt or .xml) containing the prompt')
    p.add_argument('--out', required=False, default='out.png', help='Output image filename')
    p.add_argument('--timeout', required=False, type=int, default=300, help='Request timeout seconds')

    args = p.parse_args()

    api_key = args.api_key or os.getenv('RUNPOD_API_KEY')
    if not api_key:
        print("Error: API key not provided. Use --api-key or set RUNPOD_API_KEY environment variable.")
        sys.exit(2)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Determine prompt: prompt-file takes precedence over --prompt
    prompt_text = args.prompt
    if getattr(args, 'prompt_file', None):
        pf = args.prompt_file
        if not os.path.exists(pf):
            print(f"Prompt file not found: {pf}")
            sys.exit(2)
        try:
            if pf.lower().endswith('.xml'):
                # Try to extract <prompt> tag; otherwise use all text content
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(pf)
                    root = tree.getroot()
                    node = root.find('.//prompt')
                    if node is not None and node.text and node.text.strip():
                        prompt_text = node.text.strip()
                    else:
                        # join all text
                        prompt_text = ''.join(root.itertext()).strip()
                except Exception:
                    # fallback to raw read
                    with open(pf, 'r', encoding='utf-8') as fh:
                        prompt_text = fh.read().strip()
            else:
                with open(pf, 'r', encoding='utf-8') as fh:
                    prompt_text = fh.read().strip()
        except Exception as e:
            print(f"Failed to read prompt file: {e}")
            sys.exit(2)

    payload = {
        'input': {
            'prompt': prompt_text
        }
    }

    print(f"Sending request to {args.url} with prompt: {prompt_text}")

    try:
        r = requests.post(args.url, headers=headers, json=payload, timeout=args.timeout)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(3)

    if r.status_code != 200:
        print(f"Non-200 response: {r.status_code}")
        try:
            print(r.text)
        except Exception:
            pass
        sys.exit(4)

    try:
        data = r.json()
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        print(r.text)
        sys.exit(5)

    # The handler returns {"image": "<base64>"}
    b64 = None
    if isinstance(data, dict) and 'image' in data:
        b64 = data['image']
    else:
        # Try common wrappers
        if isinstance(data, dict) and 'output' in data and isinstance(data['output'], dict) and 'image' in data['output']:
            b64 = data['output']['image']

    if not b64:
        print('No "image" key found in response JSON. Dumping JSON:')
        print(json.dumps(data, indent=2, ensure_ascii=False))
        sys.exit(6)

    try:
        img_bytes = base64.b64decode(b64)
    except Exception as e:
        print(f'Failed to decode base64 image: {e}')
        sys.exit(7)

    try:
        with open(args.out, 'wb') as f:
            f.write(img_bytes)
    except Exception as e:
        print(f'Failed to write output file: {e}')
        sys.exit(8)

    print(f'Saved image to {args.out}')


if __name__ == '__main__':
    main()
