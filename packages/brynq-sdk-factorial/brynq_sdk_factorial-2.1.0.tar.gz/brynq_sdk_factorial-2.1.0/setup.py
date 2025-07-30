from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_factorial',
    version='2.1.0',
    description='Factorial wrapper from BrynQ',
    long_description='Factorial wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'pandas>=2.2.0,<3.0.0',
    ],
    zip_safe=False,
)
