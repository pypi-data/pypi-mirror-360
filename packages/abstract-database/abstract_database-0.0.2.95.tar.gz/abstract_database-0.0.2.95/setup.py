import setuptools
import os
def get_abs_dir():
    return os.path.abspath(__name__)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='abstract_database',
    version='0.0.2.95',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description="",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=['sqlalchemy', 'abstract_pandas', 'pandas','abstract_utilities'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    # Add this line to include wheel format in your distribution
    setup_requires=['wheel'],
    include_package_data=True,  # Include package data specified in MANIFEST.in

)
