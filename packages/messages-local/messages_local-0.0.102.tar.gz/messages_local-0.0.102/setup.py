import setuptools

PACKAGE_NAME = "messages-local"

package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.102',  # https://pypi.org/project/messages-local
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="messages-local",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "item-local>=0.0.9",
        "queue-worker-local>=0.0.37",
        "label-message-local>=0.0.4",
        "message-local>=0.0.150",
        "whatsapp-message-vonage-local>=0.0.19",
        "whataspp-message-inforu-local>=0.0.12",
        "sms-message-aws-sns-local>=0.0.35",
        "email-message-aws-ses-local>=0.0.13",
        "facebook-message-selenium-local"
    ]
)
