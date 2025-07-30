
import uuid
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor
import threading
import atexit
import time
import sys

    # 定义必填字段列表
REQUIRED_FIELDS = ['traceId', 'apiCode', 'resultCode', 'startTime', 'ytenantId', 'domain']

    # 定义字段格式校验规则
VALID_FORMAT_FIELDS = {
        "requestHeader": Optional,  # 可为 None 或字符串
        "requestBody": Optional,    # 可为 None 或字符串
        "responseBody": Optional,   # 可为 None 或字符串
    }

class TraceLog:
    _executor = None
    _lock = threading.Lock()
    
    @classmethod
    def _get_executor(cls):
        if cls._executor is None:
            with cls._lock:
                if cls._executor is None:
                    cls._executor = ThreadPoolExecutor(
                        max_workers=2,
                        thread_name_prefix="TraceLog_"
                        )
                    atexit.register(cls._shutdown_executor)
        return cls._executor

    

    @classmethod
    def _shutdown_executor(cls):
        """安全关闭线程池"""
        if cls._executor:
            cls._executor.shutdown(wait=True)
            cls._executor = None
    def __init__(self):
        # 基础跟踪信息
        self.id: Optional[str] = str(uuid.uuid4())
        self.traceId: Optional[str] = None  # 必填
        self.spanId: Optional[str] = None
        self.pSpanId: Optional[str] = None  # 必填
        
        # 请求/响应信息
        self.queryMsg: Optional[str] = None
        self.apiCode: Optional[str] = None  # 必填
        self.apiUrl: Optional[str] = None
        self.resultCode: Optional[int] = None  # 必填
        self.requestHeader: Optional[str] = None
        self.requestBody: Optional[str] = None
        self.responseBody: Optional[str] = None
        
        # 时间信息
        self.startTime: Optional[int] = int(time.time() * 1000)  # 必填，时间戳（毫秒）
        self.endTime: Optional[int] = None    # 时间戳（毫秒）
        self.timeCost: Optional[int] = None   # 耗时（毫秒）
        
        # 监控与业务信息
        self.entranceFlag: Optional[int] = 0  # 入口标志 (0/1)
        self.warnThreshold: Optional[int] = None  # 告警阈值（毫秒）
        self.domain: Optional[str] = 'iuap-aip-alg'  # 必填
        self.businessKey: Optional[str] = None
        self.businessType: Optional[str] = None
        self.businessData: Dict[str, str] = {}  # 并发安全的字典
        
        # 租户与创建信息
        self.ytenantId: Optional[str] = None  # 必填
        self.creatorId: Optional[str] = None
        self.creator: Optional[str] = None
        self.createTime: Optional[int] = int(time.time() * 1000)   # 创建时间戳（毫秒）
        self.ts: Optional[int] = None          # 时间戳（毫秒）

    def validate_required_fields(self) -> None:
        """验证必填字段是否已赋值"""
        missing_fields = []
        for field in REQUIRED_FIELDS:
            value = getattr(self, field)
            # 检查字段是否为None或空字符串
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必填字段: {', '.join(missing_fields)}")
    def validate_field_formats(self) -> None:
        """验证字段格式是否符合要求"""
        format_errors = []
        
        for field, expected_format in VALID_FORMAT_FIELDS.items():
            value = getattr(self, field)
            
            # 检查字段格式
            if expected_format is Optional:
                # 检查是否为字符串或None
                if value is not None and not isinstance(value, str):
                    format_errors.append(
                        f"字段 '{field}' 格式错误: 应为字符串或None, 实际类型 {type(value).__name__}"
                    )
        
        if format_errors:
            raise TypeError("\n".join(format_errors))
        
    def full_validation(self) -> None:
        """执行完整的字段验证（必填字段 + 格式校验）"""
        self.validate_required_fields()
        self.validate_field_formats()
        self.validate_val_length()

    def validate_val_length(self):
        if self.requestBody and sys.getsizeof(self.requestBody) >= 1024 * 1024 * 1:
            self.requestBody = "RequestBody too long, Not Logged!!!"

        if self.responseBody and sys.getsizeof(self.responseBody) >= 1024 * 1024 * 1:
            self.responseBody  = "ResponseBody too long, Not Logged!!!"

    def calculate_time_cost(self) -> None:
        """自动计算请求耗时（需先设置 startTime 和 endTime）"""
        if self.startTime and self.endTime:
            self.timeCost = self.endTime - self.startTime

    def add_business_data(self, key: str, value: str) -> None:
        """线程安全地添加业务扩展数据"""
        self.businessData[key] = value

    def to_dict(self) -> Dict:
        """将对象转换为字典（包含必填字段验证）"""
        self.full_validation()
        return {attr: getattr(self, attr) for attr in dir(self) 
                if not callable(getattr(self, attr)) and not attr.startswith("_")}
