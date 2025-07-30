from setuptools import setup, find_packages

setup(
    name='JiYan_Wugan',
    version='0.1.0',
    description='过无感验证',
    author='yeeye',
    author_email='d258036653@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyExecJS',
        'requests',
    ],
    python_requires='>=3.6',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
) 