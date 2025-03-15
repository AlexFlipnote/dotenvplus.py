from dotenvplus import DotEnv

env = DotEnv(".env.example")

print(env)
print(env["STRING_VALUE"])
print(env["VAR_VALUE"])

print("STRING_VALUE" in env)

for k, v in env.items():
    print(f"{k}: {v} (type: {type(v)})")
