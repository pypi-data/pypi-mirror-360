from setuptools import setup, find_packages

# Read version from VERSION file
with open("VERSION") as f:
    version = f.read().strip()

# ✅ NEW: Read README.md for PyPI description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='QAppuccinoLibrary',
    version=version,
    description='Reusable Robot Framework keyword library for QAppuccino TestOps',
    long_description=long_description,
    long_description_content_type="text/markdown",  # 👈 Important: tells PyPI it’s markdown
    author='Eric Zamora',
    author_email='eric.zamora@lpstech.com',
    url='https://github.com/LPS-PH-ODC/QAppuccinoLibrary',
    packages=find_packages(),
    package_data={
        'qappuccino': ['*.resource'],
        'qappuccino.qappuccinoSteps': ['*.resource'],
    },
    include_package_data=True,
    install_requires=[
        'robotframework>=7.3',
        'robotframework-seleniumlibrary>=6.7.1',
        'allure-robotframework>=2.14.2',
        'allure-python-commons>=2.14.2',
        'robotframework-requests>=0.9.7',
        'robotframework-jsonlibrary>=0.5',
        'robotframework-datadriver>=1.11.2',
        'pywinauto>=0.6.8',
        'wapiti3>=3.2.4',
        'semgrep>=1.122.0',
        'DateTime>=5.5',
        'bandit>=1.8.3',
        'pandas>=2.3.0',
    ],
    classifiers=[
        "Framework :: Robot Framework",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
