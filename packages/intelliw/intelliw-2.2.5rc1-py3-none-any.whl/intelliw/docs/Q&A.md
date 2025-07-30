# 常见问题




### Q: 算法框架如何获取?

**A**:  安装 -> 获取脚手架

**详情**：

*➡️安装*：`pip install intelliw`

*➡️获取脚手架*：`intelliw init -n 项目名称 -o 输出路径`







### Q: 如何生成`model.yaml`文件?

**A**:  

➡️*通过命令*（推荐）`：intelliw train -p 你的算法框架项目包`自动生成，训练时自动生成， 纯推理服务可以通过此命令生成，但是因为没有训练过程，可能会产生报错，可以忽略

➡️*通过函数生成*：

 ````
 from intelliw.utils.gen_model_cfg import generate_model_config_from_algorithm_config as __generate
 
 # algorithm.yaml文件路径
 algo_yaml_path = os.path.join(项目路径, 'algorithm.yaml') 
 # model.yaml保存路径 与 algorithm.yaml 同级目录
 model_yaml_path = os.path.join(项目路径, 'model.yaml') 
 __generate(algo_yaml_path, model_yaml_path)
 ````





### Q: 如何快速部署**训练任务**?

**A**:  初始化项目 -> 配置服务参数 -> 参数获取 -> 训练过程coding -> 按epoch进行上报(选) -> 保存模型 -> 上报评估结果

**详情**：

➡️*初始化项目*：`intelliw init -n 项目名称 -o 输出路径`

➡️*配置服务参数*：在`algorithm.yaml`中完善项目相关参数，参数相关参考[说明书](instructions.html)，如果无需任何超参可以略过

*➡️参数获取*：在`algorithm.py`的`__init__`中获取所需参数和获取logger

*➡️训练过程coding*：在`algorithm.py`的`train`中进行开发，可以直接import现有工程，将现有工程训练入口放在`train`函数中

*➡️按epoch进行上报*：调用`algorithm.py`的`report_train_info`函数可以按epoch进行结果的上报，无需实现函数

