#!/usr/bin/env python3
"""
PROJECT: CHRONO-ZERO — ZERO HUMAN PRESENCE AUTOMATED PRODUCER
Engineered for: PLOT TWIST STUDIOS (@PlotTwistStudios-j4t)
Connects to Dreamina subscription using Seedream (ultra-realism images) and Seedance 2.5 (video).
Runs completely hands-free: submits jobs, polls completion, and downloads 9:16 clips locally.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

# --- CONFIGURATION (Zero-Human Environment Variables or Defaults) ---
DREAMINA_EMAIL = os.getenv("DREAMINA_EMAIL", "ezzhisham585@gmail.com")
DREAMINA_PASSWORD = os.getenv("DREAMINA_PASSWORD", "lolmanjoker556")
USEAPI_TOKEN = os.getenv("USEAPI_TOKEN", "")  # Token from useapi.net
DREAMINA_REGION = os.getenv("DREAMINA_REGION", "US")  # US or CA

BASE_URL = "https://api.useapi.net/v1/dreamina"
OUTPUT_DIR = Path("./generated_reels")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Negative prompt matrix applied across all generations
NEGATIVE_PROMPT = (
    "blurry, low resolution, plastic skin, airbrushed textures, flat lighting, "
    "oversaturated cartoon style, morphing hands, extra fingers, deformed facial features, "
    "inconsistent eye color, washed-out blacks, low contrast, distorted perspective, "
    "3d render look, anime, illustration"
)

# Episode 1 Master Production Blueprint
EPISODE_1_PIPELINE = {
    "episode": 1,
    "title": "The Cold Body",
    "anchor": {
        "model": "seedream",
        "ratio": "9:16",
        "prompt": (
            "candid cinematic photorealistic portrait of James Mercer (#MERCER_CORE_V1), "
            "34-year-old rugged male detective, piercing ice-hazel eyes, sharp angular jawline "
            "with heavy 3-day stubble, distinct 1.2cm diagonal scar cutting right eyebrow, "
            "wearing charcoal-black wool tactical trench coat with raised collar over obsidian-black "
            "ribbed turtleneck, worn leather shoulder holster, ultra-realistic 8k, hyper-detailed skin pores, "
            "volumetric neon-amber and cyan rim lighting, anamorphic lens flare, Arri Alexa 65, 85mm lens"
        )
    },
    "shots": [
        {
            "shot_id": 1,
            "name": "The Vault Breach",
            "duration": 8,
            "image_prompt": (
                "Cinematic extreme macro eye close-up of James Mercer (#MERCER_CORE_V1), "
                "hyper-detailed dilated hazel iris reflecting a flickering cyan neon sign reading 'VAULT 73'. "
                "Half of face illuminated by high-contrast volumetric frost vapor and radioactive amber emergency strobe, "
                "ultra-realistic 8k, sub-surface skin scattering, Arri Alexa 65 anamorphic."
            ),
            "video_prompt": (
                "[Camera: Dynamic high-speed backward pull out from extreme close-up of hazel eye pupil, "
                "pulling back into medium over-the-shoulder tracking shot] James Mercer steps forward into "
                "abandoned cryogenic bunker chamber Vault 73. Heavy cold breath vapor billowing from his mouth, "
                "dynamic flashlight beam cutting through frosty vapor, glowing floor grates, heavy volumetric atmosphere, "
                "cinematic motion blur, 8k photorealistic."
            ),
            "dialogue": "They told me Vault 73 was sealed forty years ago. But the frost on the lock was fresh."
        },
        {
            "shot_id": 2,
            "name": "The Discovery",
            "duration": 8,
            "image_prompt": (
                "Top-down cinematic close-up through frosted tempered glass of cryogenic chamber. "
                "Tactical flashlight beam cutting through ice mist. Beneath the scratched frost-covered glass "
                "lies an unmoving male corpse with the exact facial structure, heavy stubble, and right eyebrow "
                "scar as James Mercer (#MERCER_CORE_V1), wearing identical charcoal wool trench coat. "
                "Saturated electric cyan and sodium-amber dual lighting, water droplets on glass, 8k photorealism."
            ),
            "video_prompt": (
                "[Camera: Continuous vertical downward tilt following intense tactical flashlight beam, "
                "settling into top-down glass perspective] Gloved tactical hand wipes frost across tempered glass "
                "of cryogenic preservation chamber. Flashlight illuminates the dead Mercer corpse beneath the ice. "
                "Dramatic camera drift, rising frost mist, photorealistic reflections on glass."
            ),
            "dialogue": "Wiped the glass expecting a stranger. What I saw made my blood stop."
        },
        {
            "shot_id": 3,
            "name": "The Cassette Tape",
            "duration": 8,
            "image_prompt": (
                "Cinematic macro shot inside open cryogenic chamber, pale frozen male hand with frost crystals "
                "on knuckles, tightly clutching a retro black micro-cassette tape recorder. The red recording LED "
                "light is glowing bright crimson with an intense anamorphic lens flare. High-contrast electric cyan "
                "shadows, floating ice particles, photorealistic 8k, Panavision anamorphic lens."
            ),
            "video_prompt": (
                "[Camera: Smooth rotational corkscrew push-in diving into cryogenic chamber toward the hand] "
                "Close-up of frozen pale hand clutching micro-cassette recorder. The red recording light on "
                "the cassette tape pulses rhythmically in bright crimson. Atmospheric frost vapor swirls around "
                "fingers, hyper-detailed textures, shallow depth of field."
            ),
            "dialogue": "He wasn't just dead. He was clutching an analog cassette... and the record light was blinking."
        },
        {
            "shot_id": 4,
            "name": "The Cliffhanger & Loop Exit",
            "duration": 6,
            "image_prompt": (
                "Extreme close-up macro portrait of frozen dead James Mercer (#MERCER_CORE_V1) inside cryo-pod. "
                "Head tilted back, eyes wide open, dilated hazel iris centered perfectly in frame, reflecting "
                "flickering neon amber warning beacons. Ice crystals on eyelashes and pale lips, hyper-detailed skin pores, cinematic 8k."
            ),
            "video_prompt": (
                "[Camera: Ultra-fast crash zoom into cassette recorder speaker then rapid whip-pan up into "
                "macro close-up of dead Mercer's dilated hazel eye] Camera accelerates rapidly into dead Mercer's "
                "open eye pupil, aligning directly into the center of the dark pupil right at the final second. "
                "Strobe amber warning lights casting dramatic pulses, cinematic 60fps motion blur."
            ),
            "dialogue": "And the scariest part about finding your own dead body... is realizing that the person who put you in this vault..."
        }
    ]
}


def make_request(url: str, method: str = "GET", payload: dict = None, headers: dict = None) -> dict:
    """Helper to perform HTTP requests using standard urllib without external dependencies."""
    if headers is None:
        headers = {}
    
    headers.setdefault("Content-Type", "application/json")
    if USEAPI_TOKEN:
        headers["Authorization"] = f"Bearer {USEAPI_TOKEN}"

    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[ERROR] HTTP {e.code} on {url}: {err_msg}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"[ERROR] Request failed on {url}: {e}", file=sys.stderr)
        raise


def link_dreamina_account():
    """Initializes and connects your Dreamina subscription account."""
    print("=======================================================")
    print("1. CONNECTING DREAMINA SUBSCRIPTION ACCOUNT")
    print(f"   Account Email: {DREAMINA_EMAIL}")
    print(f"   Region: {DREAMINA_REGION}")
    print("=======================================================")

    if not USEAPI_TOKEN:
        print("[WARNING] USEAPI_TOKEN environment variable is not set!")
        print("To run zero-human automation via REST, obtain a token from useapi.net and set:")
        print("  export USEAPI_TOKEN='user:your-token-here'")
        return False

    payload = {
        "email": DREAMINA_EMAIL,
        "password": DREAMINA_PASSWORD,
        "region": DREAMINA_REGION,
        "maxJobs": 10
    }
    
    try:
        res = make_request(f"{BASE_URL}/accounts", method="POST", payload=payload)
        print(f"[SUCCESS] Dreamina account connected. Account ID: {res.get('email', DREAMINA_EMAIL)}")
        return True
    except Exception as e:
        print(f"[NOTICE] Direct account setup response: {e}")
        return True  # Proceed to test generation in case account is already configured


def generate_seedream_image(prompt: str, reference_url: str = None) -> str:
    """Submits a text-to-image job using Seedream with ultra-realism parameters."""
    print(f"\n[IMAGE GEN] Submitting Seedream Image: {prompt[:60]}...")
    payload = {
        "prompt": f"{prompt} --negative {NEGATIVE_PROMPT}",
        "model": "seedream",
        "ratio": "9:16",
        "mode": "standard"  # Unlimited mode - zero fast credits used
    }
    if reference_url:
        payload["image_ref"] = reference_url

    res = make_request(f"{BASE_URL}/images", method="POST", payload=payload)
    job_id = res.get("jobid") or res.get("task_id")
    print(f"[IMAGE GEN] Job queued: {job_id}. Polling for completion...")

    # Poll status
    while True:
        status_data = make_request(f"{BASE_URL}/images/{job_id}")
        state = status_data.get("status")
        if state == "completed":
            img_url = status_data.get("url") or status_data.get("output_url")
            print(f"[IMAGE GEN] Completed: {img_url}")
            return img_url
        elif state == "failed":
            raise RuntimeError(f"Seedream generation failed: {status_data.get('error')}")
        print(".", end="", flush=True)
        time.sleep(5)


def generate_seedance_video(prompt: str, start_image_url: str, duration: int = 8) -> str:
    """Submits an image-to-video job using Seedance 2.5 with zero-credit settings."""
    print(f"\n[VIDEO GEN] Submitting Seedance 2.5 Video: {prompt[:60]}... ({duration}s)")
    payload = {
        "prompt": prompt,
        "model": "seedance-2.5",
        "ratio": "9:16",
        "duration": duration,
        "image_url": start_image_url,
        "mode": "standard"  # Unlimited mode - zero fast credits used
    }

    res = make_request(f"{BASE_URL}/videos", method="POST", payload=payload)
    job_id = res.get("jobid") or res.get("task_id")
    print(f"[VIDEO GEN] Job queued: {job_id}. Rendering with Seedance 2.5...")

    # Poll status
    while True:
        status_data = make_request(f"{BASE_URL}/videos/{job_id}")
        state = status_data.get("status")
        if state == "completed":
            video_url = status_data.get("url") or status_data.get("output_url")
            print(f"\n[VIDEO GEN] Rendered successfully: {video_url}")
            return video_url
        elif state == "failed":
            raise RuntimeError(f"Seedance generation failed: {status_data.get('error')}")
        print(".", end="", flush=True)
        time.sleep(8)


def download_file(url: str, destination_path: Path):
    """Downloads remote asset to local storage."""
    print(f"[DOWNLOAD] Saving to {destination_path}...")
    urllib.request.urlretrieve(url, str(destination_path))
    print(f"[SAVED] {destination_path} ({destination_path.stat().st_size} bytes)")


def execute_autonomous_pipeline(episode_data: dict):
    """Executes the entire episode generation hands-free with zero human presence."""
    ep_num = episode_data["episode"]
    print("\n=======================================================")
    print(f"🎬 EXECUTING ZERO-HUMAN PIPELINE: EPISODE {ep_num} ('{episode_data['title']}')")
    print("=======================================================")

    # Step 1: Character Anchor Generation (Node 0)
    anchor_file = OUTPUT_DIR / f"ep{ep_num}_anchor_mercer.png"
    if not anchor_file.exists():
        anchor_url = generate_seedream_image(episode_data["anchor"]["prompt"])
        download_file(anchor_url, anchor_file)
    else:
        print(f"[CACHE] Found existing anchor: {anchor_file}")
        anchor_url = str(anchor_file)

    # Step 2: Iterate through every shot sequentially
    last_frame_url = anchor_url
    for shot in episode_data["shots"]:
        shot_id = shot["shot_id"]
        shot_video_file = OUTPUT_DIR / f"ep{ep_num}_shot_{shot_id}.mp4"
        shot_img_file = OUTPUT_DIR / f"ep{ep_num}_shot_{shot_id}_keyframe.png"

        print(f"\n-------------------------------------------------------")
        print(f"▶ PROCESSING SHOT {shot_id}/{len(episode_data['shots'])}: {shot['name']}")
        print(f"-------------------------------------------------------")

        # Generate Keyframe image with Seedream
        keyframe_url = generate_seedream_image(shot["image_prompt"], reference_url=last_frame_url)
        download_file(keyframe_url, shot_img_file)

        # Generate Seedance 2.5 Video clip
        video_url = generate_seedance_video(
            prompt=shot["video_prompt"],
            start_image_url=keyframe_url,
            duration=shot["duration"]
        )
        download_file(video_url, shot_video_file)

        # Pass forward keyframe for next shot continuity
        last_frame_url = keyframe_url

    print("\n=======================================================")
    print(f"✅ EPISODE {ep_num} AUTONOMOUS PRODUCTION COMPLETE!")
    print(f"All clips stored in: {OUTPUT_DIR.resolve()}")
    print("Ready for upload or ffmpeg auto-assembly into an infinite loop!")
    print("=======================================================")


if __name__ == "__main__":
    link_dreamina_account()
    execute_autonomous_pipeline(EPISODE_1_PIPELINE)
