import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "fnl-aws-cdk",
    "version": "1.0.1",
    "description": "A collection of AWS CDK Constructs designed by and for the FNL team.",
    "license": "Apache-2.0",
    "url": "https://github.com/colemandevries/fnl-aws-cdk.git",
    "long_description_content_type": "text/markdown",
    "author": "Cole DeVries<devriesca@nih.gov>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/colemandevries/fnl-aws-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "fnl_aws_cdk",
        "fnl_aws_cdk._jsii"
    ],
    "package_data": {
        "fnl_aws_cdk._jsii": [
            "fnl-aws-cdk@1.0.1.jsii.tgz"
        ],
        "fnl_aws_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.203.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
