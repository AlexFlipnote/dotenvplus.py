# DotEnvPlus
Reads key-value pairs from a .env file and supports multiple values with dynamic interpolation.

The values returned by the DotEnv object is treated like a dictionary, so you can use it like a normal dictionary.
Some of the usual dictionary methods are also supported like `.items()`, `.keys()`, `.values()`, etc.

Goal is to make it easy to use environment variables in your code, while also supporting multiple values.

## Installing
> You need **Python >=3.7** to use this library.

```bash
pip install dotenvplus
```

## Usage
```env
# .env
KEY1=value
KEY2=123
KEY3=true
```

```python
# main.py
from dotenvplus import DotEnv

# Create a DotEnv object
env = DotEnv()
>>> <DotEnv data={"KEY1": "value", "KEY2": 123, "KEY3": True}>

# Call it like a dictionary
(env["KEY1"], env["KEY2"], env["KEY3"])
>>> ("value", 123, True)
```
