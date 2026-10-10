"""Camera diagnostic: python -m camera_input.camera_test --source 0."""
import argparse
import time

import cv2

from camera_input.camera import CameraStream


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()

    camera = CameraStream(args.source, args.width, args.height)
    try:
        camera.open()
        frames = 0
        started = time.time()
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Camera read failed; exiting.")
                break
            frames += 1
            fps = frames / max(time.time() - started, 1e-6)
            cv2.putText(
                frame,
                f"Camera test | FPS {fps:.1f} | q to quit",
                (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2,
            )
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
