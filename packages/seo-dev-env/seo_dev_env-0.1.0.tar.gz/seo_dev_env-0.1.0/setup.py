from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="seo-dev-env",
    version="0.1.0",
    author="Votre Nom",
    author_email="orsinimelchisedek@gmail.com",
    description="Générateur d'environnements de développement pour tous niveaux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/https://github.com/elkast/seo-dev-env",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "seo": ["templates/*", "templates/**/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'flask>=2.0.0',
        'python-dotenv>=0.19.0',
    ],
    entry_points={
        'console_scripts': [
            'seo-create=seo.generators:main',
        ],
    },
)