*➡️保存模型* ：训练完成时，调用`self.save("model_path")`函数，模型的保存过程请在`save`函数中实现，模型保存的路径请使用入参路径，详细内容请参考: [训练如何保存模型?](#savemodel)

*➡️上报评估结果*：调用`algorithm.py`的`report_val_info`函数中进行训练结果上报，无需实现函数





### Q: 训练如何获取数据?

**A**:  `self.train_set / self.valid_set / self.test_set`

**详情**：

*➡️对于表格类数据*：`self.train_set` 是训练集，该参数是一个`iterable`对象，开发者可以对其迭代来获取训练数据。训练数据格式如下所示：

```
{   
    // 表头
    "meta": [  
        {"code": "column_a"},
        {"code": "column_b"}
    ],
    // 表体
    "result": [ 
        ["line_1_column_1", "line_1_column_2"],
        ["line_2_column_1", "line_2_column_2"]
    ]
}
```

每次迭代`self.train_set` 都会返回如上的一个`dict`，其中 `meta` 是数据的元数据描述，其中`code` 是列名，不同类型的数据源`meta`字段内容可能会不同，但是一定有`code`字段。`result`是数据集每一行的数据。开发者可以使用这些数据进行训练。

`self.valid_set` 是验证集,`self.test_set` 是测试集, 其数据格式与训练集一致。数据集在平台的训练配置过程中进行配置，框架会根据开发者配置的比例切分数据集。



*➡️对于图像类数据*：`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式相同，使用`self.train_set`即可:  

```
{
  'path': '/{dirpath}/tmp_local_cv_image_data/', 
  'train_set': '/{dirpath}/tmp_local_cv_image_data/train/', 
  'val_set': '/{dirpath}/tmp_local_cv_image_data/val/', 
  'test_set': '/{dirpath}/tmp_local_cv_image_data/test/', 
  'annotations': '/{dirpath}/tmp_local_cv_image_data/annotations/'
}
```

图片存储在当前目录下

```
./tmp_local_cv_image_data
    |-- train    训练集
    |-- val      验证集
    |-- test     测试集
    |-- annotations 标注信息
```

一般标注格式：

```
./tmp_local_cv_image_data     
    |-- train    训练集        
    |     |--- 1.jpg
    |     |--- 2.jpg
    |-- val      验证集        
    |     |--- 3.jpg
    |     |--- 4.jpg
    |-- test     测试集
    |     |--- 5.jpg
    |-- annotations 标注信息    
          |--- 1.json/xml
          |--- 2.json/xml
```

coco专属标注格式 标注文件来自coco官方格式，请按照官方规定使用

```
annotation demo:
{'licenses':{}, 'info':{}, 'categories':{}, 'images':[], 'annotations':[]}

./tmp_local_cv_image_data
    |-- train    训练集
    |     |--- 1.jpg
    |     |--- 2.jpg
    |-- val      验证集
    |     |--- 3.jpg
    |     |--- 4.jpg
    |-- test     测试集
    |     |--- 5.jpg
    |-- annotations 标注信息
          |--- train_set.json
          |--- validation_set.json
          |--- test_set.json
```



*➡️对于文本类数据*：`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式为:  

```
{
    'path': '/{dirpath}/tmp_local_cv_image_data/', 
    'train_set': '/{dirpath}/tmp_local_cv_image_data/train/', 
    'val_set': '/{dirpath}/tmp_local_cv_image_data/val/', 
    'test_set': '/{dirpath}/tmp_local_cv_image_data/test/', 
}
```

文本存储在当前目录下:
文件大小阈值为1G, 超过1G进行文件分割, 文件名从1开始自增, 支持txt,csv,json三种格式

```
./tmp_local_cv_image_data
    |-- train    训练集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- val      验证集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- test     测试集
```





### Q: <span id="savemodel">训练如何保存模型?</span>

**A**:  补全`save`函数 -> 训练结束时调用

**详情**：在服务部署到平台时，模型的保存实际会放到云存储上，所以保存的业务请完整的放在`save`函数中，并使用函数入参中的path

➡️*补全`save`函*数：将模型保存过程完整的实现在`algorithm.py`的`save`函数中， 例如 `torch.save(net, PATH)`, `pickle.dump(obj, PATH, [,protocol])`...  

入参路径如果为文件夹，则会将文件夹打包上传。

➡️*训练结束时调用*：输入的路径如果为文件夹请加上/，例如`./model/`



### Q: 训练如何使用checkpoint？

#### 保存
**A**:  添加`save_checkpoint`函数 -> 补全`save_checkpoint`函数

**详情**：
1 在`algorithm.py`文件中增加`save_checkpoint`函数
```
def save_checkpoint(self, path, **kwargs):
    """
    保存checkpoint模型， 保存为 path 的文件或文件夹会被框架程序自动打包上传到服务器
    Args:
        path : 模型文件路径
        save_best_only: 是否只保存最优的模型。如果save_best_only设置为true，则max_to_keep配置失效。如：save_best_only=true
        max_to_keep：设置checkpoint模型的个数，n<0时全部保存，n>0时保存最近的n个模型。如：max_to_keep=-1
        epoch： 保存checkpoint模型时的迭代次数。如：epoch=3
        indice：保存checkpoint模型时的指标数据。如：indice={"loss": "0.01"}
    Returns:
        无
    """

    # 按照自己算法所用的方法进行检查点保存， 保存路径为 path
```

#### 读取
**A**:  补全`load`函数
```
def load(self, path):
    """
    加载模型
        不需要调用，在这里实现加载checkpoint的方法，并赋值给一个属性就可以，例如：
        self.model = xxxx.load(path)
        上线流程：算法框架会将模型文件放在model/下，然后进行函数的执行
        本地流程：可以通过model.yaml中location字段进行配置，然后会传入path参数
        训练流程：如果训练方式开启checkpoint训练，算法框架会将checkpoint模型文件放在model/下，然后进行函数的执行
    Args:
        path : 模型文件路径，根据 model.yaml 文件中的 location 字段指定
    Returns:
        无
    """
    if self.is_train_mode:
        # 训练时加载checkpoint
        # checkpoint 时保存的模型
    if self.is_infer_mode:
        # 推理时加载模型
        # 训练结束时保存的模型
```




### Q: 如何快速部署**推理服务**?

**A**:  初始化项目 -> 配置服务参数 -> 参数获取 -> 加载模型 -> 推理过程coding -> 设置路由

**详情**：

➡️*初始化项目*：如果无训练项目 `intelliw init -n 项目名称 -o 输出路径`，如果存在训练项目，跳过此步。

➡️*配置服务参数*：在`algorithm.yaml`中完善项目相关参数，参数相关参考[说明书](instructions.html)，如果无需任何超参可以略过

*➡️参数获取*：在`algorithm.py`的`__init__`中获取所需参数和获取logger

➡️*加载模型*：在`algorithm.py`的`load`中通过入参路径加载模型，此函数无需调用，程序运行时自动加载。详细使用参考：[推理如何获取模型？](#getmodel)

*➡️推理过程coding*：在`algorithm.py`的`infer`中，或`Algorithm`类下自定义函数中定义网络推理过程，网络请求输入数据通过`infer_data`获取

➡️设置路由：在`algorithm.yaml`中通过`router`参数进行定义，参数定义参考[说明书](instructions.html)，详细使用参考[推理如何设置服务路由？](#setrouter)





### Q: <span id="getmodel">推理如何获取模型?</span>  

**A**:  *注⚠️：不要在网络请求时重复加载模型，模型应该只加载一次，然后作为全局属性给每个请求使用

在`algorithm.py`的`load`中通过入参路径加载模型，入参路径与`model.yaml`中的`location`参数一致，此函数无需调用，程序运行时自动加载，将加载的模型赋值给全局变量或类属性，以便后续网络请求复用。

例如:

```
my_model = None
class Algorithm:
    def __init__(self, parameters):
        pass
        
    def load(self, path):
        # 1 赋值给全局变量：
        global my_model
        my_model = xxx.load(path)

        # 2 赋值给类属性：
        self.my_model =  xxx.load(path)
```





### Q: <span id="setrouter">推理如何设置服务路由？</span>

**A**:   注⚠️: 两种方法**选一种**即可。 **不要删除**Algorithm类中的`infer`函数, 不使用`pass`就行

➡️*通过配置文件*：在`algorithm.yaml`中通过`router`参数进行定义

例如：

```
AlgorithmInformation:
  algorithm: pass
  desc: 展示算法
  name: demo
  router:
  - path: "/predict"    # 服务访问地址  127.0.0.1:8080/predict
    func: "myinfer"     # 推理对应的Algorithm类中函数名称
    method: "post"      # 请求方式
    need_feature: true  # 是否定义了特征工程 
    desc: ""            # 描述
```



➡️*通过装饰器*：

例如：

```
from intelliw.feature import Application

@Application.route("/infer-api", method='get', need_feature=True)
def myinfer(self, infer_data):
		pass

```





### Q: 推理如何获取网络请求参数？

**A**：建议网络传输使用 `json` 的方式， `form-data`等方式无法保证复杂数据的数据结构

➡️*简单请求*： 通过函数入参`infer_data`即可拿到输入数据，通常`infer_data`等于`方式self.request.json`

➡️*复杂请求*：

```
self.request dict[str, object]: 请求体
    |- self.request.header  object: 请求头
    |- self.request.files   List[file]: form-data 文件列表
    |- self.request.query   Dict[str]str: url参数
    |- self.request.form    Dict[str]list: form表单参数
    |- self.request.json    object: json参数
    |- self.request.body    bytes: raw request data
```







### Q: 项目如何打包？

**A**：本地调试无误后，可使用`intelliw`命令进行打包，生成的算法包/模型包路径可以使用

`--output_path` 参数指定，若不指定，默认会生成到 `target` 目录下。

➡️*生成算法包*:  `intelliw  package_iwa --path ${algo_path} --output_path xxxx`

➡️*生成模型包*: ` intelliw package_iwm --path ${algo_path} --output_path xxxx`





### Q: 如何进行项目测试？

**A**：通过框架中自带的 `debug_controller.py`文件进行项目 `debug`, 如果项目中不存在此文件， 可以通过`intelliw init_debug`命令生成在当前目录中