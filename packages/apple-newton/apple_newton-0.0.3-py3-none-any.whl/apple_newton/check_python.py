import os
import sys

print("Hello, Python")
# OS名称
print(os.name)
# OS情報
print(sys.platform)
# Pythonバージョン
print(sys.version)
# .venvのPATH
print(sys.prefix)
# 実行中のPythonのPATH
print(sys.executable)
# venvのもとになっているPythonのPATH
print(sys.base_prefix)
