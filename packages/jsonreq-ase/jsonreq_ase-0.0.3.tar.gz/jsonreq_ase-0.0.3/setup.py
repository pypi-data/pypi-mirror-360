import setuptools

setuptools.setup(
    name="jsonreq_ase",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Abss",
    description="Dont install this package, purely testing purpose",
    entry_points={
        'console_scripts': [
            'jsonreq_ase = http_query.http_query:main'
        ]
    },
    install_requires= [
        'click',
        'requests'
    ]
)
