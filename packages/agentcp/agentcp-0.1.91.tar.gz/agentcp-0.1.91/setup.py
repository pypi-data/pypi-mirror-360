from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentcp",
    packages=find_packages(where="."),
    package_dir={"": "."},
    version="0.1.91",
    description="""	ACP是一个开放协议,用于解决Agent互相通信协作的问题
	                ACP定义了agent的数据规范、agent之间的通信以及agent之间的授权规范

                    AagentCP Python SDK
	                    AgentCP Python SDK是一个基于ACP协议的Agent标准通信库，用于解决Agent间的身份认证及通信。
	                    AgentCP Python SDK提供了一系列API，用于创建Agent ID、连接入网、构建群组，收发消息等。
	                    AgentCP Python SDK支持多Agent协作，异步消息处理，支持内网穿透，支持Agent访问的负载均衡
     """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liwenjiang",
    author_email="19169495461@163.com",
    url="https://github.com/auliwenjiang/agentcp",
    package_data={
    },
    include_package_data=True,
    install_requires=[
        "cryptography>=3.4.7",  # 示例依赖项
        "requests>=2.26.0",     # 示例依赖项
        "websocket-client>=1.2.1",     # 示例依赖项
        "python-dotenv>=0.19.0",     # 示例依赖项
        "asyncio>=3.4.3",     # 示例依赖项
        "typing-extensions>=4.0.1",     # 示例依赖项
        "openai>=1.68.2",     # 示例依赖项
        "flask>=3.0.1",     # 示例依赖项
        "flask[async]>=1.0.1", 
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    keywords="Agent Communication Protocol",
    project_urls={
        "Bug Reports": "https://github.com/auliwenjiang/agentcp/issues",
        "Source": "https://github.com/auliwenjiang/agentcp",
    },
)