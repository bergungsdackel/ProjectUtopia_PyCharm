import math
import smbus
from Kalman import KalmanAngle
import time

class GYRO(object):

    def __init__(self):

        # Register
        self.power_mgmt_1 = 0x6b

        self.bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) for Revision 1

        self.address = 0x68  # via i2c detect, address research!
        self.bus.write_byte_data(self.address, 0x19, 7)

        # activate to communicate with the module
        # first argument is address, second is offset, third is data
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 1)
        self.bus.write_byte_data(self.address, 0x1A, 0)
        self.bus.write_byte_data(self.address, 0x1B, 24)
        self.bus.write_byte_data(self.address, 0x38, 1)

        self.gyroscopeX = 0
        self.gyroscopeY = 0
        self.gyroscopeZ = 0
        self.gyroscopeXScaled = 0
        self.gyroscopeYScaled = 0
        self.gyroscopeZScaled = 0
        self.accelerationX = 0
        self.accelerationY = 0
        self.accelerationZ = 0
        self.accelerationXScaled = 0
        self.accelerationYScaled = 0
        self.accelerationZScaled = 0
        self.xRotation = 0
        self.yRotation = 0
        self.yRotationRaw = 0

        # kalman
        self.kalmanX = KalmanAngle()
        self.kalmanY = KalmanAngle()
        self.kalAngleX = 0
        self.kalAngleY = 0
        self.timer = time.time()
        self.roll = 0
        self.pitch = 0
        self.kalmanX.setAngle(self.roll)
        self.kalmanY.setAngle(self.pitch)
        self.gyroXAngle = 0
        self.gyroYAngle = 0
        self.compAngleX = 0
        self.compAngleY = 0
        print("gyroscope initialized")

        self.yRotationk_1 = 0

    # Methods
    def read_byte(self, reg):

        return self.bus.read_byte_data(self.address, reg)

    def read_word(self, reg):

        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg + 1)
        value = (h << 8) + l
        return value

    def read_word_2c(self, reg):

        value = self.read_word(reg)
        if value >= 0x8000:
            return -((65535 - value) + 1)
        else:
            return value

    def dist(self, a, b):

        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):

        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):

        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def read_gyro(self):
        """
        writes the y-rotation in the yRotation variable
        """
        self.gyroscopeX = self.read_word_2c(0x43)
        self.gyroscopeY = self.read_word_2c(0x45)
        self.gyroscopeZ = self.read_word_2c(0x47)

        self.gyroscopeXScaled = self.gyroscopeX / 131
        self.gyroscopeYScaled = self.gyroscopeY / 131
        self.gyroscopeZScaled = self.gyroscopeZ / 131

        self.accelerationX = self.read_word_2c(0x3b)
        self.accelerationY = self.read_word_2c(0x3d)
        self.accelerationZ = self.read_word_2c(0x3f)

        self.accelerationXScaled = self.accelerationX / 16384.0
        self.accelerationYScaled = self.accelerationY / 16384.0
        self.accelerationZScaled = self.accelerationZ / 16384.0

        self.kalmanX.setAngle(self.roll)
        self.kalmanY.setAngle(self.pitch)
        self.xRotation = self.roll
        self.yRotation = self.pitch
        self.compAngleX = self.roll
        self.compAngleY = self.pitch

        dt = time.time() - self.timer
        self.timer = time.time()

        self.roll = math.atan(
            self.accelerationY / math.sqrt((self.accelerationX ** 2) + (self.accelerationZ ** 2))) * 57.2957786
        self.pitch = math.atan2(-self.accelerationX, self.accelerationZ) * 57.2957786

        gyroXRate = self.gyroscopeXScaled
        gyroYRate = self.gyroscopeYScaled

        if (self.pitch < -90 and self.kalAngleY > 90) or (self.pitch > 90 and self.kalAngleY < -90):
            self.kalmanY.setAngle(self.pitch)
            self.compAngleY = self.pitch
            self.kalAngleY = self.pitch
            self.gyroYAngle = self.pitch
        else:
            self.kalAngleY = self.kalmanY.getAngle(self.pitch, gyroYRate, dt)

        if abs(self.kalAngleY) > 90:
            gyroXRate = -gyroXRate
            self.kalAngleX = self.kalmanX.getAngle(self.roll, gyroXRate, dt)

        self.gyroXAngle = gyroXRate * dt
        self.gyroYAngle = self.gyroYAngle * dt

        self.compAngleX = 0.93 * (self.compAngleX + gyroXRate * dt) + 0.07 * self.roll
        self.compAngleY = 0.93 * (self.compAngleY + gyroYRate * dt) + 0.07 * self.pitch

        self.xRotation = self.kalAngleX

        self.yRotationk_1 = self.yRotationRaw
        self.yRotationRaw = self.kalAngleY
        self.yRotation = (self.yRotationk_1 + self.yRotationRaw) / 2
