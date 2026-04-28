from pypylon import pylon
import cv2

# Connect to camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# Start grabbing
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        frame = image.GetArray()

        cv2.imshow("Basler Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(frame)
            break

    grabResult.Release()

camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()