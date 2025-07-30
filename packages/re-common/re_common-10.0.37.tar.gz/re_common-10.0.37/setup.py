import setuptools

# test.pypi
# updatepypi
# [pypi]
# username = __token__
# password = pypi - AgENdGVzdC5weXBpLm9yZwIkZDU5NzdkOWUtN2NmNy00MDhjLWI3ZmMtOWY1NmQxOTRiMTU0AAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiCmmvSirLVoekGxZAQ4e5EMSnF7vrkdqYrOdEC1PXaaPg

# python3 setup.py sdist bdist_wheel
# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

"""
# 打包教程
https://packaging.python.org/tutorials/packaging-projects/
 
pypi
re_common 
[pypi]
  username = __token__
  # 失效
  password = pypi-AgEIcHlwaS5vcmcCJDdlYTBjNzZjLTU2NDItNGExYy04NzY4LWIxM2IyMzgzZjFiYgACJXsicGVybWlzc2lvbnMiOiAidXNlciIsICJ2ZXJzaW9uIjogMX0AAAYgPjmPag7MzYc7m6hG5x5-RGYtOolOXPWtTb88iMdB3xE
  # 请使用新的令牌
  password_new = pypi-AgEIcHlwaS5vcmcCJGU4NzNiN2QyLWY3NDgtNGVhZC04YTM1LThhZDNlZThlY2E1NgACEVsxLFsicmUtY29tbW9uIl1dAAIsWzIsWyIwYWIzYjIzMy0zZTlmLTQ1ZjAtYWQ5OC03NjJhNDM5NjNiZmUiXV0AAAYgGvyJ9zFd7e-sy4JMScCo23eNGqKFLWIIZMSiKqDkV0g
  # new 20250224
  password_new = pypi-AgEIcHlwaS5vcmcCJDJkMzJhNWZkLTBkOTktNGE4Yi1iN2Q5LWU0ZjNjMGNiNzhjYwACEVsxLFsicmUtY29tbW9uIl1dAAIsWzIsWyIwYWIzYjIzMy0zZTlmLTQ1ZjAtYWQ5OC03NjJhNDM5NjNiZmUiXV0AAAYg0Pu6BqqupvhX7ad69d8e6XS8BmnLav6x6D9HJ-U3gko
  
 pypi-AgEIcHlwaS5vcmcCJDBlMzc1OTU1LWVkOGItNDVjZS1iMGNhLTQwYmNmYmU3NmViMwACEVsxLFsicmUtY29tbW9uIl1dAAIsWzIsWyIwYWIzYjIzMy0zZTlmLTQ1ZjAtYWQ5OC03NjJhNDM5NjNiZmUiXV0AAAYgisva56cDT5J3a9EBb3paplusibupSRSfoZc_L8PUGDY
python setup.py sdist bdist_wheel
python -m twine upload dist/*

"""
long_description = """
    这是一个基础类，依赖很多的第三方包，是一个用得到的第三方库的封装，可以在此基础上迅速构建项目
"""
setuptools.setup(
    name="re_common",
    version="10.0.37",
    author="vic",
    author_email="xujiang5@163.com",
    description="a library about all python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/xujiangios/re-common",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
