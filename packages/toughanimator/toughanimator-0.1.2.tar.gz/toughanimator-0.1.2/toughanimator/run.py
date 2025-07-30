import os
import tough_classes as ta
import pandas as pd
import matplotlib.pyplot as plt

dir_name = "unresolved" #"test_cases
case_name = "3D five spot MINC"
test_case_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir_name) 

case_dir = os.path.join(test_case_dir, case_name)
#case_dir = r"D:\Projects\202506\cake"

#case_dir = r"D:\Projects\202504\polygonal\poly_test"
#case_dir = r"D:\Projects\202501\toughanimator\test_cases\P5_eco2n_1D-radial"
reader = ta.vis_reader(case_dir)
#reader.write_eleme_conne()
#reader.write_geometry()
#reader.write_incon()
#reader.write_result()
#reader.
reader.write_all()


