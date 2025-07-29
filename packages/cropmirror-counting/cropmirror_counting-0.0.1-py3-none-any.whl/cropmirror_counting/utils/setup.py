from distutils.core import setup
from Cython.Build import cythonize
import os

# 确保目标目录存在
os.makedirs("counting/utils", exist_ok=True)


setup(
    ext_modules=cythonize([
        "imageProc.py",
        "jpg2tiff.py", 
        "tif2cog.py", 
        "tiffProc.py", 
        "wmct2wgs84.py"
    ]),
    script_args=['build_ext', '--inplace']
)

