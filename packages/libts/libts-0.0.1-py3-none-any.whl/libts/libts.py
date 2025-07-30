import os
import sys
import ctypes
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from importlib.resources import files, as_file

class ReturnCode(IntEnum):
    GENERAL_SUCCESS = 0
    VERIFICATION_OK = 1
    VERIFICATION_FAIL = 2
    INVALID_PARAM = 3
    OPENSSL_ERROR = 4

LIBTS_CTX = ctypes.c_void_p

if (lib_name := {"win32": "libts.dll", "linux": "libts.so"}.get(sys.platform)):
    with as_file(files("libts") / lib_name) as lib_path:
        _libts = ctypes.CDLL(str(Path(lib_path).absolute()))
else:
    raise RuntimeError("不支持的系统")

'''
if sys.platform.startswith("win"):
    _libts = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "libts.dll"))
elif sys.platform.startswith("linux"):
    _libts = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "libts.so"))
else:
    raise RuntimeError("不支持的系统")
'''

_libts.init_ctx.restype = LIBTS_CTX

_libts.free_ctx.argtypes = [LIBTS_CTX]
_libts.free_ctx.restype = None

_libts.add_cert_file.argtypes = [LIBTS_CTX, ctypes.c_char_p]
_libts.add_cert_file.restype = ctypes.c_int

_libts.add_cert_dir.argtypes = [LIBTS_CTX, ctypes.c_char_p]
_libts.add_cert_dir.restype = ctypes.c_int

_libts.add_cert_store.argtypes = [LIBTS_CTX, ctypes.c_char_p]
_libts.add_cert_store.restype = ctypes.c_int

_libts.load_system_ca.argtypes = [LIBTS_CTX]
_libts.load_system_ca.restype = ctypes.c_int

_libts.get_last_openssl_error.argtypes = [LIBTS_CTX]
_libts.get_last_openssl_error.restype = ctypes.c_char_p

_libts.get_last_gentime_utc.argtypes = [LIBTS_CTX]
_libts.get_last_gentime_utc.restype = ctypes.c_time_t
_libts.get_last_gentime_bj.argtypes = [LIBTS_CTX]
_libts.get_last_gentime_bj.restype = ctypes.c_time_t

_libts.ts_verify.argtypes = [LIBTS_CTX, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
_libts.ts_verify.restype = ctypes.c_int

_libts.ts_verify_noctx.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_libts.ts_verify_noctx.restype = ctypes.c_int

# 不创建ctx快速验证，使用系统CA，仅验证，无法获取错误信息和时间戳
def ts_verify_noctx(data_file: str, sign_file: str) -> ReturnCode:
    return ReturnCode(_libts.ts_verify_noctx(data_file.encode("utf-8"), sign_file.encode("utf-8")))

# 时间戳格式化，简化的ISO-8601表示法
def format_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# 每个线程之间使用独立的ctx避免出现竞态问题
class libts_ctx:
    def __init__(self):
        self.inited = False
        self.init_ctx()

    def __del__(self):
        if self.inited:
            _libts.free_ctx(self.ctx)

    def init_ctx(self) -> None:
        if not self.inited:
            self.ctx = _libts.init_ctx()
            if not self.ctx:
                raise RuntimeError("无法创建ctx，这不应该发生")
            self.inited = True

    def add_cert_file(self, file: str) -> ReturnCode:
        self.init_ctx()
        return ReturnCode(_libts.add_cert_file(self.ctx, file.encode("utf-8")))
    
    def add_cert_dir(self, dir: str) -> ReturnCode:
        self.init_ctx()
        return ReturnCode(_libts.add_cert_dir(self.ctx, dir.encode("utf-8")))
    
    def add_cert_store(self, store: str) -> ReturnCode:
        self.init_ctx()
        return ReturnCode(_libts.add_cert_store(self.ctx, store.encode("utf-8")))
    
    def load_system_ca(self) -> ReturnCode:
        self.init_ctx()
        return ReturnCode(_libts.load_system_ca(self.ctx))
    
    def ts_verify(self, data_file: str, sign_file: str, parse_response: bool = True) -> ReturnCode:
        self.init_ctx()
        return ReturnCode(_libts.ts_verify(self.ctx, data_file.encode("utf-8"), sign_file.encode("utf-8"), parse_response))
    
    # 获取最近openssl的错误信息，ReturnCode为OPENSSL_ERROR时调用
    def get_last_openssl_error(self) -> str:
        self.init_ctx()
        err_ptr = _libts.get_last_openssl_error(self.ctx)
        return err_ptr.decode("utf-8") if err_ptr else ""
    
    # 返回值格式化
    def format_return_code(self, code: ReturnCode) -> str:
        if code == code.GENERAL_SUCCESS:
            return "操作成功完成"
        if code == code.VERIFICATION_OK:
            return "验证成功"
        if code == code.VERIFICATION_FAIL:
            return f"验证失败 {self.get_last_openssl_error()}"
        if code == code.INVALID_PARAM:
            return "参数错误"
        if code == code.OPENSSL_ERROR:
            return f"openssl内部错误 {self.get_last_openssl_error()}"
    
    # 秒级UTC时间戳
    def get_last_gentime_utc(self) -> int:
        self.init_ctx()
        return int(_libts.get_last_gentime_utc(self.ctx))
    
    def get_last_gentime_utc_formatted(self) -> str:
        return format_timestamp(self.get_last_gentime_utc())

    # 秒级北京时间时间戳（东八区）
    def get_last_gentime_bj(self) -> int:
        self.init_ctx()
        return int(_libts.get_last_gentime_bj(self.ctx))
    
    def get_last_gentime_bj_formatted(self) -> str:
        return format_timestamp(self.get_last_gentime_bj())
