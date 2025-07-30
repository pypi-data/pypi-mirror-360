import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdklabs.ecs-codedeploy",
    "version": "0.0.418",
    "description": "CDK Constructs for performing ECS Deployments with CodeDeploy",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-ecs-codedeploy",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<aws-cdk-dev@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-ecs-codedeploy"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk.ecs_codedeploy",
        "cdk.ecs_codedeploy._jsii"
    ],
    "package_data": {
        "cdk.ecs_codedeploy._jsii": [
            "cdk-ecs-codedeploy@0.0.418.jsii.tgz"
        ],
        "cdk.ecs_codedeploy": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.139.0, <3.0.0",
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
