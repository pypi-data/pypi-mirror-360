import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pricegoldtoday-indonesia",
    versions="0.0.4",
    author="Haeder Ali",
    author_email="haederalee@gmail.com",
    description="This package will get update price gold in Indonesia, source from lakuemas.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    License = "GNU General Public License v3 (GPLv3)e",
    url="https://github.com/masalee-dev/price-gold-today-id",
    project_url={
        "Github profile": "https://github.com/Masalee-hub",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
   # package_dir={"": "src"},
   # packages=(setuptools.find_packages(where="src"),
    packages= setuptools.find_packages(),
    python_requires=">=3.13",
)
