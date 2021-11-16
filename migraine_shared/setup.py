import setuptools

setuptools.setup(
    name='migraine_shared',
    # Should follow Semantic Versioning <https://semver.org/>
    version='0.0.1',
    # author='',
    # author_email='',
    packages=setuptools.find_packages(),
    url='https://github.com/fogies/aws-infrastructure-migraine',
    # license='',
    # description='',
    # long_description='',
    python_requires='>=3',
    install_requires=[
        'ruamel.yaml>=0.17,<0.18',
    ],
)
