import setuptools

PACKAGE_NAME = "message-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.186',  # https://pypi.org/project/message-local
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description=PACKAGE_NAME,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["item-local>=0.0.9",
                      "api-management-local>=0.0.73",
                      "language-remote>=0.0.20",
                      "variable-local>=0.0.95",
                      "logger-local>=0.0.135",
                      "database-mysql-local>=0.1.6",
                      "star-local>=0.0.16",
                      "profile-local>=0.0.65",
                      "phones-local>=0.0.18",
                      "criteria-local",
                      "user-external-local"
                      ]
)
