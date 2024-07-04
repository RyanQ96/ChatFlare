from setuptools import setup, find_packages 

setup(
    name='chatflare', 
    version='0.1.0', 
    packages=find_packages(), 
    include_package_data=True,
    install_requires=[

    ], 
    entry_points={
        'console_scripts': [
            # CLI Commands 
        ]
    },  
    author='Rui Qiu',
    author_email='qiurui96@gmail.com',
    description='Lightning-fast framework for building and deploying Large Language Models applications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/chatflare',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)