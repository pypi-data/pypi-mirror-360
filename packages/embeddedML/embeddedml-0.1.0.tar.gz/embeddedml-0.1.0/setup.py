from setuptools import setup

setup(
    name='EmbeddedML',
    version='0.1.0',
    description='Optimized Machine Learning Library for Embedded Systems',
    author='Halil Hüseyin Çalışkan',
    author_email='caliskanhalil815@gmail.com',
    license='MIT',
    packages=['EmbeddedML'],
    package_dir={"EmbeddedML": "embeddedml"},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
