# APISpecToolkit


- Can't use Optional, adding default value instead, since Optional would generate type: "null" in the openapi which is not supported.

- Before submitting the changes, please generate it first locally and test the openapi in [online swagger editor](https://editor.swagger.io/)



# Publish Package

```bash
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
python -m twine upload dist/*

rm -rf dist build
```
