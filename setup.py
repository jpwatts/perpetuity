from distutils.core import setup


setup(
    name="Perpetuity",
    version="0.0.1",
    description="A retirement simulator",
    author="Joel Watts",
    author_email="joel@joelwatts.com",
    url="http://github.com/jpwatts/perpetuity",
    packages=[
        "perpetuity",
    ],
    install_requires=[
        "click",
    ],
    entry_points={
        'console_scripts': [
            "perpetuity = perpetuity.simulation:main",
        ],
    }
)
