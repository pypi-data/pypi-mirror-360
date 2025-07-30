from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_functions',
    version='2.3.0',
    description='Helpful functions from BrynQ',
    long_description='Helpful functions from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'pandas>=1,<3',
        'requests>=2,<=3',
        'pyarrow>=10',
        'pandera<=0.22.0',
        'numpy<2',
    ],
    zip_safe=False,
)
