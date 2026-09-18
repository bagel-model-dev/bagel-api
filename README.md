# BAGEL API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro)

BAGEL is ByteDance Seed's open unified multimodal model: one network that understands images, generates them from text and edits them with natural-language instructions. This package is a Python client that gives you a BAGEL API for those three jobs, image editing, image generation and visual question answering, with `pip install bagel-api` and no GPU of your own.

You get a blocking `run()` that returns the finished image or answer, a submit-and-poll path for queued jobs, webhook delivery for servers that must not block, and a single runtime dependency (`requests`). It is meant for backend services, content pipelines and notebooks that need a multimodal model as a function call rather than a 14B checkpoint.

> **Try it now:** [https://synexa.ai/explore/black-forest-labs/flux-kontext-pro](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About BAGEL](#about-bagel)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **14B parameters do not fit a consumer GPU.** BAGEL has 7B active parameters in a 14B mixture-of-transformer-experts; the bf16 weights alone are roughly 28 GB, and the reference inference targets an 80 GB card, with offloading and quantisation as the fallback. The hosted endpoints run on hardware sized for the job.
- **Three tasks, three tuned endpoints.** Instead of one general model, the client routes editing to `black-forest-labs/flux-kontext-pro`, generation to `openai/gpt-image-2` and understanding to `yorickvp/llava-13b`, each specialised for its task.
- **No cold start.** Loading a 14B model plus its ViT and VAE encoders takes minutes before the first token; hosted runs start on a warm model.
- **Per-run pricing.** Editing is $0.02 per run, generation $0.10 and image understanding $0.0005. There is no instance to keep alive between requests.

## Installation

```bash
pip install git+https://github.com/bagel-model-dev/bagel-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import bagel_api

output = bagel_api.run({
    "prompt": "Make this a 90s cartoon",
    "input_image": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from bagel_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "Make this a 90s cartoon", "input_image": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`black-forest-labs/flux-kontext-pro`](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro) | text-to-image | A state-of-the-art text-based image editing model that delivers high-quality outputs with excellent prompt following and consistent results for transforming images through natural language | $0.02 |
| [`openai/gpt-image-2`](https://synexa.ai/explore/openai/gpt-image-2) | text-to-image | OpenAI's state-of-the-art image generation model. Create and edit images from text with strong instruction following, sharp text rendering, and detailed editing. | $0.1 |
| [`yorickvp/llava-13b`](https://synexa.ai/explore/yorickvp/llava-13b) | text-recognition-ocr | Visual instruction tuning towards large language and vision models with GPT-4 level capabilities | $0.0005 |

The default model is **`black-forest-labs/flux-kontext-pro`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `black-forest-labs/flux-kontext-pro`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `seed` | integer | no | `random` | — | Random seed. Set for reproducible generation |
| `prompt` | string | yes | `Make this a 90s cartoon` | — | Text description of what you want to generate, or the instruction on how to edit the given image. |
| `input_image` | file | yes | `https://files.synexa.ai/models/black-for…` | — | Input image to start generating from |
| `aspect_ratio` | string | no | `match_input_image` | match_input_image, 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 4… | Aspect ratio of the generated image. Use 'match_input_image' to match the aspect ratio of the input image. |
| `output_format` | string | no | `jpg` | jpg, png | Output format for the generated image |

### `openai/gpt-image-2`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A photo of a wooden desk in golden hour …` | — | A text description of the desired image, or instructions for editing the input images |
| `aspect_ratio` | string | no | `1:1` | 1:1, 3:2, 2:3, 16:9, 9:16 | Aspect ratio of the generated image |
| `input_images` | files | no | — | — | Optional reference images for editing or multi-image composition (up to 20) |

### `yorickvp/llava-13b`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image` | file | yes | `https://synexa.s3.us-east-005.backblazeb…` | — | Input image |
| `top_p` | number | no | `1` | 0, 1 | When decoding text, samples from the top p percentage of most likely tokens; lower to ignore less likely tokens |
| `prompt` | string | yes | `Are you allowed to swim here?` | — | Prompt to use for text generation |
| `max_tokens` | integer | no | `1024` | 0, 1024 | Maximum number of tokens to generate. A word is generally 2-3 tokens |
| `temperature` | number | no | `0.2` | 0, 1 | Adjusts randomness of outputs, greater than 1 is random and 0 is deterministic |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from bagel_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About BAGEL

BAGEL was released by ByteDance Seed in May 2025 with the paper *Emerging Properties in Unified Multimodal Pretraining* and Apache 2.0 weights. It is a single decoder-only model with 7B active parameters (14B total) built on a Mixture-of-Transformer-Experts design: one expert handles understanding tokens and one handles generation tokens, sharing self-attention so both modalities see the same context. Two visual encoders feed it, a ViT for semantic understanding and a VAE for pixel-level generation, and it was pretrained on trillions of interleaved text, image, video and web tokens.

The result is one model that answers questions about an image, generates images from text, edits an existing image from an instruction, and handles free-form manipulation such as changing style, adding or removing objects, or predicting the next frame of a scene. A *thinking* mode lets it reason in text before rendering, which the authors show improves complex edits and compositional prompts. On public benchmarks it was competitive with dedicated understanding models of similar size and with open image-generation models of the time.

Outputs are 1024 by 1024 by default and the usual caveats apply: small text rendering is unreliable, precise spatial edits can bleed into neighbouring regions, and the understanding side is a 7B-class vision-language model rather than a frontier one. It is a research release; inference is slow without a large GPU and the repository provides a Gradio demo rather than a serving stack.

The hosted endpoints used by this client are different models that together provide the same capabilities: `black-forest-labs/flux-kontext-pro` for instruction-based image editing, `openai/gpt-image-2` for text-to-image and multi-image composition, and `yorickvp/llava-13b` for image understanding and visual question answering; the original BAGEL weights are available at https://github.com/ByteDance-Seed/Bagel if you want to self-host the unified model.

**Official project:** https://github.com/ByteDance-Seed/Bagel

## Use cases

- **Instruction-based photo editing** — call `run()` with an `input_image` and a `prompt` such as "replace the sky with dusk" to get the edited image from `black-forest-labs/flux-kontext-pro`.
- **Product shots from text** — use the `openai/gpt-image-2` endpoint with a `prompt` and `aspect_ratio` to generate marketing imagery with legible packaging text.
- **Multi-image composition** — pass up to 20 reference photos as `input_images` to combine a product, a background and a style reference in one output.
- **Image captioning and tagging** — send an `image` and a `prompt` like "list the objects in this photo" to `yorickvp/llava-13b` for $0.0005 per call.
- **Visual QA in support tools** — let agents ask "what error is shown on this screenshot?" and get a text answer without a vision model in your stack.
- **Batch catalogue cleanup** — submit one edit per SKU without blocking and collect results via a webhook, with `seed` set for reproducible re-runs.

## FAQ

**Is there a BAGEL API?**

ByteDance publishes BAGEL as open weights with a Gradio demo, not as a hosted API. This package wraps Synexa endpoints that provide the same understanding, generation and editing capabilities over HTTPS, so you do not need to run the 14B model.

**How much does the BAGEL API cost?**

Image editing through `black-forest-labs/flux-kontext-pro` is $0.02 per run, image generation through `openai/gpt-image-2` is $0.10 per run, and image understanding through `yorickvp/llava-13b` is $0.0005 per run. Billing is per completed run.

**Can I run BAGEL without a GPU?**

Not in practice; the model needs a large GPU, and CPU inference is impractically slow. With this client the compute happens on the hosted side, so any machine that can make an HTTPS request is enough.

**Does this client work with the original ByteDance-Seed/Bagel repo or ComfyUI?**

No. It does not load local BAGEL checkpoints, use its thinking mode, or talk to the ComfyUI BAGEL nodes. It is an HTTP client for the hosted endpoints only.

**What input formats does it accept?**

For editing, `prompt` and `input_image` are required, with optional `aspect_ratio` (including `match_input_image`), `seed` and `output_format`. For generation, `prompt` is required and `input_images` (up to 20) and `aspect_ratio` are optional. For understanding, `image` and `prompt` are required, with optional `max_tokens`, `temperature` and `top_p`.

**Is this the official BAGEL SDK?**

No. This is an independent client and is not affiliated with ByteDance or the Seed team. The official project is at https://github.com/ByteDance-Seed/Bagel.

## Related

- [BAGEL (official repository)](https://github.com/ByteDance-Seed/Bagel)
- [Synexa Python client](https://github.com/synexa-ai/synexa-python)
- [black-forest-labs/flux-kontext-pro on Synexa](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro)
- [openai/gpt-image-2 on Synexa](https://synexa.ai/explore/openai/gpt-image-2)
- [yorickvp/llava-13b on Synexa](https://synexa.ai/explore/yorickvp/llava-13b)

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of BAGEL. Model weights and trademarks belong to their respective owners.
