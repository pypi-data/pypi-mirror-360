

from setuptools import setup, find_packages

setup(
    name='git-tips-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'git-tips = git_tips.__main__:main',
        ],
    },
    author='Naoki Hashimoto',
    description='A simple CLI tool that shows a random useful Git tip.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)