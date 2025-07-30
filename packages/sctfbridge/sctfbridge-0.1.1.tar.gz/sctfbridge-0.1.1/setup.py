from setuptools import setup, find_packages

setup(
    name="sctfbridge",
    version="0.1.1",
    packages=find_packages(where="src"),
    description='sctfbridge ',
    author='Feng-ao Wang',
    package_dir={"": "src"},
    install_requires=[
        'torch~=2.6.0',
        'numpy~=2.2.5',
        'scanpy~=1.11.1',
        'episcanpy~=0.4.0',
        'pandas~=2.3.0',
        'pybedtools~=0.12.0',
        'anndata~=0.11.4',
        'tqdm~=4.67.1',
        'setuptools~=75.8.0',
        'scipy~=1.15.2',
    ],
    python_requires='>=3.8', # 建议添加对Python版本的限制
)
