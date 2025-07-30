from setuptools import setup, find_packages

setup(
    name="my_unique_import",
    version="0.3.17",
    packages=find_packages(),
    include_package_data=True,
    description="A custom importer package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://pypi.org/project/my-unique-import/",
    author="Jingyuan Chen",
    author_email="jchensteve@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'qgit=my_import.quick_git:main',
            'EnvUpdate=my_import.update_env:main',
            'qstart=my_import.start_server:main',
            'hpy=my_import.hsr_run:main',
            'my_shutdown=my_import.auto_control:AutoControl.shutdown',
            # 'AI=my_import:AI',
        ],
    },
    python_requires='>=3.9',
    install_requires=[
        'tqdm==4.66.4'
    ],
)