import setuptools

version = {
    "major" :1,
    "minor" :0,
    "patch" :0
}

setuptools.setup(
    name='r3frame2-nightly',
    version=f"{version["major"]}.{version["minor"]}.{version["patch"]}",
    description='A neat little thing... with nightly updates',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Izaiyah Stokes',
    author_email='d34d0s.dev@gmail.com',
    url='https://github.com/r3shape/r3frame2',
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ['r3playground=r3frame2.playground.playground:main']
    },
    install_requires=[
        'pygame-ce', 'pytz', 'numpy', 'numba'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ], include_package_data=True
)