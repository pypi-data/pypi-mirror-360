import setuptools

with open("README.md", "r") as f:
    description = f.read()

setuptools.setup(
    name="AppEnergy",
    version="0.2.1",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4==4.13.4",
        "Requests==2.32.4",
        "selenium==4.33.0",
    ],
    entry_points={
        "console_scripts": [
            "AppEnergy=AppEnergy.main:calculate_energy_consumption",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)