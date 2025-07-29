from setuptools import setup, find_packages

setup(
    name='go-ssh',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paramiko',
        'keyring'
    ],
    entry_points={
        'console_scripts': [
            'gossh=gossh.gossh:main',
        ],
    },
    author='Mr kumar',
    author_email='mrpirate404@gmail.com',
    description='Smart SSH connector using fuzzy host search and auto-key upload',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/go-ssh/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
