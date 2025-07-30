# UBootEnv package
This package offers a Python implementation of the well-known `fw_setenv` and `fw_getenv` commands, based on the C library *libubootenv*.

## Features
- Read and modify variables in the U-Boot environment
- Erase variable values
- Shadow writing to minimize write cycles

## Usage
```python
from ubootenv import UBootEnv

uenv = UBootEnv()
# Or specify a custom config path
uenv = UBootEnv("/etc/fw_env.config")

var = uenv.get("foo")
print(var) # => None

uenv.set("foo", "bar")
var = uenv.get("foo")
print(var) # => b'bar'

# Use shadow writing, get method returns the shadow value
uenv.shadow("foo", "foo")
var = uenv.get("foo")
print(var) # => b'foo'

# Commit shadow values to disk
uenv.store()

```


