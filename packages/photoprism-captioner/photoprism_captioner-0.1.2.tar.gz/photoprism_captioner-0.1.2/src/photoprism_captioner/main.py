#!/usr/bin/env python3
"""photoprism_captioner.py – Caption your PhotoPrism library via a *unified* model interface.
Examples:
    # Local BLIP‑large, overwrite missing captions only
    photoprism_captioner.py --auth-token $SID --backend local \
        --model Salesforce/blip-image-captioning-large

    # Remote GPT‑4o Vision via litellm (needs OPENAI_API_KEY)
    photoprism_captioner.py --auth-token $SID --backend remote \
        --model gpt-4o-vision-preview --overwrite
"""

# TODO:
#   - if a video - make screenshot
#   - allow downsize photos
#   - allow custom prompt
#   - decouple Captioner into separate module
#   - Write comprehensive README.md (dockerized, croned, ollama, openai, local)
#   - Add tests
#   - Add logging
#   - Add docker and env examples
#   - Add pip package
#   - Add GitHub Actions
#   - memory management

from __future__ import annotations

import argparse
import base64
import os
import sys
from typing import Optional

from photoprism_captioner.photoprism_client import PhotoPrismClient
from photoprism_captioner.utils import resize_photo_to_max_width

MAX_PHOTO_WIDTH = 1024

###############################################################################
# Unified  ↔  Captioner layer
###############################################################################

class Captioner:
    """Abstract base class."""

    def caption(self, image_path: str) -> str:  # noqa: D401 – short method name OK
        raise NotImplementedError


###############################################################################
# Local models – Hugging Face pipeline("image-to-text")
###############################################################################

class HFImageCaptioner(Captioner):
    """Image captioner using *any* HF model that supports the image‑to‑text pipeline."""

    def __init__(self, model_name: str):
        import torch
        from transformers import pipeline  # lazy import – heavy

        device = 0 if torch.cuda.is_available() else -1
        self.pipe = pipeline("image-to-text", model=model_name, device=device)

    def caption(self, image_path: str) -> str:  # noqa: D401
        out = self.pipe(image_path, max_new_tokens=32)[0]["generated_text"]
        return out.strip()


###############################################################################
# Remote providers – litellm gives us a single chat‑completion call
###############################################################################

class LLMCaptioner(Captioner):
    """Remote vision model via litellm (OpenAI, Claude, Ollama, etc.)."""

    PROMPT = "Describe what you see in this image, in one sentence."

    def __init__(self, model_name: str, api_base: str):
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm not installed – run: pip install litellm"
            ) from exc
        self.litellm = litellm
        self.model = model_name
        self.api_base = api_base

    def caption(self, image_path: str) -> str:  # noqa: D401
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        # litellm mimics the OpenAI chat/completions payload—even for other providers
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                    {"type": "text", "text": self.PROMPT},
                ],
            }
        ]
        resp = self.litellm.completion(model=self.model, messages=messages, api_base=self.api_base)
        return resp.choices[0].message.content.strip()


###############################################################################
# PhotoPrism helpers
###############################################################################

def process_photos(
    captioner: Captioner,
    photoprism_url: str,
    auth_token: str,
    order: str,
    count: int,
    start_offset: int,
    overwrite: bool,
) -> None:
    """Process photos using the provided captioner.

    Args:
        captioner: The captioner to use for generating captions
        photoprism_url: Base URL of the PhotoPrism instance
        auth_token: Authentication token for the PhotoPrism API
        order: Sort order for photos (e.g., 'newest', 'oldest')
        count: Number of photos to process per batch
        start_offset: Offset to start processing from
        overwrite: Whether to overwrite existing descriptions
        allowed_exts: File extensions of images to process
    """
    import tempfile

    client = PhotoPrismClient(photoprism_url, auth_token)

    for photo in client.get_photos(order=order, count=count, start_offset=start_offset):
        photo_id = photo["UID"]
        description_existing = photo.get("Description")

        if description_existing and not overwrite:
            print(f"[SKIP] {photo_id} – already has description")
            continue
        try:
            # Download the photo
            image_data = client.download_photo(photo)
            if not image_data:
                print(f"[ERROR] Failed to download {photo_id}")
                continue
            image_data = resize_photo_to_max_width(image_data, MAX_PHOTO_WIDTH)

            # Save to a temporary file for processing
            with tempfile.NamedTemporaryFile(
                delete=True,
                suffix=photo_id
            ) as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()

                # Generate caption using the temporary file
                try:
                    caption = captioner.caption(tmp_file.name)
                    client.update_photo_description(photo_id, caption)
                    print(f"[OK] {photo_id} – {caption}")
                except Exception as e:
                    print(f"[ERROR] Failed to caption {photo_id}: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Failed to process {photo_id}: {e}")


###############################################################################
# CLI helpers
###############################################################################

def build_captioner(backend: str, model_name: str, api_base: Optional[str] = None) -> Captioner:
    if backend == "local":
        return HFImageCaptioner(model_name)
    if backend == "remote":
        return LLMCaptioner(model_name, api_base)
    raise ValueError(f"Unknown backend: {backend}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--auth-token",
        required=True,
        help="PhotoPrism session token (X-Auth-Token)",
        default=os.environ.get("PHOTOPRISM_AUTH_TOKEN"),
    )
    parser.add_argument(
        "--photoprism-url",
        default=os.environ.get("PHOTOPRISM_URL", "http://localhost:2342"),
        help="PhotoPrism URL (default: http://localhost:2342)",
    )
    parser.add_argument(
        "--backend",
        choices=("local", "remote"),
        required=True,
        help="Backend to use for captioning",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model name (e.g., 'Salesforce/blip-image-captioning-large' or 'gpt-4-vision-preview')",
    )
    parser.add_argument(
        "--order",
        default="newest",
        help="Sort order (default: newest)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of photos to process (default: 100)",
    )
    parser.add_argument(
        "--start-offset",
        type=int,
        default=0,
        help="Offset to start processing from (default: 0)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing descriptions",
    )
    parser.add_argument(
        "--api-base",
        help="LLM API base URL",
    )

    args = parser.parse_args(argv)

    if not args.auth_token:
        parser.error("No authentication token provided. Use --auth-token or set PHOTOPRISM_AUTH_TOKEN environment variable.")

    return args


def main(argv: Optional[list[str]] = None) -> None:
    """Run the script."""
    args = parse_args(argv)
    captioner = build_captioner(args.backend, args.model, args.api_base)

    try:
        process_photos(
            captioner=captioner,
            photoprism_url=args.photoprism_url,
            auth_token=args.auth_token,
            order=args.order,
            count=args.count,
            start_offset=args.start_offset,
            overwrite=args.overwrite,
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Aborted by user.")
        sys.exit(130)
