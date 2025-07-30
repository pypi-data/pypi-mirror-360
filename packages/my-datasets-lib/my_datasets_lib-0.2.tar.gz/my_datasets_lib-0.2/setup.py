from setuptools import setup, find_packages

setup(
    name='my_datasets_lib',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
    ],
    description='A library of custom datasets.',
    author='Emilio Dulay',
    author_email='emiliodulay19@g.ucla.edu',
    url="https://github.com/emilio-dulay/my_datasets_lib",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
