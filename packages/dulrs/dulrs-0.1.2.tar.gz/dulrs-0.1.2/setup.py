from setuptools import setup, find_packages

setup(
    name="dulrs",  # 包名称
    version="0.1.2",  # 版本号
    author="Fengyi_Wu",
    author_email="wufengyi98@163.com",
    description="A Python package to generate heatmaps, lowrank, and sparsity from deep learning models.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fengyiwu98",  # 你的 GitHub 主页
    packages=find_packages(include=["dulrs", "dulrs.*"]),  # 确保包含所有子模块
    include_package_data=True,  # 关键：确保额外的文件（如 __init__.py）被打包
    install_requires=[
        "torch",
        "torchvision",
        "numpy",
        "scipy",
        "opencv-python",
        "matplotlib",
        "pandas",
        "plotnine",
        "Pillow",
        "statistics",
        "torchvision"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)


from setuptools import setup, find_packages

