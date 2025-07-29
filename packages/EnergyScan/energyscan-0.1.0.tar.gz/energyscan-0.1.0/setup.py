import setuptools

setuptools.setup(
    name="EnergyScan",
    version="0.1.0",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4==4.13.4",
        "Requests==2.32.4",
        "selenium==4.33.0",
    ],
    entry_points={
        "console_scripts": [
            "EnergyScan=EnergyScan.main:calculate_energy_consumption",
        ],
    },
)