import setuptools

PACKAGE_NAME = "storage-remote-graphql"  # storage-remote-graphql as we might also have storage-remote-restapi
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/storage-remote-graphql
    version='0.0.16',
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="This is a package for sharing common methods of storage remote used in different repositories",  # noqa: E501
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.32.4",  # >=2.31.0, latest version is 2.32.4
        "python-sdk-remote>=0.0.93",
        "url-remote>=0.0.28"
    ]
)
