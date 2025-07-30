from setuptools import setup, find_packages
setup(
    name="FreeKnowledge_AI",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'beautifulsoup4>=4.9.3',
        'jieba>=0.42.1',
        'matplotlib>=3.3.4'
    ],
    author="wuyuhang11",
    author_email="m325124620@sues.edu.cn",
    description="An Agent for obtaining external knowledge for free.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VovyH/FreeKnowledge_AI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    license="MIT",  # 添加license字段
    license_files = ("LICENSE",),  # 添加license_files字段
)