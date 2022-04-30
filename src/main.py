from consts import GAUSSIAN_KERNEL_5
from input_output import get_input_img_name_from_arguments, read_input_img, save_output_img
from kernel import apply_kernel_to_matrix
from utils import ImageUtils


def main():
  input_img_name = get_input_img_name_from_arguments()
  bgr_input_img = read_input_img(input_img_name)
  
  result_img = ImageUtils.convert_bgr_img_to_grayscale(bgr_input_img)
  result_img = apply_kernel_to_matrix(GAUSSIAN_KERNEL_5, result_img)

  save_output_img(result_img, input_img_name)


if __name__ == '__main__':
  main()