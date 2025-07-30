import os
import sys
import numpy as np
from typing import Optional, Union, List, Dict, Any
from enum import Enum

def find_qairt_sdk():
    """查找QAIRT SDK路径"""
    # 检查环境变量
    qnn_sdk_root = os.environ.get("QNN_SDK_ROOT")
    snpe_root = os.environ.get("SNPE_ROOT")
    
    # 如果环境变量已设置，使用它们
    if qnn_sdk_root and os.path.exists(qnn_sdk_root):
        qairt_python_path = os.path.join(qnn_sdk_root, "lib", "python")
        if os.path.exists(os.path.join(qairt_python_path, "qairt")):
            return qairt_python_path
    
    if snpe_root and os.path.exists(snpe_root):
        qairt_python_path = os.path.join(snpe_root, "lib", "python")
        if os.path.exists(os.path.join(qairt_python_path, "qairt")):
            return qairt_python_path
    
    # 默认路径尝试
    default_path = "/home/linbaichuan/qcom/qairt/2.35.0.250530/lib/python"
    if os.path.exists(os.path.join(default_path, "qairt")):
        return default_path
    
    return None

def init_qairt(sdk_path=None):
    """初始化QAIRT SDK
    
    参数:
        sdk_path: 可选，手动指定SDK路径。如果为None，将尝试从环境变量自动检测。
        
    返回:
        bool: 初始化成功返回True
        
    异常:
        ImportError: 如果找不到SDK或导入失败
    """
    if sdk_path:
        qairt_path = sdk_path
    else:
        qairt_path = find_qairt_sdk()
    
    if not qairt_path:
        raise ImportError(
            "找不到QAIRT SDK。请确保已设置QNN_SDK_ROOT或SNPE_ROOT环境变量，"
            "或使用init_qairt(sdk_path)手动指定SDK路径。"
            "\n提示：您可以运行SDK包中的envsetup.sh脚本来设置环境变量。"
        )
    
    if qairt_path not in sys.path:
        sys.path.append(qairt_path)
    
    try:
        global qairt
        global BackendType
        global Device
        import qairt
        from qairt.api.configs import BackendType, Device
        return True
    except ImportError as e:
        raise ImportError(f"导入QAIRT SDK失败: {e}")

# 类定义
class DataType(Enum):
    TYPE_FLOAT32 = "float32"
    TYPE_UINT8 = "uint8"
    TYPE_INT8 = "int8"
    TYPE_INT32 = "int32"

class FrameworkType(Enum):
    TYPE_QNN = "QNN"
    TYPE_SNPE2 = "SNPE2"

class AccelerateType(Enum):
    TYPE_DSP = "HTP"
    TYPE_CPU = "CPU"
    TYPE_GPU = "GPU"

class ImplementType(Enum):
    TYPE_LOCAL = "LOCAL"

class Model:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.qairt_model = None
        self.input_shapes = None
        self.output_shapes = None
        self.input_dtype = None
        self.output_dtype = None
        
    @classmethod
    def create_instance(cls, model_path: str):
        return cls(model_path)
    
    def set_model_properties(self, input_shapes: List[List[int]], input_dtype: DataType,
                           output_shapes: List[List[int]], output_dtype: DataType):
        self.input_shapes = input_shapes
        self.output_shapes = output_shapes
        self.input_dtype = input_dtype
        self.output_dtype = output_dtype

class Config:
    def __init__(self):
        self.implement_type = ImplementType.TYPE_LOCAL
        self.framework_type = FrameworkType.TYPE_QNN
        self.accelerate_type = AccelerateType.TYPE_DSP
        self.number_of_threads = 4
        self.is_quantify_model = 0
        
    @classmethod
    def create_instance(cls):
        return cls()

