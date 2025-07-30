from setuptools import setup, find_packages

setup(
    name="an_envmanager",  # パッケージ名
    version="1.3.2",  # バージョン
    description="An initializer package for Google Colab projects",  # 説明
    author="Atsushi888",  # 作者名
    author_email="vtgrotxu@gmail.com",  # メールアドレス
    url="https://github.com/Atsushi888/Atsushi888",  # GitHubやWebサイトのURL
    packages=find_packages(),  # 自動でパッケージを検出
    install_requires=[],  # 必要な外部ライブラリ(必要なら記述)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 対応するPythonのバージョン
)
