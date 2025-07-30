from setuptools import setup, find_packages

setup(
    name="sctfbridge",
    version="0.1.0",
    packages=find_packages(where="src"),
    description='sctfbridge ',
    author='Feng-ao Wang',
    package_dir={"": "src"},
    install_requires=[
        # 依赖列表
    ],
)
