import cv2
import numpy as np
from pypylon import pylon


class Camera:
    def __init__(self):
        # Connect to camera
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )
        self.camera.Open()

        # Converter setup
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    def start(self):
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def stop(self):
        self.camera.StopGrabbing()
        self.camera.Close()
        cv2.destroyAllWindows()

    def get_frame(self):
        grabResult = self.camera.RetrieveResult(
            5000, pylon.TimeoutHandling_ThrowException
        )

        if grabResult.GrabSucceeded():
            image = self.converter.Convert(grabResult)
            frame = image.GetArray()
            grabResult.Release()
            return frame

        grabResult.Release()
        return None

    def check_sharpness(self, image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def run(self):
        self.start()

        while self.camera.IsGrabbing():
            frame = self.get_frame()

            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow("Basler Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                sharpness = self.check_sharpness(gray)
                print(f"Sharpness: {sharpness:.2f}")
                break

        self.stop()


if __name__ == "__main__":
    cam = Camera()
    cam.run()