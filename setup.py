from setuptools import setup

setup(
    name='pinnwand',
    version='0.0.dev',
    packages=['pinnwand'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'Pygments'
    ]
)
