import sys
import ctypes
from ctypes import *

DEFAULT_CFG_FILE = "/etc/fw_env.config"
DEFAULT_ENV_FILE = "/etc/u-boot-initial-env"

class UBootCtx(Structure): pass

# struct uboot_ctx *ctx
UBootCtxPtr = POINTER(UBootCtx)

class UBootEnv():
    """
    libuenv context class.
    """

    clib = CDLL("libubootenv.so")

    # int libuboot_read_config_ext(struct uboot_ctx **ctx, const char *config)
    clib.libuboot_read_config_ext.argstypes = (UBootCtxPtr, c_char_p)

    # const char *libuboot_namespace_from_dt(void)
    clib.libuboot_namespace_from_dt.restype = c_char_p

    # struct uboot_ctx *libuboot_get_namespace(struct uboot_ctx *ctxlist, const char *name)
    clib.libuboot_get_namespace.argstypes = (UBootCtxPtr, c_char_p)
    clib.libuboot_get_namespace.restype = UBootCtxPtr

    # int libuboot_open(struct uboot_ctx *ctx)
    clib.libuboot_open.argstypes = UBootCtxPtr

    # int libuboot_load_file(struct uboot_ctx *ctx, const char *filename)
    clib.libuboot_load_file.argstypes = (UBootCtxPtr, c_char_p)

    # char *libuboot_get_env(struct uboot_ctx *ctx, const char *varname)
    clib.libuboot_get_env.argstypes = (UBootCtxPtr, c_char_p)
    clib.libuboot_get_env.restype = c_char_p

    # int libuboot_set_env(struct uboot_ctx *ctx, const char *varname, const char *value)
    clib.libuboot_set_env.argstypes = (UBootCtxPtr, c_char_p, c_char_p)

    # int libuboot_env_store(struct uboot_ctx *ctx)
    clib.libuboot_env_store.argstypes = UBootCtxPtr

    # void libuboot_close(struct uboot_ctx *ctx)
    clib.libuboot_close.argstypes = UBootCtxPtr
    clib.libuboot_close.restype = c_void_p

    # void libuboot_exit(struct uboot_ctx *ctx)
    clib.libuboot_exit.argstypes = UBootCtxPtr
    clib.libuboot_exit.restype = c_void_p

    def __init__(self, cfg_path=DEFAULT_CFG_FILE, default_env_path=DEFAULT_ENV_FILE, namespace=None):
        self.uboot_ctx_p = UBootCtxPtr()

        cfg = create_string_buffer(str.encode(cfg_path))
        if self.clib.libuboot_read_config_ext(byref(self.uboot_ctx_p), cfg) != 0:
            print("Cannot initialize environment", file=sys.stderr)
            exit(1)

        if namespace is None:
            namespace = self.clib.libuboot_namespace_from_dt()
        
        if namespace:
            self.uboot_ctx_p = self.clib.libuboot_get_namespace(self.uboot_ctx_p, namespace)

        if self.uboot_ctx_p is None:
            print("Namespace %s not found" % namespace, file=sys.stderr)
            exit(1)

        if self.clib.libuboot_open(self.uboot_ctx_p) < 0:
            print("Cannot read environment, using default", file=sys.stderr)
            ret = self.clib.libuboot_load_file(self.uboot_ctx_p, default_env_path)
            if ret < 0:
                print("Cannot read default environment from file", file=sys.stderr)
                exit(ret)

    def __del__(self):
        self.clib.libuboot_close(self.uboot_ctx_p)
        self.clib.libuboot_exit(self.uboot_ctx_p)

    def store(self):
        self.clib.libuboot_env_store(self.uboot_ctx_p)

    def shadow(self, variable, value=None):
        if value is None and self.get_env(variable) is None:
            print("debug: value already empty, skip")
            return False
        
        if value is not None and str.encode(value) == self.get_env(variable):
            print("debug: same value, skip")
            return False

        variable = create_string_buffer(str.encode(variable))
        if value is not None:
            value = create_string_buffer(str.encode(value))
        ret = self.clib.libuboot_set_env(self.uboot_ctx_p, variable, value)
        if ret:
            print("libuboot_set_env failed: %d" % ret, file=sys.stderr)
            exit(-ret)
        
        return True

    def set(self, variable, value=None):
        if self.shadow(variable, value):
            self.store()

    def get(self, variable):
        variable = create_string_buffer(str.encode(variable))
        value = self.clib.libuboot_get_env(self.uboot_ctx_p, variable)
        return value
