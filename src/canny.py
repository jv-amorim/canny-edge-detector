import numpy as np
from consts import GAUSSIAN_KERNEL_5, SOBEL_KERNEL_X, SOBEL_KERNEL_Y
from kernel import apply_kernel_to_matrix
from math import pi


def apply_canny_edge_detector_to_img(img, low_threshold = None, high_threshold = None):
  canny_edge_detector = CannyEdgeDetector(low_threshold, high_threshold)
  canny_edge_detector.set_input_img(img)
  canny_edge_detector.apply_edge_detector()
  return canny_edge_detector.get_result_imgs()


class CannyEdgeDetector:

  def __init__(self, low_threshold = None, high_threshold = None):
    self.img = None
    self.applied = False

    self.low_threshold = 20 if (low_threshold is None) else low_threshold
    self.high_threshold = self.low_threshold * 2 if (high_threshold is None) else high_threshold


  def set_input_img(self, img):
    if len(img.shape) != 2:
      raise ValueError('The input image must have only two dimensions!')

    self.img = img
    self.img_height, self.img_width = img.shape


  def apply_edge_detector(self):
    if self.img is None:
      raise ValueError('The input image must be setted before calling this method.')

    self.applied = True

    print('Smoothing the image with Gaussian kernel...')
    self.__smooth_with_gaussian_kernel()

    print('Calculating the gradients with Sobel kernels...')
    self.__calculate_gradient_with_sobel_kernels()

    print('Calculating the gradient magnitude...')
    self.__calculate_gradient_magnitude()

    print('Calculating the gradient direction...')
    self.__calculate_gradient_direction()

    print('Performing the non-maximum suppression...')
    self.__perform_nonmaximum_suppression()

    print('Performing the hysteresis thresholding...')
    self.__perform_hysteresis_thresholding()


  def __smooth_with_gaussian_kernel(self):
    self.smoothed_img = apply_kernel_to_matrix(GAUSSIAN_KERNEL_5, self.img)


  def __calculate_gradient_with_sobel_kernels(self):
    self.gradient_x = apply_kernel_to_matrix(SOBEL_KERNEL_X, self.smoothed_img)
    self.gradient_y = apply_kernel_to_matrix(SOBEL_KERNEL_Y, self.smoothed_img)

  def __calculate_gradient_magnitude(self):
    powered_gradients_sum = np.power(self.gradient_x, 2) + np.power(self.gradient_y, 2)
    self.gradient_magnitude = np.sqrt(powered_gradients_sum)

  def __calculate_gradient_direction(self):
    gradient_direction_in_radians = np.arctan2(self.gradient_y, self.gradient_x)
    gradient_direction_in_degrees = gradient_direction_in_radians * 180 / pi
    self.gradient_direction = gradient_direction_in_degrees


  def __perform_nonmaximum_suppression(self):
    self.nonmaximum_suppressed_img = np.zeros(self.img.shape)

    for row in range(self.img_height):
      for column in range(self.img_width):
        if not self.__does_the_magnitude_value_must_be_suppressed(row, column):
          self.nonmaximum_suppressed_img[row, column] = self.gradient_magnitude[row, column]

  def __does_the_magnitude_value_must_be_suppressed(self, row, column):    
    is_the_extreme_horizontal_border = (column + 1 >= self.img_width) or (column - 1 <= 0)
    is_the_extreme_vertical_border = (row + 1 >= self.img_height) or (row - 1 <= 0)

    if is_the_extreme_horizontal_border or is_the_extreme_vertical_border:
      return True

    current_edge_angle = self.gradient_direction[row, column]
    current_edge_orientation = self.__get_edge_orientation(current_edge_angle)
    current_mag = self.gradient_magnitude[row, column]
    mags = self.gradient_magnitude
    
    if current_edge_orientation == 'horizontal':
      if current_mag < mags[row, column - 1] or current_mag < mags[row, column + 1]:
        return True
    elif current_edge_orientation == 'vertical':
      if current_mag < mags[row - 1, column] or current_mag < mags[row + 1, column]:
        return True
    elif current_edge_orientation == '+45':
      if current_mag < mags[row - 1, column + 1] or current_mag < mags[row + 1, column - 1]:
        return True
    elif current_edge_orientation == '-45':
      if current_mag < mags[row - 1, column - 1] or current_mag < mags[row + 1, column + 1]:
        return True

    return False

  def __get_edge_orientation(self, edge_angle):
    if edge_angle >= 180:
      return 'horizontal'
    if edge_angle < 157.5 and edge_angle >= 112.5:
      return '+45'
    if edge_angle < 112.5 and edge_angle >= 67.5:
      return 'vertical'
    if edge_angle < 67.5 and edge_angle >= 22.5:
      return '-45'
    if edge_angle < 22.5 and edge_angle >= -22.5:
      return 'horizontal'
    if edge_angle < -22.5 and edge_angle >= -67.5:
      return '+45'
    if edge_angle < -67.5 and edge_angle >= -112.5:
      return 'vertical'
    if edge_angle < -112.5 and edge_angle >= -157.5:
      return '-45'
    if edge_angle < -157.5:
      return 'horizontal'


  def __perform_hysteresis_thresholding(self):    
    low_threshold_img = self.__apply_threshold(self.low_threshold)
    high_threshold_img = self.__apply_threshold(self.high_threshold)

    low_threshold_img -= high_threshold_img

    edges_pixels_coords = np.transpose(np.nonzero(high_threshold_img))
    valid_edge_pixels = np.full(self.img.shape, False)

    for edge_pixel_coords in edges_pixels_coords:
      for row_index in range(edge_pixel_coords[0], 3):
        for column_index in range(edge_pixel_coords[1], 3):
          if low_threshold_img[row_index, column_index] != 0:
            valid_edge_pixels[row_index, column_index] = True

    self.thresholded_img = np.where(valid_edge_pixels == False, high_threshold_img, low_threshold_img)

  def __apply_threshold(self, threshold_value):
    thresholded_img = np.copy(self.nonmaximum_suppressed_img)
    thresholded_img[thresholded_img <= threshold_value] = 0
    thresholded_img[thresholded_img > threshold_value] = 255
    return thresholded_img


  def get_result_imgs(self):
    if not self.applied:
      raise ValueError('No result image have been found. Call the apply_edge_detector method before.')

    result_imgs = CannyResultImages()

    result_imgs.smoothed = self.smoothed_img
    result_imgs.gradient_x = self.gradient_x
    result_imgs.gradient_y = self.gradient_y
    result_imgs.gradient_magnitude = self.gradient_magnitude
    result_imgs.nonmaximum_suppressed = self.nonmaximum_suppressed_img
    result_imgs.thresholded = self.thresholded_img

    return result_imgs


class CannyResultImages():
  smoothed = None
  gradient_x = None
  gradient_y = None
  gradient_magnitude = None
  nonmaximum_suppressed = None
  thresholded = None
