# 算法框架使用手册

## 1. 流程概述

算法平台支持开发者导入算法包或模型包。

### 1.1  算法导入

开发者自行导入算法包的使用流程如下所示。开发者导入编写的算法包，平台校验确认算法包符合要求后，开发者可以使用导入的算法包创建模型。创建好的模型可以在平台进行训练。模型训练好后，开发者可以将该模型上线，成功上线后，即可使用该服务进行推理。

```
导入算法 -> 新建模型 -> 训练 -> 推理
```

### 1.2 模型导入

开发者导入模型包的使用流程如下所示。开发者编写、训练好模型包后，将模型包导入算法平台，平台校验确认算法包符合要求后，开发者可以使用导入的模型包上线，成功上线后，即可使用该服务进行推理。

```
导入模型 -> 推理
```

### 1.3  应用导入

开发者导入模型包使用流程如下所示。开发者导入模型包，上线即可使用。

```
导入应用 -> 上线
```

## 2. 算法包

### 2.1  算法包目录结构

一个典型的算法包目录结构如下图所示:

```shell
${my algorithm}  
    ├── algorithm.py          算法入口文件
    ├── algorithm.yaml        算法描述文件
    ├── README.md             项目描述文件
    ├── debug_controller.py    本地开发测试文件
    ├── requirements.txt      python 依赖包
    └── docs                  算法框架使用说明
        ├── README.md         框架使用说明
        └── instructions.md   算法文件说明
```

- `algorithm.py` 是算法文件，用户编写的主要逻辑入口在这个文件中。
- `algorithm.yaml` 是算法的描述文件，这个文件定义了算法的基本信息，是算法包的元数据描述。
- 用户代码中需要依赖的python 包，可以在 `requirements.txt` 中声明，平台在加载用户的算法包时，会根据该文件安装依赖包。
- 如果用户需要使用自定义的镜像，可以提供 `Dockerfile`，平台会使用该 `Dockerfile` 来构建运行算法包的镜像。

各文件说明如下表所示：

| 文件               | 必须 | 说明             |
|------------------|----|----------------|
| algorithm.py     | Y  | 算法入口文件         |
| algorithm.yaml   | Y  | 算法描述文件         |
| requirements.txt | N  | 算法包python库依赖文件 |
| Dockerfile       | N  | 算法包自定义镜像构建文件   |
| README.md        | N  | 算法说明文件         |

### 2.2  算法描述文件·`algorithm.yaml`

`algorithm.yaml` 是算法描述文件，该文件对算法进行了基本描述，包括算法的基本信息、特征工程转换函数、超参数定义、推理API等，是算法的元数据描述。

算法描述文件使用 YAML格式，各字段定义详见下表：

*Algorithm*：

| 参数                           | 参数说明                            | 必填 | 类型     | 示例数据                     |
|------------------------------|---------------------------------|----|--------|--------------------------|
| Algorithm.name               | 算法包名称                           | Y  | string | demo_algorithm           |
| Algorithm.desc               | 算法描述                            | Y  | string | 示例算法                     |
| Algorithm.example            | 示例调用代码                          | N  | string |                          |
| Algorithm.ref                | 算法url（如 wiki 页面、github 页面等 url） | N  | sring  | <https://www.diwork.com> |
| Algorithm.requestMem         | 算法运行内存最小值                       | N  | string | 256m                     |
| Algorithm.isGpu              | 算法运行是否使用GPU                     | N  | bool   | false                    |
| Algorithm.isDistributed      | 算法运行是否使用分布式                     | N  | bool   | false                    |
| AlgorithmInformation.command | 自定义算法启动命令                       | N  | list   |                          |
| AlgorithmInformation.args    | 自定义算法启动参数                       | N  | list   |                          |
| AlgorithmInformation.system  | 算法运行时的系统参数                      | N  | map    |                          |
  
  
  
  

*AlgorithmInformation.system*：  
AlgorithmInformation.system.parameters[]:

| 参数                                           | 参数说明        | 必填 | 类型          | 示例数据      |  
|----------------------------------------------|-------------|----|-------------|-----------|
| AlgorithmInformation.system.parameters[]     | 系统环境变量配置    | Y  | object list |           |  
| AlgorithmInformation.system.parameters[].key | 系统环境变量key   | Y  | string      | env1      |  
| AlgorithmInformation.system.parameters[].val | 系统环境变量配置当前值 | N  | string      | env_value |  

例如：

```
AlgorithmInformation:
  ...
  system:     
     parameters:
      - key: 'env1'
        val: 123
      - key: 'env2'
        val: 'intelliw'
  algorithm:
     ...
```

*Algorithm.router[]*：

| 参数                              | 参数说明                            | 必填 | 类型           | 示例数据                |
|---------------------------------|---------------------------------|----|--------------|---------------------|
| Algorithm.router[]              | 算法上线后的推理接口                      | N  | object array |                     |
| Algorithm.router[].path         | 接口api                           | Y  | string       | /api/demo/infer     |
| Algorithm.router[].func         | 接口调用的推理函数（函数需要在algorithm.py中实现） | Y  | string       | infer               |
| Algorithm.router[].desc         | 接口描述                            | N  | string       | 推理接口api             |
| Algorithm.router[].method       | 请求方式                            | N  | string       | get/post/put/delete |
| Algorithm.router[].need_feature | 请求数据是否需要进行特征处理                  | N  | bool         | false               |

*Algorithm.algorithm[]*：

