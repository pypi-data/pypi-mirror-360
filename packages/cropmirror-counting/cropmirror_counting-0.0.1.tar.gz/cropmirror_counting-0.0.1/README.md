
### 说明
ccnet算法执行之后，每个图片输出三个文件

- detected_pts.txt json文件，标识了识别的标点数量和位置。
- result.tif 打上结果标点之后的，geotiff格式的原始图片。
- result.jpg 压缩之后便于web展示的图片。

### run in python env

```shell
#安装本地环境 requirements.txt CCNet_3.8.env.*,
#项目中CCNet_3.8.env.* 是linux的，可能不适用于windows、macos

conda activate CCNet #或者使用本地环境

python main.py --algorithm ccnet --model-file test/ccnet/model/mouse_hole.pth --input-path test/ccnet/images/mouse --output test/ccnet/output

python main.py --algorithm yolo --model-file test/yolo/model/sheep_counting.pt --input-path test/yolo/images --output test/yolo/output
```


### run in docker

```shell
docker run -ti --rm -v ./test:/test --entrypoint /bin/bash harbor.hzw.ruihudata.cn/cropmirror/counting_model:v0.7

conda activate CCNet

python counting/main.py --algorithm ccnet --model-file /test/ccnet/model/mouse_hole.pth --input-path /test/ccnet/images/mouse --output /test/ccnet/output

python counting/main.py --algorithm yolo --model-file /test/yolo/model/sheep_counting.pt --input-path /test/yolo/images --output /test/yolo/output
```

# windows 10

```shell
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
conda install opencv
pip install opencv-contrib-python
pip install ultralytics
pip install scipy
#https://github.com/cgohlke/geospatial-wheels/releases/tag/v2024.2.18
```
