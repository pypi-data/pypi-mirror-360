from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-tos-uploader",
    version="1.0.1",
    author="Your Name",  # 请替换为你的真实姓名
    author_email="your.email@example.com",  # 请替换为你的真实邮箱
    description="Django widget for uploading files to Volcengine TOS (Tinder Object Storage)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ren000thomas/django-tos-uploader",  # 请替换为你的真实GitHub地址
    packages=find_packages(include=["tos_uploader", "tos_uploader.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "volcengine>=1.0.0",  # 添加volcengine依赖
    ],
    include_package_data=True,
    package_data={
        "tos_uploader": [
            "static/tos_uploader/css/*.css",
            "static/tos_uploader/js/*.js",
            "templates/tos_uploader/*.html",
        ],
    },
    keywords="django, volcengine, tos, upload, widget, file-upload",
    project_urls={
        "Bug Reports": "https://github.com/ren000thomas/django-tos-uploader/issues",
        "Source": "https://github.com/ren000thomas/django-tos-uploader",
        "Documentation": "https://github.com/ren000thomas/django-tos-uploader#readme",
    },
)
