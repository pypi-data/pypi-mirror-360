from setuptools import find_packages, setup

setup(
    name="django-notifications-websocket",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A Django app for real-time notifications using WebSocket.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JOYBARMAN/django-notifications-websocket",
    author="JOY BARMAN",
    author_email="barmanjoy88@gmail.com",
    install_requires=[
        "channels[daphne]",
        "jsonschema",
        "channels-redis",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
