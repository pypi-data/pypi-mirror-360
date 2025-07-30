# libts

一个用于验证 RFC3161 时间戳签名的库

## example

```python
from libts import libts_ctx

ctx = libts_ctx()
ctx.load_system_ca()
code = ctx.ts_verify("example.txt", "example.txt.tsr")
print(ctx.format_return_code(code))
print(ctx.get_last_gentime_utc_formatted())
print(ctx.get_last_gentime_bj_formatted())
```
