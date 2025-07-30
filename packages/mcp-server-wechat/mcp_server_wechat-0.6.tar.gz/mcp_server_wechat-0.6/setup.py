from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mcp_server_wechat',
    version='0.6',
    license='MIT',
    description='基于MCP技术的微信聊天记录获取和消息发送功能的服务器',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='panxingfeng',
    author_email='1115005803@qq.com',
    url='https://github.com/panxingfeng/mcp_server_wechat',
    download_url='https://github.com/panxingfeng/mcp_server_wechat/archive/refs/tags/0.4.tar.gz',
    
    packages=find_packages(),
    keywords=['wechat', 'mcp', 'chat', 'automation'],
    
    install_requires=[
        'pywechat127>=1.8.8',
        'mcp==1.9.1',
        'pywinauto==0.6.9',
        'PyAutoGUI==0.9.54',
    ],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.11',
        'Natural Language :: Chinese (Simplified)',
    ]
)