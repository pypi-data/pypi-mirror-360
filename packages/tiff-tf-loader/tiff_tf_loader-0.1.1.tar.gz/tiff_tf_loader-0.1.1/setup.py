from setuptools import setup, find_packages

setup(
    name='tiff-tf-loader',
    version='0.1.1',
    description='Load TIFF images into TensorFlow datasets using rasterio',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Hari Babu KVN',
    author_email='haribabuatwork@gmail.com',
    url='https://github.com/haribabugitwork/tiff-tf-loader',
    packages=find_packages(),
    install_requires=[
        'tensorflow>=2.8',
        'rasterio',
        'scikit-learn',
        'numpy'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
