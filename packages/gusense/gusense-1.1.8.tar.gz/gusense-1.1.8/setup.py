# import re
import setuptools

version = "1.1.8"
# with open('gusense/__init__.py', 'r') as fd:
#     version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
#                         fd.read(), re.MULTILINE).group(1)
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="gusense",
    version=version,
    author="wgp",
    author_email="284250692@qq.com",
    description="This is API util",
    license='BSD License',
    python_requires='>=2.7',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.python.org",
    install_requires=[
        'requests',
        'pandas',
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )
)
