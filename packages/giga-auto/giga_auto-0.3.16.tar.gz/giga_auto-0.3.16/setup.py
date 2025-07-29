from setuptools import setup, find_packages

setup(
    name='giga_auto',
    version='0.3.16',
    description='giga auto test common package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='LangMuQing',
    author_email='langli0728@gmail.com',
    url='https://github.com/your_username/your_package_name',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)