import os

filePath = os.path.abspath("token.json")
print(filePath)

os.remove(filePath)