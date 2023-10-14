import sys
import os
import time
from huggingface_hub import HfApi, ModelFilter
hf_api = HfApi()
models = hf_api.list_models(
    filter=ModelFilter(
        task="text-classification",
        library="pytorch",
        language="en",
    ),
    # limit=999,
)

KEYWORDS = [
    "abusive",
    "abuse",
    "hate",
    "hateful",
    "nsfw",
    "offensive",
    "toxic",
    "toxicity",
    "vulgar",
    "vulgarity",
    "profanity",
    "slur",
    "slurs",
    "anti-semitic",
    "anti-social",
    "antisocial",
    "impolite",
    "blind",
    "threat",
]

total, hit, miss = 0, 0, 0
print("author,model,downloads,likes,lastModified,security")
for model in models:
    total += 1
    if hasattr(model, "library_name") and model.library_name == 'transformers' and any([keyword in model.modelId.lower() for keyword in KEYWORDS]):
        print(f"{model.author},{os.path.basename(model.modelId)},{model.downloads},{model.likes},{model.lastModified},{model.securityStatus}")
        hit += 1
    else:
        miss += 1
        continue
        # print(f"NOMATCH model: {model.modelId}, security: {model.securityStatus}")

time.sleep(1)
print(f"Total: {total}, hit: {hit}, miss: {miss}", file=sys.stderr)

# python utilities/huggingface-model-finder.py | tee ./utilities/models.csv; visidata ./utilities/models.csv