| 参数                                                    | 参数说明                                                        | 必填 | 类型                    | 示例数据         |
|-------------------------------------------------------|-------------------------------------------------------------|----|-----------------------|--------------|
| Algorithm.algorithm                                   | 算法详细描述                                                      | Y  | Object                |              |
| Algorithm.algorithm.desc                              | 算法描述                                                        | Y  | string                | 示例算法         |
| Algorithm.algorithms.transforms[]                     | 特征工程函数定义                                                    | Y  | object array          |              |
| Algorithm.algorithms.transforms[].type                | 特征工程函数阶段，支持 pre-train：训练前， pre-predict：推理前，post-predict：推理后 | Y  | string                | pre-train    |
| opetion.min                                           |                                                             |    |                       |              |
| Algorithm.algorithms.transforms[].functions[]         | 具体特征工程函数                                                    | Y  | object array          |              |
| Algorithm.algorithms.transforms[].key                 | 特征工程函数名，即函数签名的函数名称                                          | Y  | string                | convert_data |
| Algorithm.algorithms.transforms[].name                | 特征工程函数名称                                                    | Y  | string                | 特征转换         |
| Algorithm.algorithms.transforms[].desc                | 特征工程函数描述                                                    | N  | string                | 特征转换         |
| Algorithm.algorithms.transforms[].can_split           | 此函数是否按行处理数据                                                 | N  | false                 | true         |
| Algorithm.algorithms.transforms[].parameters[]        | 特征工程函数参数定义                                                  | N  | object array          |              |
| Algorithm.algorithms.transforms[].parameters[].key    | 特征工程函数参数key                                                 | Y  | string                | parameter_1  |
| Algorithm.algorithms.transforms[].parameters[].name   | 特征工程函数参数名称                                                  | Y  | string                | 特征转换参数       |
| Algorithm.algorithms.transforms[].parameters[].val    | 特征工程函数参数当前值                                                 | N  | string/number/boolean | hello        |
| Algorithm.algorithms.transforms[].parameters[].option | 特征工程函数参数配置项，详见参数配置项说明                                       | N  | object                |              |
| Algorithm.algorithms.parameters[]                     | 算法超参数                                                       | Y  | object array          |              |
| Algorithm.algorithms.parameters[].key                 | 算法超参数key                                                    | Y  | string                | parameter_2  |
| Algorithm.algorithms.parameters[].name                | 算法超参数名称                                                     | Y  | string                | 参数2          |
| Algorithm.algorithms.parameters[].val                 | 算法超参数当前值                                                    | N  | string/number/boolean | 123          |
| Algorithm.algorithms.parameters[].option              | 算法超参数配置项，详见参数配置项说明                                          | N  | object                |              |

*Algorithm.algorithms.transforms\[\].parameters\[\].option，与Algorithm.algorithms.parameters\[\].option
中的参数定义如下表所示*：

| 参数                  | 参数说明                                              | 必填 | 类型                    | 示例数据    |
|---------------------|---------------------------------------------------|----|-----------------------|---------|
| option.type         | 参数类型，目前支持 string、booean、integer、double、array(int) | Y  | string                | integer |
| option.defaultValue | 参数默认值                                             | N  | string/number/boolean | 1       |

开发者上传完毕算法包，创建数据模型是可以配置配置文件中定义的参数，平台会根据option 中的配置，选取合适的控件进行展示校验。

一个简单的算法描述文件示例如下：

```yaml
AlgorithmInformation:
  name: "demo-algorithm"
  desc: "示例算法"
  example: ""
  ref: "http://github.com/microsoft/LightGBM"
  isGpu: true
  isDistributed: true
  requestMem: "512M"
  algorithm:
    desc: "示例算法"
    transforms:
      - type: "pre-train"
        functions:
          - desc: "数据增强"
            name: "数据增强"
            key: "convert_data"
            parameters:
              - key: "convert_data_param"
                desc: "数据增强参数"
                name: "数据增强参数"
                val: true
                option:
                  defaultValue: true
                  type: "boolean"
    parameters:
      - key: "hyper_parameter_1"
        name: "超参数1"
        desc: "超参数1"
        val: true
        option:
          defaultValue: true
          type: "boolean"
```

### 2.3  算法入口文件 algorithm.py

#### 2.3.1 概述

algorithm.py 是算法入口文件，开发者的主要入口逻辑需在该文件中实现，平台读取并运行该文件，实现训练、推理等逻辑。algorithm.py
文件中需要定义 `Algorthm` 类，该类定义如下所示。开发者根据需求去实现其中特定函数。

```python
class Algorithm:
    """
    算法类， 导入的算法必须定义class Algorithm， 并放入 algorithm.py 文件中
    """

    def __init__(self, parameters):
        """
        初始化， parameters 为 dict格式的参数信息， 比如
        {
            "params1": "value1",
            "params1", 2
        }
        """
        self.parameters = parameters
        self.logger = self.parameters['framework_log']  # 日志
        pass

    def load(self, path):
        """
        加载模型
            不需要调用，只需要根据加载模型的方式是上线或checkpoint训练，在这里实现加载模型的方法，并赋值给一个属性就可以，例如：
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
            pass
        if self.is_infer_mode:
            pass

    def save(self, path):
        """
        保存模型， 保存为 path 的文件或文件夹会被框架程序自动打包上传到服务器
        如果是path是文件夹，需要加上/， 系统会创建该文件夹
            Args:
                path : 模型文件路径， 文件名或文件夹名，根据算法自定义
            Returns:
                无
        """
        pass

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
        pass

    def train(self, train_data, val_data, **kwargs):
        """
        模型训练
            Args:
                self.train_set 或 train_data : 训练数据
                self.valid_set 或 val_data : 验证数据
                self.test_set : 测试数据
                [{
                    "meta": [   // 表头
                        {"code": "column_a"},
                        {"code": "column_b"}
                    ],
                    "result": [ // 表体
                        ["line_1_column_1", "line_1_column_2"],
                        ["line_2_column_1", "line_2_column_2"]
                    ]
                },...]

                kwargs: 特征工程后返回的数据
                {
                    "target_cols":   [{"col": 目标列下标,"column_name": 目标列名称},...] // 目标列
                    "category_cols": [1,2,3]     // 类别列下标
                    "column_meta":   [Employee_ID,Gender,Age,...]    // 原始数据的列名
                    "column_relation_df": Dataframe // the map between the input columns and output columns, if column is droped, it will not exist in column_relation_df!
                }
            Returns:
                无
        """
        pass
```

#### 2.3.2 函数调用过程

```shell
# 算法包Algorithm调用过程
# 导入算法包
 -> __init__
# 训练
 -> __init__ 
# 如果checkpoint训练则加载模型
 -> if CHECKPOINT_MODE: load
 -> pre-train transfrom functions 
 -> train(
        -> report_train_info 
        -> sava 
        -> report_val_info
      )
# 推理
 -> __init__ 
 -> load
 -> pre-predict transfrom functions 
 -> infer
 -> post-predict transfrom functions
```

对于导入的算法包，平台会在特定业务逻辑中调用特定的函数，其主要业务与调用函数的调用关系如上所示。

- 导入算法包环节，平台会实例化开发者实现的 `Algorithm` 类，调用该类的`__init__`构造函数，以验证该算法文件可以正常加载。

