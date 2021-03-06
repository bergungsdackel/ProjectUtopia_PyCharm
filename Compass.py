import math
import smbus



class COMPASS(object):
    def __init__(self):
        # Get I2C bus
        self.bus = smbus.SMBus(1)
        self.address = 0x1E
        # HMC5883 address, 0x1E
        self.bus.write_byte_data(self.address, 0x00, 0x60)
        self.bus.write_byte_data(self.address, 0x02, 0x00)
        # self.hmc5883l = i2c_QMC5883L.QMC5883L(output_range=i2c_QMC5883L.RNG_8G)  # if not the first I2C Device, the 1 has to be changed

    def compass(self):
        """
        :return: current orientation related to north in degree
        """
        # HMC5883 address, 0x1E and Read data
        data = self.bus.read_i2c_block_data(self.address, 0x03, 6)

        # Convert the data
        xMag = data[0] * 256 + data[1]
        if xMag > 32767:
            xMag -= 65536
        xMag = xMag * 0.75

        zMag = data[2] * 256 + data[3]
        if zMag > 32767:
            zMag -= 65536

        yMag = data[4] * 256 + data[5]
        if yMag > 32767:
            yMag -= 65536
        yMag = yMag + 80

        [x, y] = [xMag, yMag]
        if x is None or y is None:
            return None
        else:
            orientation = math.degrees(math.atan2(y, x)) + 42
            if orientation < 0:
                orientation += 360.0
            orientation += 2.45 # magnetic Correction
            if orientation < 0.0:
                orientation += 360.0
            elif orientation >= 360.0:
                orientation -= 360.0
        return orientation
