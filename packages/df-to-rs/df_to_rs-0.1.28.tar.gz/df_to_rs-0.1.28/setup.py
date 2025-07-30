from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()
with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()
long_description = f"{readme}\n\n# Changelog\n\n{changelog}"

setup(
    name="df_to_rs",
    version="0.1.28",
    author="Ankit Goel",
    author_email="ankitgoel888@gmail.com",
    description="A package to upload Pandas DataFrame to Redshift",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ankitgoel888/df_to_rs",
    packages=find_packages(),
    package_data={
        '': ['CHANGELOG.md']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "boto3",
        "pandas",
        "psycopg2",
    ],
    python_requires='>=3.6, <4.1',
)