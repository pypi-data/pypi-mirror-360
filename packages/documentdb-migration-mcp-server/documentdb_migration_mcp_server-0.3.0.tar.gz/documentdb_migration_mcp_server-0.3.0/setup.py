# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

from setuptools import setup, find_namespace_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="documentdb-migration-mcp-server",
    version="0.3.0",
    description="DocumentDB Migration MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DocumentDB Team",
    author_email="documentdb-dev@example.com",
    url="https://github.com/documentdb/documentdb-tools",
    packages=find_namespace_packages(include=["awslabs.*"]),
    package_data={
        "awslabs.documentdb_migration_mcp_server": ["scripts/*.py"],
    },
    install_requires=[
        "pydantic>=2.0.0",
        "loguru>=0.6.0",
        "pymongo>=4.0.0",
        "boto3>=1.26.0",
        "mcp-server>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "documentdb-migration-mcp-server=awslabs.documentdb_migration_mcp_server.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
)
