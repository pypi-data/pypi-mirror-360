from setuptools import setup, find_packages

setup(
    name="forcode",
    version="0.1.3",
    description="Generate recursive README.md documentation for Python modules using generative AI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="James",
    author_email="support@forcode.ai",
    url="https://github.com/yourusername/forcode",  # Replace if you have one
    license="Proprietary",
    packages=find_packages(),
    install_requires=[
        "forgen>=0.1.5",
        "openai>=1.73",
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'forcode = forcode.main:main',  # Adjust if main is elsewhere
        ],
    },
)
