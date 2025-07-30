from setuptools import setup, find_packages
VERSION = '0.0.14'
DESCRIPTION = 'Phenom Public Apis SDK for Python'
def read_readme():
    with open('README.md', 'r') as f:
        return f.read()
# Setting up
setup(
    name="phenom_api_management",
    version=VERSION,
    author="phenom",
    author_email="api-management@phenom.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=read_readme(),
    packages=find_packages(),
    install_requires=['PyJWT==2.4.0', 'certifi==2025.6.15', 'urllib3==2.5.0', 'six==1.16.0'],
    keywords=['resumeparser', 'search', 'jobs', 'candidate', 'employee', 'phenom'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
    ]
)