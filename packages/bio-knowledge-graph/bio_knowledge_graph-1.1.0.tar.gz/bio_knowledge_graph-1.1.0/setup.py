from setuptools import setup, find_packages

setup(
    name="bio_knowledge_graph",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers>=4.0.0",  # 指定最低版本为 4.0.0
    ],
    author="DT.L",
    description="A Chinese relation extraction data utility toolkit based on CasRel model",
    long_description=open("README.md", encoding='utf-8').read(),  # 显式指定 UTF-8 编码,
    long_description_content_type="text/markdown",
    url="https://github.com/yuyanhong/bio_knowledge_graph",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)