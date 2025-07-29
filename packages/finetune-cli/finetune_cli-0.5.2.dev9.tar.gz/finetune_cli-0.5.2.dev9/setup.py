from setuptools import setup, find_packages

setup(
    name='finetune-cli',
    use_scm_version={
        "local_scheme": "no-local-version",
    },
    setup_requires=['setuptools_scm'],
    author='stupidfish001',
    author_email='shovel@hscsec.cn',
    description='一个将原始语料库变成微调需要的alpaca数据集格式的工具',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'finetune=finetune.main:main'
        ]
    },
    install_requires=['langchain',
                      'typer',
                      'pandas',
                      'loguru',
                      'kink',
                      'langchain_openai',
                      'fastparquet',
                      'pyarrow',
                      'transformers',
                      'trl',
                      'peft',
                      'bitsandbytes',
                      'tensorboard'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
