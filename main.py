"""Launch the prototype: python main.py --config config/settings.yaml."""
import argparse

from app.pipeline import run_app
from config import load_config


def main():
    parser = argparse.ArgumentParser(description="Depth-aware AI navigation assistant prototype")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--source", help="Override camera source: 0, webcam index, or IP stream URL")
    parser.add_argument("--no-depth", action="store_true", help="Disable monocular depth estimation")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice input and speech output")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.source is not None:
        config["camera"]["source"] = args.source
    if args.no_depth:
        config["perception"]["enable_depth"] = False
    if args.no_voice:
        config["voice"]["enabled"] = False
    run_app(config)


if __name__ == "__main__":
    main()
