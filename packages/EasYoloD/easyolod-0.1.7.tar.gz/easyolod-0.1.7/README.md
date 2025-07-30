# EasYoloD

Easy Yolo Detect

用户快速部署yolo的识别程序，支持onnxruntime, opencv(dnn), openvino

仅需简短几行代码即可实现yolo目标检测

## Provider 介绍

1. onnxruntime:
    + cpu: 适配性最高的版本，不需要GPU即可执行
    + gpu: onnxruntime-gpu 需要英伟达GPU，并且安装对应版本cuda，cudnn之后才能使用，速度快
    + onnxdml: onnxruntime-directml 不需要使用特定GPU，核显也可以允许，而且不需要安装任何额外程序，速度一般，而且仅适用与windos系统
1. openvino: 
    + cpu: 同onnx的cpu一样
    + gpu: 仅适用于intel的GPU，其他GPU不可用
1. opencv: 
    + cpu: 同上
    + gpu: 需要单独编译带有cuda的opencv包，并正确配置路径，并且安装好cuda和cudnn，速度快

## 安装和使用

```bash
pip install EasYoloD
```

Requirements
+ Python 3.8-3.12
+ opencv-python <= 4.10.0.84
+ numpy <= 1.26

使用: 

```python
import EasYoloD

EasYoloD.init(provider='onnxruntime',gpu=False) # onnxruntime-directml 则使用onnxdml，openvino使用 openvino
model = EasYoloD.Model()
# conf 置信度
# ious
# namse 可以是文件，也可以是一个list
model.load('modelpath', conf, ious, names)
# or 你使用的是opencv dnn yolov4的weight模型
# model.load('config path', 'weight path', inputsize, names, conf, nms)

result = model.detect(img=image)
# or 你希望自己处理输出
# result = model.detect_only(img=image)
```
输出示例:

detect:
```
{
  1: [
    {'confidence': 0.89, 'box': [(614, 202), (732, 242)], 'center': (673, 222)}, 
    {'confidence': 0.87, 'box': [(975, 227), (1105, 268)], 'center': (1040, 247)}, 
    {'confidence': 0.87, 'box': [(845, 241), (962, 284)], 'center': (903, 262)}, 
    {'confidence': 0.86, 'box': [(418, 203), (495, 243)], 'center': (456, 223)}, 
    {'confidence': 0.85, 'box': [(713, 233), (822, 273)], 'center': (767, 253)}, 
    {'confidence': 0.83, 'box': [(776, 222), (888, 261)], 'center': (832, 241)}
  ], 
  2: [], 
  3: [
    {'confidence': 0.8, 'box': [(664, 265), (687, 289)], 'center': (675, 277)}
  ], 
  4: [
    {'confidence': 0.86, 'box': [(846, 195), (955, 236)], 'center': (900, 215)}, 
    {'confidence': 0.84, 'box': [(1108, 227), (1208, 273)], 'center': (1158, 250)}
  ], 
  5: [], 
  6: [], 
  7: []
}
```
detect_only:
```
(array([[ 614.5011 ,  202.27354,  732.4082 ,  242.74388],
       [ 975.4805 ,  227.59409, 1105.0723 ,  268.69995],
       [ 845.77277,  241.3953 ,  962.0877 ,  284.1887 ],
       [ 418.44012,  203.71834,  495.6739 ,  243.37538],
       [ 846.04956,  195.53143,  955.15515,  236.9972 ],
       [ 713.3884 ,  233.3027 ,  822.95776,  273.27628],
       [1108.0188 ,  227.39557, 1208.6423 ,  273.43536],
       [ 776.30786,  222.16605,  888.85815,  261.70145],
       [ 664.80615,  265.0358 ,  687.7573 ,  289.32138]], dtype=float32), array([0.88843024, 0.86892086, 0.8652373 , 0.8610253 , 0.858262  ,
       0.84596515, 0.8361889 , 0.83084583, 0.8002863 ], dtype=float32), array([0, 0, 0, 0, 3, 0, 3, 0, 2], dtype=int64))
```