class Interpreter:
    def __init__(self, model: Model, config: Config):
        self.model = model
        self.config = config
        self.qairt_model = None
        self.is_initialized = False
        self.is_loaded = False
        
    def init(self) -> int:
        try:
            self.qairt_model = qairt.Model.load(self.model.model_path)
            self.is_initialized = True
            return 0
        except Exception as e:
            print(f"Failed to initialize model: {e}")
            return -1
    
    def load_model(self) -> int:
        try:
            if not self.is_initialized:
                return -1
            
            # 设置后端类型
            if self.config.framework_type == FrameworkType.TYPE_QNN:
                if self.config.accelerate_type == AccelerateType.TYPE_DSP:
                    backend = BackendType.HTP
                elif self.config.accelerate_type == AccelerateType.TYPE_CPU:
                    backend = BackendType.CPU
                elif self.config.accelerate_type == AccelerateType.TYPE_GPU:
                    backend = BackendType.GPU
                else:
                    backend = BackendType.CPU
            else:
                backend = BackendType.CPU
            
            # 初始化模型
            self.qairt_model.initialize(backend=backend)
            self.is_loaded = True
            return 0
        except Exception as e:
            print(f"Failed to load model: {e}")
            return -1
    
    def set_input_tensor(self, index: int, data: np.ndarray) -> int:
        try:
            if not self.is_loaded:
                return -1
            
            # 存储输入数据
            if not hasattr(self, 'input_data'):
                self.input_data = {}
            self.input_data[index] = data
            return 0
        except Exception as e:
            print(f"Failed to set input tensor: {e}")
            return -1
    
    def invoke(self) -> int:
        try:
            if not self.is_loaded or not hasattr(self, 'input_data'):
                return -1
            
            # 设置后端类型
            if self.config.framework_type == FrameworkType.TYPE_QNN:
                if self.config.accelerate_type == AccelerateType.TYPE_DSP:
                    backend = BackendType.HTP
                elif self.config.accelerate_type == AccelerateType.TYPE_CPU:
                    backend = BackendType.CPU
                elif self.config.accelerate_type == AccelerateType.TYPE_GPU:
                    backend = BackendType.GPU
                else:
                    backend = BackendType.CPU
            else:
                backend = BackendType.CPU
            
            # 执行推理
            inputs = self.input_data[0]  # 假设单输入
            result = self.qairt_model(inputs, backend=backend)
            
            # 存储输出结果
            if not hasattr(self, 'output_data'):
                self.output_data = {}
            
            # 根据QAIRT 2.35.0.250530 SDK的ExecutionResult结构处理结果
            # 在QAIRT 2.35中，ExecutionResult.data是一个字典，键是输出张量名，值是numpy数组
            if hasattr(result, 'data') and result.data is not None:
                # 如果是字典类型，获取第一个输出
                if isinstance(result.data, dict):
                    # 获取第一个输出张量的值
                    first_output_name = next(iter(result.data))
                    self.output_data[0] = result.data[first_output_name]
                # 如果是序列类型，获取第一个字典的第一个输出
                elif isinstance(result.data, (list, tuple)) and len(result.data) > 0:
                    first_dict = result.data[0]
                    if isinstance(first_dict, dict) and len(first_dict) > 0:
                        first_output_name = next(iter(first_dict))
                        self.output_data[0] = first_dict[first_output_name]
            else:
                # 如果result本身就是输出张量，直接使用
                self.output_data[0] = result
            
            return 0
        except Exception as e:
            print(f"Failed to invoke model: {e}")
            return -1
    
    def get_output_tensor(self, index: int) -> Optional[np.ndarray]:
        try:
            if not hasattr(self, 'output_data') or index not in self.output_data:
                return None
            return self.output_data[index]
        except Exception as e:
            print(f"Failed to get output tensor: {e}")
            return None
    
    def destory(self) -> int:
        try:
            if self.qairt_model:
                self.qairt_model.destroy()
            self.is_initialized = False
            self.is_loaded = False
            return 0
        except Exception as e:
            print(f"Failed to destroy interpreter: {e}")
            return -1

class InterpreterBuilder:
    @staticmethod
    def build_interpretper_from_model_and_config(model: Model, config: Config) -> Optional[Interpreter]:
        try:
            return Interpreter(model, config)
        except Exception as e:
            print(f"Failed to build interpreter: {e}")
            return None