'''
2025/06/30 10:00, 添加slice_counting_predict.py
'''
from distutils.core import setup
from Cython.Build import cythonize
import os

# 确保目标目录存在
os.makedirs("counting/sahi_predict", exist_ok=True)


setup(
    ext_modules=cythonize([
        "sahi_counting_predict.py",
        "slice_counting_predict.py",
    ]),
    script_args=['build_ext', '--inplace']
)

