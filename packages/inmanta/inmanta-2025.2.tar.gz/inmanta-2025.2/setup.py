from setuptools import setup


setup(
    version="2025.2",
    python_requires=">=3.12",  # also update classifiers
    # Meta data
    name="inmanta",
    description="Inmanta deployment tool",
    author="Inmanta",
    author_email="code@inmanta.com",
    url="https://github.com/inmanta/inmanta",
    license="Apache Software License 2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="orchestrator orchestration configurationmanagement",
    project_urls={
        "Bug Tracker": "https://github.com/inmanta/inmanta-core/issues",
        "Documentation": "https://docs.inmanta.com/community/latest/",
    },
    install_requires=[
        "inmanta-core==16.0.0",
        "inmanta-ui==5.1.7",
    ],
    # explicitly declare packages so setuptools does not attempt auto discovery
    packages=[],
)
