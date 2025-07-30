import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-dev-cloud-constructs",
    "version": "0.0.9",
    "description": "CDK Construct Library to create an open source developer platform at AWS",
    "license": "MIT",
    "url": "https://github.com/cloudbauer/cdk-dev-cloud-constructs",
    "long_description_content_type": "text/markdown",
    "author": "bitbauer<4582513+bitbauer@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cloudbauer/cdk-dev-cloud-constructs"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_dev_cloud_constructs",
        "cdk_dev_cloud_constructs._jsii"
    ],
    "package_data": {
        "cdk_dev_cloud_constructs._jsii": [
            "cdk-dev-cloud-constructs@0.0.9.jsii.tgz"
        ],
        "cdk_dev_cloud_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.173.4, <3.0.0",
        "cdk-nag>=2.36.33, <3.0.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
