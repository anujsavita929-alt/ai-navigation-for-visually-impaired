"""Print Python, PyTorch, CUDA, and OpenCV diagnostics."""
import sys


def main():
    print("Python:", sys.version)
    try:
        import torch
        print("PyTorch:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))
            print("CUDA runtime:", torch.version.cuda)
    except Exception as exc:
        print("PyTorch diagnostic unavailable:", exc)

    try:
        import cv2
        print("OpenCV:", cv2.__version__)
    except Exception as exc:
        print("OpenCV diagnostic unavailable:", exc)


if __name__ == "__main__":
    main()
