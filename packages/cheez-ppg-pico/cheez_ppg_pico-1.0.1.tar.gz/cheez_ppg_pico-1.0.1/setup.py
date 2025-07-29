from setuptools import setup, find_packages

setup(  
    name='cheez_ppg_pico',
    version='1.0.1',
    description='SDK for CheezPico(PPG) USB/BLE Devices',
    long_description=open('README.md', encoding='utf-8').read(),  
    long_description_content_type='text/markdown',
    author='vecang', 
    packages=find_packages(),
    install_requires=[
        'pyserial',
        'aioserial' 
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
