from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cmo_gymnasium',
    version='1.0.0',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        "gymnasium==0.28.1",
        "pygame==2.1.3",
        "mujoco==2.3.3",
        "xmltodict>=0.13.0",
        "pyyaml>=6.0",
        "imageio>=2.27.0",
        "gymnasium-robotics>=1.2.0,<1.3.0", 
        "scipy>=1.7.0",
        "gymnasium[box2d]==0.28.1",
    ],
    setup_requires=['swig'],
    include_package_data=True,
    long_description=long_description, # store README.md to PYPI description
    long_description_content_type='text/markdown',
)


# TO Run build: 
# python setup.py sdist bdist_wheel 

# TO test locally: 
# pip install dist/cmo_gymnasium-<version>-py3-none-any.whl --force-reinstall   

# TO upload to test PYPI:
# python -m twine upload --repository testpypi dist/*