- 训练环节，平台首先会实例化开发者实现的 `Algorithm` 类，调用构造函数`__init__`
  方法。实例化成功后，平台根据用户的配置加载训练数据，如果用户在 `algorithm.yaml` 中定义了`pre-train`
  环节的特征工程函数，算法框架会调用`algorithm.py`文件或模块中定义的对应函数。数据经过特征工程函数处理后，平台会调用`train`
  函数，开发者需要在该函数中实现主要训练逻辑。训练过程中，开发者可以调用`report_train_info`上报训练过程中的`loss`、`lr`
  等训练过程数据。训练得到的模型，开发者需要在`save` 方法中进行保存。开发者将模型保存逻辑实现在`save`函数中，并在`train`
  方法中调用。平台会将用户保存的模型文件保存到云端。得到训练模型后，用户可以对模型进行验证，验证的结果通过调用`report_val_info`
  进行上报。

- 推理环节，平台首先会实例化开发者实现的 `Algorithm` 类，调用构造函数`__init__`方法。实例化成功后，框架会调用`load`
  函数，来加载训练环节保存的模型文件。模型加载成功后，视为模型上线成功。用户不论是通过暴露的API调用还是定时调用，算法框架会调用用户编写的infer函数，进行推理。调用infer函数前，如果用户在`algorithm.yaml`
  文件中定义了`pre-predict`
  环节的特征工程函数，平台会将输入的数据传递给定义的特征工程函数。特征工程函数调用完毕后，平台会调用开发者编写的`infer`
  函数，开发者在该函数中实现推理逻辑，并返回推理结果。如果开发者定义了`post-predict`
  环节的特征工程函数，平台会使用开发者返回的推理结果作为参数调用对应的特征工程函数。

#### 2.3.3 函数说明

##### 2.3.3.1 __init__

函数：`__init__ (self, parameters)`

该函数是`Algorithm`的构造函数，`parameters`是开发者在`algorithm.yaml`中定义的超参数。`parameters` 是一个`dict`
，其键为描述文件定义的`Algorithm.algorithms.parameters[].key`，其值为用户在训练时配置的超参数值，
在算法框架启动时，会根据配置文件进行参数类型转换，并将实例化后的`logger`放入`parameters`
，使用时直接通过`parameters.get('framework_log')`获取。

##### 2.3.3.2 load

函数：`load(self, path)`

开发者需要在`load`函数中实现模型加载逻辑。

1. 推理上线过程中，算法框架会调用该方法，执行用户定义的模型加载逻辑。模型文件的绝对路径会在`path`
   参数中传递。该模型文件是用户在训练过程中产生的，平台会在推理时将模型文件加载到path。
2. checkpoint训练时，算法框架也会调用该方法，执行用户定义的模型加载逻辑。checkpoint模型文件的绝对路径会在`path`参数中传递。

```python
# 示例：    
def load(self, path):
    if self.is_train_mode:
        # 加载checkpoint模型逻辑
        pass
    if self.is_infer_mode:
        # 加载训练好的模型逻辑
        pass
```

##### 2.3.3.3 save

函数：`save(self, path)`

`save`函数是模型保存函数，开发者需要将用户的模型保存逻辑在该函数中进行实现，并在训练结束后调用该方法保存模型。`path`
是模型保存路径，用户可以使用相对路径保存到算法包所在的某个路径下，平台根据会将该路径下生成的模型文件打包上传，保存至云端。

##### 2.3.3.4 save_checkpoint

函数：`save_checkpoint(self, path, **kwargs)`

`save_checkpoint`
函数是模型训练过程中保存checkpoint函数，开发者需要将训练过程中保存checkpoint模型逻辑在该函数中实现，同时需要在load(self,
path)函数中写明checkpoint训练加载模型的逻辑。

注： `save_checkpoint`方法需要在save方法之前调用，否则会报异常。

```txt
示例：
save_checkpoint(path, max_to_keep=-1, epoch=0, indice={"loss": 0.01}, save_best_only=true)
```

参数：

- path: checkpoint模型保存的路径，用户可以使用相对路径保存到算法包所在的某个路径下，平台根据会将该路径下生成的模型文件打包上传，保存至云端。
- save_best_only:
  是否只保存最优的模型,开发者可在需要保存最优模型的位置调用save_checkpoint方法并设置save_best_only参数为True。如果save_best_only设置为true，则max_to_keep配置失效。如：save_best_only=true
- max_to_keep：设置checkpoint模型的个数，n<0时保存全部保存，n>0时保存最近的n个模型。如：max_to_keep=n
- epoch： 保存checkpoint模型时的迭代次数。如：epoch=3
- indice：保存checkpoint模型时的指标数据。如：indice={"loss": "0.012"}

##### 2.3.3.5 train

函数： `train(self, **kwargs)`

