import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "merapar.waf-http-api",
    "version": "1.0.1",
    "description": "A CDK construct that fronts an HTTP API with a CloudFront distribution and protects it with AWS WAF.",
    "license": "MIT",
    "url": "https://github.com/JaapHaitsma/waf-http-api.git",
    "long_description_content_type": "text/markdown",
    "author": "Jaap Haitsma<jaap@haitsma.org>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/JaapHaitsma/waf-http-api.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "merapar_waf_http_api",
        "merapar_waf_http_api._jsii"
    ],
    "package_data": {
        "merapar_waf_http_api._jsii": [
            "waf-http-api@1.0.1.jsii.tgz"
        ],
        "merapar_waf_http_api": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.200.0, <3.0.0",
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
