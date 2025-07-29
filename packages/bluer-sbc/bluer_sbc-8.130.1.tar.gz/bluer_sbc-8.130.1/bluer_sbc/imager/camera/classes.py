import cv2
from typing import Tuple
import numpy as np
from time import sleep

from blueness import module
from bluer_options import string
from bluer_options import host
from bluer_options.timer import Timer
from bluer_options.logger import crash_report
from bluer_objects import file, objects

from bluer_sbc import env
from bluer_sbc import NAME
from bluer_sbc.hardware import hardware
from bluer_sbc.imager.classes import Imager
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)


class Camera(Imager):
    def __init__(self):
        self.device = None
        self.resolution = []

    def capture(
        self,
        close_after: bool = True,
        log: bool = True,
        open_before: bool = True,
        filename: str = "",
        object_name: str = "",
    ) -> Tuple[bool, np.ndarray]:
        success = False
        image = np.ones((1, 1, 3), dtype=np.uint8) * 127

        if open_before:
            if not self.open():
                return success, image

        if self.device is None:
            return success, image

        if host.is_rpi():
            temp = file.auxiliary("camera", "png")
            try:
                self.device.capture(temp)
                success = True
            except Exception as e:
                crash_report(e)

            if success:
                success, image = file.load_image(temp)
        else:
            try:
                success, image = self.device.read()

                if success:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            except Exception as e:
                crash_report(e)

        if close_after:
            self.close()

        if success and log:
            logger.info(f"{NAME}.capture(): {string.pretty_shape_of_matrix(image)}")

        if success and filename:
            success = file.save_image(
                filename=objects.path_of(
                    object_name=object_name,
                    filename=filename,
                ),
                image=image,
                log=log,
            )

        return success, image

    # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/6
    def capture_video(
        self,
        filename: str,
        object_name: str,
        length: int = 10,  # in seconds
        preview: bool = True,
        pulse: bool = True,
        resolution=None,
    ) -> bool:
        if not host.is_rpi():
            logger.error(f"{NAME}.capture_video() only works on rpi.")
            return False

        if not self.open(resolution=resolution):
            return False

        full_filename = objects.path_of(
            object_name=object_name,
            filename=filename,
        )

        success = True
        try:
            if preview:
                self.device.start_preview()

            self.device.start_recording(full_filename)
            if pulse:
                for _ in range(int(10 * length)):
                    hardware.pulse("outputs")
                    sleep(0.1)
            else:
                sleep(length)
            self.device.stop_recording()

            if preview:
                self.device.stop_preview()
        except Exception as e:
            crash_report(e)
            success = False

        if not self.close():
            return False

        if success:
            logger.info(
                "{}.capture_video(): {} -{}-> {}".format(
                    NAME,
                    string.pretty_duration(length),
                    string.pretty_bytes(file.size(full_filename)),
                    filename,
                )
            )

        return success

    def close(self, log: bool = True) -> bool:
        if self.device is None:
            logger.warning(f"{NAME}.close(): device is {self.device}, failed.")
            return False

        success = False
        try:
            if host.is_rpi():
                self.device.close()
            else:
                self.device.release()
            success = True
        except Exception as e:
            crash_report(e)
            return False

        self.device = None

        if log:
            logger.info(f"{NAME}.close().")

        return success

    def get_resolution(self):
        try:
            if host.is_rpi():
                from picamera import PiCamera

                return [value for value in self.device.resolution]
            else:
                return [
                    int(self.device.get(const))
                    for const in [cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FRAME_WIDTH]
                ]
        except Exception as e:
            crash_report(e)
            return []

    def open(
        self,
        log: bool = True,
        resolution=None,
    ) -> bool:
        try:
            if host.is_rpi():
                from picamera import PiCamera

                self.device = PiCamera()
                self.device.rotation = env.BLUER_SBC_CAMERA_ROTATION

                # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7
                self.device.resolution = (
                    (
                        (2592, 1944)
                        if env.BLUER_SBC_CAMERA_HI_RES
                        else (
                            env.BLUER_SBC_CAMERA_WIDTH,
                            env.BLUER_SBC_CAMERA_HEIGHT,
                        )
                    )
                    if resolution is None
                    else resolution
                )
            else:
                self.device = cv2.VideoCapture(0)

                # https://stackoverflow.com/a/31464688
                self.device.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
                self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

            self.resolution = self.get_resolution()

            if log:
                logger.info(f"{NAME}.open({string.pretty_shape(self.resolution)})")

            return True
        except Exception as e:
            crash_report(e)
            return False

    def preview(
        self,
        length: float = -1,
    ) -> bool:
        logger.info(
            "{}.preview{} ... | press q or e to quit ...".format(
                NAME,
                "[{}]".format("" if length == -1 else string.pretty_duration(length)),
            )
        )

        hardware.sign_images = False
        timer = Timer(length, "preview")
        try:
            self.open(
                log=True,
                resolution=(320, 240),
            )

            while not hardware.pressed("qe"):
                _, image = self.capture(
                    close_after=False,
                    log=False,
                    open_before=False,
                )
                hardware.update_screen(image, None, [])

                if timer.tick(wait=True):
                    logger.info(
                        "{} is up, quitting.".format(string.pretty_duration(length))
                    )
                    break

        except KeyboardInterrupt:
            logger.info("Ctrl+C, stopping.")

        finally:
            self.close(log=True)

        return True