*注*： 以下格式只针对表格数据， cv, nlp 类请参考 [数据集](#dataset)

`train` 函数是训练入口函数，开发者需要在该函数中实现训练逻辑。`self.train_set` 是训练集，该参数是一个`iterable`
对象，开发者可以对其迭代来获取训练数据。训练数据格式如下所示：

```json
{
  // 表头
  "meta": [
    {
      "code": "column_a"
    },
    {
      "code": "column_b"
    }
  ],
  // 表体
  "result": [
    [
      "line_1_column_1",
      "line_1_column_2"
    ],
    [
      "line_2_column_1",
      "line_2_column_2"
    ]
  ]
}
```

每次迭代`self.train_set` 都会返回如上的一个`dict`，其中 `meta` 是数据的元数据描述，其中`code`是列名，不同类型的数据源`meta`
字段内容可能会不同，但是一定有`code`字段。`result`是数据集每一行的数据。开发者可以使用这些数据进行训练。
`self.valid_set` 是验证集,`self.test_set` 是验证集, 其数据格式与训练集一致。数据集在平台的训练配置过程中进行配置，框架会根据开发者配置的比例切分数据集。

`**kwargs`:特征工程后返回的数据, 内容如下：

```json
{
  "target_cols": [
    {
      "col": 目标列下标,
      "column_name": 目标列名称
    },
    ...
  ]
  // 目标列
  "category_cols": [
    1,
    2,
    3
  ]
  // 类别列下标
  "column_meta": [
    Employee_ID,
    Gender,
    Age,
    ...
  ]
  // 原始数据的列名
  "column_relation_df": Dataframe
  // the map between the input columns and output columns, if column is droped, it will not exist in column_relation_df!
}
```

训练结束后，开发者需要在该函数调用`save`方法来保存模型。训练过程的`loss`、`lr`等数据可以调用`report_train_info`
进行上报，模型验证结果可以调用`report_val_info`函数进行上报。

##### 2.3.3.6 infer

函数： `infer(self, infer_data)`

`infer` 函数是推理函数，开发者需要在函数中实现推理逻辑。参数`infer_data`是json输入数据。对于API调用，该参数的格式如下所示：

```shell
推理服务Args:
    infer_data : 推理请求数据, json输入的参数, 类型可以为列表/字符串/字典

    如果使用特征工程, infer_data格式有硬性要求:
    {
        "data": 任意格式，如果配置特征工程，此数据为处理后的数据 # 推理数据
        "original_data":  原始输入的data ，防止数据在通过特征处理后丢失原先的数据
    }

    self.request dict[str, object]: 请求体
        |- self.request.header  object: 请求头
        |- self.request.files   List[file]: form-data 文件列表
        |- self.request.query   Dict[str]str: url参数
        |- self.request.form    Dict[str]list: form表单参数
        |- self.request.json    object: json参数
        |- self.request.body    bytes: raw request data

批处理服务Args:
    infer_data : 批处理输入数据
                [{
                    "meta": [   // 表头
                        {"code": "column_a"},
                        {"code": "column_b"}
                    ],
                    "result": [ // 表体
                        ["line_1_column_1", "line_1_column_2"],
                        ["line_2_column_1", "line_2_column_2"]
                    ]
                }]
    self.request dict[str, object]: 请求体
    |- self.request.batch_params List[Dict] 批处理接口(/batch-predict)输入参数,为请求中的json数据,用作任务间参数传递

Returns:
    推理结果, json
```

用户可以在data中获取推理输入数据， 请求的相关参数会存储在self.request中，数据参数和用户定义一致

用户调用模型获得的推理结果作为返回值返回给框架。对于API类型的调用，算法框架会将推理结果返回给调用方，对于定时推理类型的调用，算法框架会将返回值写入用户指定的数据源。

执行推理操作时，`infer` 函数的返回值会被序列化为`json` 格式后返回给用户，因此`infer` 函数的返回值必须是可以被 `json.dumps`
序列化的。

*注*：
如果使用特征工程，infer_data格式有硬性要求

```json
{
  "data": 任意格式
  ，
  如果配置特征工程
  ，
  此数据为处理后的数据
  "original_data": 原始输入的data
  ，
  防止数据在通过特征处理后丢失原先的数据
}
```

**自定义推理函数API的方法**：

1. 调用算法包方法Application来设置路由：    
   | 参数 | 必须 | 类型 | 默认值 | 说明 | 示例 |
   | ------------ | ---- | ------ | ------ | --------------------------------------------------------------- | ----------------- |
   | path | Y | 字符串 | | 访问路由 | "/infer-api"      |
   | method | N | 字符串 | post | 访问方式，支持 get post push delete head patch options | method='get'      |
   | need_feature | N | bool | True | 是否需要使用特征工程，如果是自定义与推理无关的函数，请设置False |
   need_feature=True |

  ```python
  from intelliw.feature import Application


@Application.route("/infer-api", method='get', need_feature=True)
def infer(self, infer_date):
    pass
  ```

1. 通过algotiyhm.yaml下Algorithm.router[]进行参数配置
   | 参数 | 必须 | 类型 | 默认值 | 说明 | 示例 |
   | ------------ | ---- | ------ | ------ | --------------------------------------------------------------- | ----------------- |
   | path | Y | 字符串 | | 访问路由 | path: "/predict"  |
   | func | Y | 字符串 | | 路由访问的algorithm.py中的函数 | func: "infer"     |
   | method | N | 字符串 | post | 访问方式，支持 get post push delete head patch options | method: "get"     |
   | need_feature | N | bool | True | 是否需要使用特征工程，如果是自定义与推理无关的函数，请设置False |
   need_feature=True |

  ```yaml
    router:
      - path: "/predict"
        func: "infer"
        method: "get"
        need_feature: false
        desc: ""
  ```

3. 不设置默认会给algorithm.py下的infer函数设置post方法的路由/predict

##### 2.3.3.7  report_train_info

函数：`report_train_info(self, loss, lr, iter, batchsize=1)`

该函数是训练信息上报函数，开发者不需要实现该函数，只需要在训练过程中调用该函数即可。该函数参数定义如下，其中`loss`
是损失函数的`loss`值，`lr`是学习率，`iter`是当前的`iteration`，`batchsize`是每批训练数据大小。

##### 2.3.3.8 report_val_info

函数： `report_val_info(self, **kwargs)`

该函数是评估结果上报函数，开发者不需要实现该函数，只需要在训练结束后根据自身需求调用该函数传递评估结果。
评估结果参数以 `kwargs` 的形式传递，当前平台支持的参数定义如下表所示。开发者可以传递感兴趣的评估结果进行上报，平台会在模型服务的评估结果页面对上报结果进行展示。

```
kwargs = {"metrics":{...}, "feature_importances":{...}}

# 调用
self.report_val_info(metrics={}, feature_importances={})
```

[如何使用](https://uap-wiki.yyrd.com/pages/viewpage.action?pageId=156767267)

##### 2.3.3.9 特征工程函数

开发者可以根据自身算法需要，编写特征工程函数，来对训练数据、推理数据进行预处理、后处理。

特征工程函数需要定义在`Algorithm`类之外，算法框架会根据开发者在`algorithm.yaml`定义的特征工程函数的`key`在`algorithm.py`
中查找加载。

一个典型的特征工程函数如下所示：

```python
def convert_data(data, params):
    # do something with data
    return data
```

在进行训练或推理前，算法框架会调用特征工程函数。调用时，会传递两个位置参数，第一个参数是当前处理的数据，第二个参数是开发者配置的特征工程函数的参数，上述示例中分别取名为`data`
和`params`。其中，`params` 参数格式同`__init__`方法中传递的超参数格式，`data`格式根据特征工程函数所处的调用环节有所不同：

- 对于`pre-train` 阶段的特征工程函数，用户每次对`train_data`或`val_data`
  迭代读取时，读取到的结果会首先传递给特征工程函数做处理，其格式同train环节获取的数据格式。用户可以对`result`
  中的数据进行加工。处理完毕后，需要返回处理后的结果，其格式需要与入参保持一致。

- 对于`pre-predict`阶段的特征工程函数，`data`格式根据推理任务不同有所不同，其格式与`infer`函数的`test_data`
  一致，调用`infer`函数前，算法框架会将`test_data`传递给特征工程函数，再将特征工程函数的返回值传递给`infer`函数。

- `post-predic`t阶段的特征函数，其`data`为`infer`函数的返回值。

#### 2.3.4 构造算法包

编写好算法包后，开发者可以通过算法框架对算法文件夹打包

```shell
intelliw  package_iwa --path ${算法文件路径} --output_path xxxx
```

## 3. 模型包

### 3.1 模型包格式

一个典型的模型包目录结构如下所示：

```shell
${my model}  
    ├── model      
    | └── gbm.model
    ├── algorithm.py      
    ├── algorithm.yaml    
    ├── model.yaml        
    ├── README.md         
    └── requirements.txt  
```

模型包目录结构与算法包类似，主要不同是增加了模型描述文件`model.yaml`
。同时，开发者可能将训练好的模型文件放置在模型包内，上述示例中，`model` 目录即为模型文件目录。模型文件目录可在`model.yaml`
中进行配置。

各文件说明详见下表：
| 文件 | 必须 | 说明 |
| ---------------- | ---- | ---------------------- |
| algorithm.py | Y | 算法入口文件 |
| algorithm.yaml | Y | 算法描述文件 |
| model.yaml | Y | 模型配置文件 |
| requirements.txt | N | 算法包python库依赖文件 |
| README.md | N | 算法说明文件 |

### 3.2 模型配置文件 `model.yaml`

`model.yaml`是模型配置文件。`algorithm.yaml`描述了算法的基本能力，如支持的特征函数、支持的超参数等，而`model.yaml`
描述了算法的具体运行时，给出了可配置项的具体值，如加载模型文件的路径、启用哪些特征函数、超参数的具体值等。

*注：使用算法框架本地进行训练时会自动通过`algorithm.yaml`生成`model.yaml`*

模型描述文件使用YAML格式，各配置项如下表：
| 参数 | 参数说明 | 必填 | 类型 | 示例数据 |
| ------------------------------------- | ----------------------------------------------------------------------------------- | ---- | --------------------- | ----------------- |
| Model.name | 模型包名称 | Y | string | demo_model |
| Model.desc | 模型包描述 | Y | string | 示例模型 |
| Model.requestMem | 算法运行内存最小值 | N | string | 256m |
| Algorithm.isGpu | 算法运行是否使用GPU | N | bool | false |
| Algorithm.isDistributed | 算法运行是否使用分布式 | N | bool | false |
| Model.location | 模型文件路径 | Y | string | ./model/gbm.model |
| Model.algorithm | 模型使用的算法 | Y | object |
| Model.algorithm.name | 算法名称 | Y | string | demo_algorithm |
| Model.algorithm.desc | 算法描述 | Y | string | 示例算法 |
| Model.transforms[]                    | 模型包启用的特征函数，特征函数需在algoritm.yaml中定义 | Y | object array |
| Model.transforms[].type | 特征工程函数阶段，支持 pre-train：训练前，pre-predict：推理前，post-predict：推理后 | Y | string |
pre-train |
| Model.transforms[].functions[]        | 启用的特征工程函数 | Y | object array |
| Algorithm.algorithms.transforms[].key | 特征工程函数名，即函数签名的函数名称 | Y | string | convert_data |
| Model.transforms[].parameters[]       | 特征工程函数参数配置 | N | object array |
| Model.transforms[].parameters[].key | 特征工程函数参数key | Y | string | parameter_1 |
| Model.transforms[].parameters[].val | 特征工程函数参数值 | N | string/number/boolean | hello |
| Algorithm.algorithms.parameters | 算法超参数配置，以key/value形式配置 | Y | object | arg_1: true |

一个简单的模型描述文件示例如下，该描述文件指定了模型加载路径：`" ./model/gbm.model"`，指定了算法在`pre-predict`
阶段要启用`convert_data`特征工程函数，且为该函数传递了配置项`convert_data_param`，其值为`true`
。同时，为算法配置了三个超参数：`parameter_a`，`param_2`，`param_3`。

```yaml
Model:
  name: "lightgbm"
  desc: "lightgbm测试用例"
  isGpu: true
  isDistributed: true
  requestMem: "256M"
  location: "./model/gbm.model" #  保存的模型文件路径
  algorithm:
    name: "lightgbm"
    desc: "流程测试算法"
  transforms:
    - type: "pre-predict"
      functions:
        - key: "convert_data"
          parameters:
            - key: "convert_data_param"
              val: true
  parameters:
    parameter_a: treu
    param_2: 123
    param_3: "hello"

```

### 3.3 模型执行过程

```
# 导入模型
 -> __init__
 -> load
# 推理
 -> __init__ 
 -> load
 -> pre-predict transfrom functions 
 -> infer
 -> post-predict transfrom functions
```

开发者编写的`Algorithm`类在模型包各业务环节中调用流程如上图所示。导入模型包时，会实例化`Algorithm`类，调用其`__init__`
方法，之后，会调用`load`方法加载模型，`load`方法执行成功后，视为导入模型成功。上线推理时，算法框架首先会实例化`Algorithm`
类，调用其`__init__`方法，并调用`load`方法加载模型。如果开发者配置了`pre-predic`
t阶段的特征工程函数，推理输入数据在调用`infer`函数前传递给`pre-predict`
的特征工程函数。特征工程函数处理后，算法使用该数据调用`infer`函数。如果用户定义了`post-predict`阶段的特征工程函数，`infer`
函数的返回数据会传递给`post-predict`特征工程函数处理，处理后的结果返回给调用者。

### 3.4 构造模型包

编写好模型包后，开发者可以通过算法框架进行对算法文件夹打包

```shell
intelliw  package_iwm --path ${算法文件路径} --output_path xxxx
```

## 4. 应用包

### 4.1 应用包格式

一个典型的应用包目录结构如下所示：

```
${my app}  
    ├── app.yaml      
    ├── my_app.jar      
    └── Dockerfile        
```

`app.yaml`是模型包描述文件，该文件描述了应用的基本信息。如果用户需要算法平台打包，可以提供`Dockerfile`
文件，算法平台会使用该`Dockerfile`和应用包中的文件打包。
| 文件 | 必须 | 说明 |
| ---------- | ---- | ------------------ |
| app.yaml | Y | 应用包描述文件 |
| Dockerfile | N | 应用包镜像构建文件 |

### 4.2 应用描述文件 `app.yaml`

`app.yaml` 是应用描述文件，平台根据该文件运行应用。

配置文件配置项如下表所示：

| 参数                      | 参数说明        | 必填 | 类型     | 示例数据                                        |
|-------------------------|-------------|----|--------|---------------------------------------------|
| App.name                | 应用名称        | Y  | string | youycTag                                    |
| App.desc                | 应用描述        | Y  | string | 采购标签应用                                      |
| App.requestMem          | 应用运行内存最小值   | N  | string | 512M                                        |
| Algorithm.isGpu         | 算法运行是否使用GPU | N  | bool   | false                                       |
| Algorithm.isDistributed | 算法运行是否使用分布式 | N  | bool   | false                                       |
| App.image               | 应用镜像地址      | N  | string | hub.yonyou.com/intelliw/youyc/youyc_tag:1.0 |
| App.env                 | 应用环境变量配置    | Y  | object |                                             |
| App.env.service.port    | 服务暴露端口号     | Y  | int    | 8080                                        |

其中，`App.image`
是应用镜像地址，如果开发者配置了该地址，算法平台会在上线是加载该镜像，如果没有配置该地址，平台会使用应用包中的`Dockerfile`
构建镜像。`App.env` 是应用的环境变量，开发者填写的环境变量平台会在启动应用时进行传递。`service.port`
是一个特殊的环境变量，其含义是服务暴露端口，平台会将该端口向外网暴露。

一个简单的算法包示例如下：

```yaml
App:
  name: "yonycTag"
  desc: "采购标签应用"
  image: hub.yonyou.com/intelliw/youyc/youyc_tag:1.0
  envs:
    server.port: 8081
    system.code: yonycTagApp
```

### 4.3 构造应用包

编写好应用包后，开发者可以通过算法框架进行对算法文件夹打包

```shell
intelliw  package_iwp --path ${算法文件路径}  --output_path xxxx
```

<a id="dataset"></a>

## 5. 数据集

### 5.1 表格数据集

`self.train_set` 是训练集，该参数是一个`iterable`对象，开发者可以对其迭代来获取训练数据。训练数据格式如下所示：

```json
{
  // 表头
  "meta": [
    {
      "code": "column_a"
    },
    {
      "code": "column_b"
    }
  ],
  // 表体
  "result": [
    [
      "line_1_column_1",
      "line_1_column_2"
    ],
    [
      "line_2_column_1",
      "line_2_column_2"
    ]
  ]
}
```

每次迭代`self.train_set` 都会返回如上的一个`dict`，其中 `meta` 是数据的元数据描述，其中`code`是列名，不同类型的数据源`meta`
字段内容可能会不同，但是一定有`code`字段。`result`是数据集每一行的数据。开发者可以使用这些数据进行训练。
`self.valid_set` 是验证集,`self.test_set` 是验证集, 其数据格式与训练集一致。数据集在平台的训练配置过程中进行配置，框架会根据开发者配置的比例切分数据集。

### 5.2 图片数据集格式

`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式为:

```json
{
  'path': '/{dirpath}/tmp_local_cv_image_data/',
  'train_set': '/{dirpath}/tmp_local_cv_image_data/train/',
  'val_set': '/{dirpath}/tmp_local_cv_image_data/val/',
  'test_set': '/{dirpath}/tmp_local_cv_image_data/test/',
  'annotations': '/{dirpath}/tmp_local_cv_image_data/annotations/'
}
```

图片存储在当前目录下

```shell
./tmp_local_cv_image_data
    |-- train    训练集
    |-- val      验证集
    |-- test     测试集
    |-- annotations 标注信息
```

一般标注格式：

```shell
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

coco专属标注格式
标注文件来自coco官方格式，请按照官方规定使用

```shell
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

### 5.3 文本数据集格式

`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式为:

```json
{
  'path': '/{dirpath}/tmp_local_cv_image_data/',
  'train_set': '/{dirpath}/tmp_local_cv_image_data/train/',
  'val_set': '/{dirpath}/tmp_local_cv_image_data/val/',
  'test_set': '/{dirpath}/tmp_local_cv_image_data/test/'
}
```

文本存储在当前目录下:
文件大小阈值为1G, 超过1G进行文件分割, 文件名从1开始自增, 支持txt,csv,json三种格式

```shell
./tmp_local_cv_image_data
    |-- train    训练集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- val      验证集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- test     测试集
```

### 5.4 数据输出

#### 5.4.1 输出到智能输出源

*使用流程*
通过训练/推理得到数据 -> 标准化输出数据格式 -> 调用输出sdk   
注意⚠️：`id`字段、`ts`字段和`batch_no`为关键字，请勿占用，以防数据丢失

*标准化输出数据格式*

- 返回字段是否与智能输出源数据库定义一致
- 返回字段的列名是否与每行一一对应
- 如果使用数据输出功能，返回数据格式应为
   ```python
   output_data = {
         "meta":[
             {"code":"col1"},
             {"code":"col2"},
             {"code":"col3"}
         ],
         "result":[
             ["col1_value1", "col2_value1", "col3_value1"],
             ["col1_value2", "col2_value2", "col3_value2"],
             ["col1_value3", "col2_value3", "col3_value3"],
         ]
   }
   ```

*调用输出sdk*

```python
from intelliw.feature import OutPutWriter

writer = OutPutWriter()
res_data = writer.write(output_data)
```

*获取输出表元数据*

此数据为输出数据表的字段信息：

```python
[
    {'code': 'customerCode', 'type': 'varchar', 'comment': 'customerCode'},
    {'code': 'deliveryDate', 'type': 'date', 'comment': 'deliveryDate'},
    {'code': 'id', 'type': 'varchar', 'comment': '主键'},
    {'code': 'batch_no', 'type': 'varchar', 'comment': '批次号'}
]
```

其中，`id`字段和`batch_no`为关键字，可以忽略，无需写入数据，写入的数据会被覆盖

获取数据表元数据的方式：

```python
from intelliw.feature import OutPutWriter

writer = OutPutWriter()
# 元数据信息
columns = writer.table_columns  
```


## 6 通用组件

### 6.1 分布式训练

为了满足大规模模型训练的需求，算法框架考虑支持各种主流AI框架的分布式训练模式。
目前已适配:

- PyTorch模型并行训练

### 6.1.1 Torch

> 目前支持模型并行的方式
> 想使用torch，算法同学需要对算法进行以下改造：

- 使用 `torch.distributed.init_process_group` 初始化进程组
- 使用` torch.nn.parallel.DistributedDataParallel` 创建 分布式模型
- 使用 `torch.utils.data.distributed.DistributedSampler` 创建 DataLoader
- 调整其他必要的地方(tensor放到指定device上，Save/Load checkpoint，指标计算等)

#### BN(batch normalization)

- 多卡同步计算BN的时候会显著降低并行效率，如果不适用同步BN则精度会受损。
- 使用 `torch.nn.SyncBatchNorm.convert_sync_batchnorm()` 同步GPU之间的数据。注意，training和test阶段都需要同步

#### 数据同步

使用`Distributed data parallel ` 的时候，需要特殊的函数进行数据的分发: torch.utils.data.distributed.DistributedSampler

#### 必要的新参数

为了使用分布式训练，需要首先初始化进程组，其函数原型为

```python
def init_process_group(backend,
                       init_method=None,
                       timeout=default_pg_timeout,
                       world_size=-1,
                       rank=-1,
                       store=None,
                       group_name=''):
```

- backend ：指定当前进程要使用的通信后端。支持的通信后端有 gloo(CPU分布式训练)，mpi，nccl(GPU分布式训练)
- init_method ： 指定当前进程组初始化方式。可选参数，字符串形式。如果未指定 init_method 及 store，则默认为 env:
  //，表示使用读取环境变量的方式进行初始化。该参数与 store 互斥。根据官网介绍，该参数还支持tcp、共享文件等方式
- rank ： 所有进程中的第几个进程。int 值。表示当前进程的编号，即优先级。rank=0 的为主进程，即 master 节点, 由节点自己控制无需传值。
- world_size ：所有机器中使用的进程数量, 由节点自己控制无需传值
- timeout ： 指定每个进程的超时时间

声明分布式模型使用 `DistributedDataParallel`

```python
class DistributedDataParallel(
    module,
    device_ids=None,
    output_device=None,
    dim=0,
    broadcast_buffers=True,
    process_group=None,
    bucket_cap_mb=25,
    find_unused_parameters=False,
    check_reduction=False,
    gradient_as_bucket_view=False,
    static_graph=False)
```

- model: model对象
- device_ids: 本地GPU的ID（从 0 开始）
- bucket_cap_mb: bucket缓存大小，这个参数涉及到pytorch C++的源代码，请尽量不要修改

负责分配数据的 `torch.utils.data.distributed.DistributedSampler`

```python
class DistributedSampler(dataset,
                         num_replicas=None,
                         rank=None,
                         shuffle=True,
                         seed=0,
                         drop_last=False)
```

- dataset: DataSet对象
- num_replicas: 参与训练的进程数
- seed: shuffle用的随机数种子
- drop_last: 补全数据标识。如果训练数据不是world_size的整倍数，pytorch将会由这个标识来决定最终的几个数据如何处理

#### 推荐运行环境

```shell
dockerhub.yonyoucloud.com/c87e2267-1001-4c70-bb2a-ab41f3b81aa3/intelliw/touch-data-parallel:1.0
```

### 6.2 Spark数据处理

Spark是一款分布式内存计算的统一分析引擎。 其特点就是对任意类型的数据进行自定义计算。
Spark可以计算:结构化、半结构化、非结构化等各种类型的数据结构，同时也支持使用Python、Java、Scala、R以及SQL语言去开发应用程序计算数据。

在算法框架中，可以通过手动开启的方式进行Spark数据处理

```python
from intelliw.feature import Spark

# 获取spark session
sp = Spark.get_spark(master=None, appName=None, conf=None, hive_support=False)

# 通过spark读取文件
content = sp.read_file(filetype="csv", filepath="xxxx")
```

### 6.2.1 初始化

Spark初始化支持本地模式和Standalone模式，Standalone模式需要用户指定集群信息
`get_spark()`的`master`参数，可以指定为 "local"运行本地模式 或 "spark://master:7077" 以运行standalone模式。

### 6.2.2 读取文件

`read_file()`函数可以读取常见的数据格式
`filetype`可以根据文件类型进行指定，支持 csv/txt/json
`filepath`为文件链接，可以是文件夹/文件/文件链接

### 6.2.3 推荐运行环境

```python
dockerhub.yonyoucloud.com/c87e2267-1001-4c70-bb2a-ab41f3b81aa3/intelliw/pyspark3.3.0:py38-jdk8
```

### 6.3 服务缓存
算法框架支持推理服务缓存，当请求内容相同时，会直接返回缓存内容

#### 开启缓存
上线时设置环境变量
```
INFER_CACHE=true
```
#### 缓存超时
默认有效时间为10s， 可以在上线时通过环境变量设置时长，单位s
```
INFER_CACHE_TTL=true
```
#### 通过参数跳过缓存
在请求体中添加参数use_cache=true, 跳过缓存，只支持json格式
```angular2html
{
    "data": "userdata",
    "use_cache": true
}
```

### 6.4 携带上下文的线程池
封装 ThreadPoolExecutor 和 threading.Thread，并自动在创建子线程时传递主线程的上下文
#### 6.4.1 threading.Thread
使用方式：
```python
from intelliw.feature import context as ctx

def sample_task(a,b,c):
    # do something
    pass

thread = ctx.ContextThread(target=sample_task, args=("thread_task", "2", "3"), name="ThreadTest")
thread.start()
thread.join()
```

#### 6.4.2 ThreadPoolExecutor
使用方式：
```python
from intelliw.feature import context as ctx


def sample_task(a, b, c):
    # do something
    pass


with ctx.ContextThreadExecutor(max_workers=3) as context_executor:
    futures = [
        context_executor.submit(sample_task, f"task-{i}", "2", "3") for i in range(5)
    ]
    for future in futures:
        future.result()
```

### 6.5 推理服务性能配置
项目启动时可以通过以下变量控制服务性能， 通过环境变量进行设置  

**CPU数量**：CPU_COUNT  
 - 默认为页面配置的最大值
 - 用来控制线程数量和多进程模式下进程数量

**使用多进程启动服务**：INFER_MULTI_PROCESS  
 - 默认为false
 - 当值为 True 时使用多进程模式，进程数等于CPU_COUNT, 最大8（仅适用于单进程服务，如果服务本身自带多核调用框架，请不要使用，会造成资源抢占）

**最大线程数**：INFER_MULTI_THREAD_COUNT  
 - 默认值 CPU_COUNT*2+1
 - 推理线程数（最大并发数），最大值为32，可以根据自己服务性能进行修改

**最大任务数**：INFER_MAX_TASK_RATIO  
 - 默认为3，代表三倍的线程数
 - 表示推理服务最大允许同时处理的任务数（正在处理+排队任务），最大任务数=INFER_MULTI_THREAD_COUNT*INFER_MAX_TASK_RATIO 


### 6.6 定时任务
算法框架支持通过定时任务来执行python代码，通过`intelliw.utils.crontab`模块进行调用

#### 6.6.1 使用说明
配置joblist进行后台任务配置，支持多任务同时进行
```python
joblist = [
    {'crontab': '0/1 * * * *', 'func': task, 'args': ('job1',)}, # 每分钟执行
    {'crontab': '0 */2 * * * *', 'func': task, 'args': ('job2',)}, # 每隔 2 分钟执行
]
```
 - crontab： crontab表达式
 - func：需要执行的函数
 - args：函数参数

建议配置到 algorithms.py 的 load 函数中，使用非阻塞方式启动到后台，确保不影响主进程的推理服务启动



使用示例：
```python
from intelliw.utils.crontab import Crontab

def task(*args):
    pass

joblist = [
    {'crontab': '0/1 * * * *', 'func': task, 'args': ('job1',)},
    {'crontab': '0 */2 * * * ?', 'func': task, 'args': ('job2',)},
    {'crontab': '0 */3 * * * ? *', 'func': task, 'args': ('job3',)},
]

# sync 同步阻塞，进程会卡在 start，定时执行 job
crontab1 = Crontab(joblist)
crontab1.start()

# async 异步非阻塞，代码会继续向下执行
crontab2 = Crontab(joblist, True)
crontab2.start()

```

### 6.7 链路上报
算法框架支持链路上报，通过`intelliw.utils.iuap_request.async_report_trace_log`模块进行调用  


使用方法：
```python
import os
import time
from intelliw.utils import iuap_request
from intelliw.utils.trace_log import TraceLog

tenant_id = os.environ['TENANT_ID']
# 实例化TraceLog, 自动生成id, startTime, domain('iuap-aip-alg')
trace_log = TraceLog()

# todo 业务逻辑开始
pass
# todo 业务逻辑结束

# 填充数据
ctx = header_ctx.get()

## 链路日志上下文
traceId = ctx.get('traceId', '0')
if traceId == '0':
  trace_log.traceId = 'testzb07'
else:
  trace_log.traceId = traceId
trace_log.apiCode = "aiConsole" # 微服务编码
trace_log.resultCode = 200 # 响应码 200, 4XX, 5XX
trace_log.requestBody = json.dumps({"id": "1"})
trace_log.responseBody = json.dumps({"id": "1"})
trace_log.ytenantId = tenant_id

# 异步上报
iuap_request.async_report_trace_log(tenant_id, trace_log)
```

使用说明：  
 - 需要在任务开始事记录开始时间， 时间为 13位时间戳`time.time()*1000`    
 - 上报函数`iuap_request.async_report_trace_log`字段
    ```python
    def async_report_trace_log(tenant_id: str, trace_log: TraceLog):
      """
      异步上报trace log
      :param tenant_id: 租户id
      :param trace_log: trace log
      """
      pass
    ```


### 6.8 携带恢复租户的上下文信息
算法框架支持携带恢复租户的上下文信息, 通过 `intelliw.utils.iuap_request.post_json` 模块进行调用
算法框架 优先使用 header 中的 X-tenantId 字段来恢复， 否则会使用系统租户恢复。
使用方法:
```python
from intelliw.utils.iuap_request import post_json, AuthType
CALLBACK_URL = ""
data  = {"data": "userdata"}
headers = {"Content-Type": "application/json", "X-tenantId": "your_tenant_id"}
res = post_json(url=CALLBACK_URL, headers=headers, json=data, auth_type=AuthType.YHT) # AuthType.YHT
```

使用说明:
  - AuthType: 是否需要鉴权
    - No = 0 , 不需要鉴权
    - AuthSDK = 1 , authsdk 鉴权
    - YHT = 2 , 友互通 token
  - 函数字段定义: 
    ```python
    def post_json(url: str, headers: dict = None, params: dict = None, json: object = None,
              timeout: float = DEFAULT_TIMEOUT, auth_type=AuthType.AuthSDK, ak=None, ase=None,
              retry: [bool, int] = True) -> Response:
    """
    post request, send data as json

    :param auth_type: 是否需要鉴权 0 不需要 1 authsdk 2 yht
    :param timeout: request timeout
    :param url: request url
    :param headers: request headers
    :param params: request url parameters
    :param json: request body. if data is not `str`, it will be serialized as json.
    :param ak: 用户自定义access key
    :param ase: 用户自定义access secret
    :param retry: 重试, 0或false为不重试，可以设置重试次数
    :return: Response
    """
    pass
    ```
  - 如果 cookie 中包含 yht_access_token, 会读取 cookie 中 yht_access_token，否则会请求工作坊接口获取 yht_access_token

### 6.9 获取当前请求的租户信息 
算法框架支持获取当前请求租户信息， 通过 `from intelliw.utils.context.header_ctx` 模块进行调用
使用方法：
```python
from intelliw.utils.context import header_ctx

async def infer(self, infer_data):
    extra_info = {}
    cur_header_ctx = header_ctx.get() # 获取当前租户信息
    tmp_header = {}
    if cur_header_ctx:
        if 'yht_access_token' in cur_header_ctx:
            tmp_header['yht_access_token'] = cur_header_ctx['yht_access_token']
        if 'cookie' in cur_header_ctx:
            tmp_header['cookie'] = cur_header_ctx['cookie']
        if tmp_header:
            extra_info['header'] = tmp_header
    pass
```

使用说明：
  - 使用 ContextVar 来存储当前租户信息, 可以显式地读取租户信息，做后续操作

### 6.10 动态获取租户配置的向量数据库编码
算法框架支持根据 tenant_id 或者 yht_access_token 动态获取租户配置的向量数据库编码, 服务启动时创建一次

使用方法
```python
from intelliw.utils.user_router import UserRouter

# 服务启动时创建一次
user_router = UserRouter()

tenant_id = 'your_tenant_id'
yht_access_token = 'your_yht_access_token'
status, vecdb_code = user_router.get_vecdb_code(tenant_id=tenant_id, yht_access_token=yht_access_token)
# status 为 True 表示成功， vecdb_code 为向量库编码
# status 为 False 表示失败, vecdb_code 为错误信息
print(status, vecdb_code)

```

使用说明：

```python
class UserRouter:
    def __init__(
        self,
        timeout: float = 5.0, # 默认超时时间, 调用工作坊接口时，超时为5秒
        cache_size: int = 1000, # 缓存大小
        cache_ttl: int = 60  # 缓存时间，默认为60秒
    )

    def get_vecdb_code(self, tenant_id: Optional[str]=None, yht_access_token: Optional[str]=None):
        """
        获取租户路由 vecdb_code 信息
        :param tenant_id: 租户ID
        :param yht_access_token: 认证令牌
        :return: (状态, 路由向量库编码或错误信息)
        """
        pass

```
