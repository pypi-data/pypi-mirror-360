from setuptools import setup, find_packages

setup(
    name='pyrebase_air',
    version='4.10.0',
    url='https://github.com/kbirger/pyrebase-air',
    description='A simple python wrapper for the Firebase API with current deps',
    author='kbirger',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests-toolbelt>=1.0.0',
        'requests>=2.31',
        'urllib3>=2.0',
        'gcloud>=0.18.3',
        'oauth2client>=4.1.2',
        'python-jwt>=2.0.1',
        'pycryptodome>=3.6.4'
    ]
)
