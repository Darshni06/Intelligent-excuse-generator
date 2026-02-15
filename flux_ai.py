# flux_ai.py
import os
import requests
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class FluxImageGenerator:
    def __init__(self):
        # Try Streamlit secrets first (cloud), then .env (local)
        try:
            import streamlit as st
            self.api_key = st.secrets.get("STABILITY_API_KEY", "")
        except Exception:
            self.api_key = os.getenv("STABILITY_API_KEY", "")

        if not self.api_key:
            raise ValueError(
                "STABILITY_API_KEY not found. "
                "Add it to Streamlit secrets or your .env file."
            )

        self.api_url = (
            "https://api.stability.ai/v1/generation/"
            "stable-diffusion-xl-1024-v1-0/text-to-image"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    def generate_image(self, prompt, width=1024, height=1024, cfg_scale=7, steps=30):
        """Generate image via Stability AI and return a PIL Image."""
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": steps,
            "style_preset": "photographic",
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=90,
            )

            if response.status_code == 200:
                data = response.json()
                artifacts = data.get("artifacts", [])
                if artifacts:
                    img_bytes = BytesIO(base64.b64decode(artifacts[0]["base64"]))
                    return Image.open(img_bytes)
                raise RuntimeError("No image artifacts returned from API.")
            else:
                raise RuntimeError(
                    f"API error {response.status_code}: {response.text[:300]}"
                )

        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out. Please try again.")
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Network error: {exc}")
        except Exception as exc:
            raise RuntimeError(f"Unexpected error: {exc}")
