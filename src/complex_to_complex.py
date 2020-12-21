import numpy as np


class PlotterComplex:
    """
    Class for complex plotting
    """
    def __init__(self, resolution: int = 256, distance: float = 7.0, format_of_image: tuple = (3, 2.1), squish: bool = False):
        """
        creates an Plotter.
        
        :param resolution: resolution of the complex plot (Pixels on the x-Axis)
        :param distance: distance of the point (0, 0). The x-Axis of the plot is the interval [-distance, distance]
        :param format_of_image: the ratio of x-Axis to y-Axis
        :param squish: different rescaling algorithm
        """
        self.format = format_of_image
        self.squish = squish
        self.resolution = resolution
        self.distance = distance
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
        """
        translates (hue, saturation, value) colors to (red, green, blue) colors
        
        :param h: hue
        :param s: saturation
        :param v: value
        :return: a tuple auf rgb-values
        """
        c = s * v
        x = c * (1 - abs(((h / 60) % 2) - 1))
        m = v - c
        rs, gs, bs, = (c, x, 0) if 0 <= h < 60 else ((x, c, 0) if 60 <= h < 120 else ((0, c, x) if 120 <= h < 180 else (
            (0, x, c) if 180 <= h < 240 else ((x, 0, c) if 240 <= h < 300 else (c, 0, x)))))
        return rs + m, gs + m, bs + m
    
    @staticmethod
    def contour_plot(polar: tuple, angle: bool) -> tuple:
        """
        calculates the contour lines (and angle lines if wanted) of the the plot
        :param polar: the polar coordinates of the pixel, which should be translated
        :param angle: determines if the angle lines should be plotted
        :return: the color of the pixel
        """
        r0 = 0.0
        r1 = 5e-2
        while polar[0] > r1:
            r0 = r1
            r1 = r1 * np.e
        r = (polar[0] - r0) / (r1 - r0)
        q1 = 1 - r ** 10
        v = 1
        if angle:
            phi = polar[1]
            phi /= np.pi
            phi *= 180
            phi %= 20
            phi /= 18
            v = 1 - (2 * phi) ** 10 if phi < 0.5 else 1 - (2 * (1 - phi)) ** 10
        return PlotterComplex.hsv_to_rgb((polar[1] / np.pi) * 180, 1, 0.4 + 0.6 * v * q1)
    
    @staticmethod
    def kart_to_polar(x: float, y: float) -> tuple:
        """
        translates from cartesian to polar coordinate space
        :param x: the value of the x-Axis
        :param y: the value of the y-Axis
        :return: a tuple (radius, angle) which describes the same point
        """
        r = abs(x + y * 1j)
        return r, 0 if r == 0 else (np.arccos(x / r) if y >= 0 else (2 * np.pi - np.arccos(x / r)))
    
    def rescale(self, i, j):
        """
        rescales a point (i, j) to another coordinate space\n
        different behavior when squish is set to true
        
        :param i: the x-value
        :param j: the y-value
        :return: the values in the new coordinate space
        """
        if self.squish:
            return (i - self.resolution / 2) / self.resolution * self.distance, \
                   (j - int(self.resolution * self.format[1] / self.format[0]) / 2) / int(self.resolution * self.format[1] / self.format[0]) * self.distance
        return (i - self.resolution / 2) / self.resolution * self.distance, \
               (j - self.resolution / 2) / self.resolution * self.distance + self.distance / 6
    
    @staticmethod
    def color_correct(image):
        """
        squishes all colors in the interval [0, 1[ and rotates the image by 90°
        :param image: the image, which is edited
        :return: the edited image
        """
        return np.rot90(1 - (1 / (image + 1)))
    
    @staticmethod
    def query(x: float, y: float, contour: bool = False, angle: bool = True) -> tuple:
        """
        translates an complex number to an pixel (finds the corresponding color, etc.)
        
        :param x: the reel value
        :param y: the imaginary value
        :param contour: determines if the contour lines should be plotted
        :param angle: determines if the angle lines should be plotted
        :return:
        """
        polar = PlotterComplex.kart_to_polar(x, y)
        if contour:
            return PlotterComplex.contour_plot(polar, angle)
        return PlotterComplex.hsv_to_rgb((polar[1] / np.pi) * 180, 1, polar[0])
    
    def plot_func(self, function: callable, contour: bool = False, angle: bool = False) -> np.ndarray:
        """
        generates the complex plot of a given function\n
        prints warnings in the console, if an overflow or a division by 0 is made. The pixel at that position is then set to 0.
        
        :param function: the function of which a complex plot is created
        :param contour: a bool, which determines if the contour lines should be plotted
        :param angle: a bool, which determines if the angle lines should be plotted
        :return: the plot of the function
        """
        image = np.ndarray((int(self.resolution), int(self.resolution * self.format[1] / self.format[0]), 3))
        for i in range(image.shape[0]):
            for j in range(int(image.shape[1])):
                try:
                    i_tmp, l_tmp = self.rescale(i, j)
                    num = (i_tmp + l_tmp * 1j)
                    res = function(num)
                    image[i, j] = self.query(res.real, res.imag, contour, angle)
                except OverflowError:
                    image[i, j] = 0
                    print("Overflow (i =" + str(i) + ", j = " + str(j) + ")")
                except ZeroDivisionError:
                    image[i, j] = 0
                    print("Zero division (i =" + str(i) + ", j = " + str(j) + ")")
        return self.color_correct(image) if not contour else np.rot90(image)
