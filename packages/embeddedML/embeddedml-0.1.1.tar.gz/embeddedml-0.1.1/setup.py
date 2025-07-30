from setuptools import setup, find_packages

setup(
    name="EmbeddedML",
    version="0.1.1",
    description="Optimized Machine Learning Library for Embedded Systems",
    author="Halil Hüseyin Çalışkan",
    author_email="caliskanhalil815@gmail.com",
    license="MIT",
    packages=find_packages(),  # Burada otomatik embeddedML klasörünü bulur
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
