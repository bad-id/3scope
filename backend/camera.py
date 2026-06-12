import cv2
import numpy as np
from pypylon import pylon, _genicam
from pyflow import extensity
from device import Device
import logging

@extensity
class Camera(Device):
    def __init__(self):
        self.device_name = 'Camera'

        self.camera = None

    def connect(self):
        """
        This function attempts to connect to the camera
        """
        try:
            # Connect to camera
            self.camera = pylon.InstantCamera(
                pylon.TlFactory.GetInstance().CreateFirstDevice()
            )
            self.camera.Open()

            # Converter setup
            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            self.connected = True
        
        except (_genicam.RuntimeException) as e:
            self.connected = False
        return self.connected

    def start(self):
        """
        This function makes the camera start
        """
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def stop(self):
        """
        This function makes the camera stop
        """
        self.started = False
        self.camera.StopGrabbing()
        self.camera.Close()
        cv2.destroyAllWindows()

    def set_exposure(self, exposure_time_us):
        """
        This function sets the camera exposure using the functi0n argument
        """
        self.camera.ExposureTime.SetValue(exposure_time_us)
        
    def get_frame(self):
        """
        This function returns the image at that instant in an 1920 x 1080 array
        """
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

    def gaussian_blur(self, image, blur=(3,3)):
        """
        This function applies a variable Gaussian blur. The image-array, kernel size
        and standard deviation are function arguments.  
        """
        blurred_image = cv2.GaussianBlur(image, blur, 0)
        return blurred_image

    def check_sharpness(self, image):
        """
        This function checks the sharpness using the built in Laplacian function from the cv2 library
        """
        #The value gets higher when the picture gets sharper
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def tenengrad(self, image):
        """
        This function uses the Sobel operator to compute the local partial derivatives
        and adds returns the mean value.
        """
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

        g = np.sqrt(gx**2 + gy**2)

        return np.mean(g)

    def run(self):
        """
        This function initializes the camera and starts grabbing images until "q" is pressed.
        Then it stops the camera and returns the sharpness value of the latest frame.
        """
        self.start()

        while self.camera.IsGrabbing():
            frame = self.get_frame()

            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow("Basler Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                sharpness = self.check_sharpness(gray)
                logging.info(f"Sharpness: {sharpness:.2f}")
                break

        self.stop()