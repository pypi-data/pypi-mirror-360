from setuptools import setup, find_packages

# Read version and README
with open("sparkxform/VERSION", "r", encoding="utf-8") as version_file:
    version = version_file.read().strip()

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name='sparkxform',
    version=version,
    description='Reusable PySpark transformation functions for enterprise-grade ETL pipelines.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ranjit Maity',
    author_email='ranjitmaity95a@gmail.com',
    url='https://github.com/RanjitM007/sparkxform',
    project_urls={
        'Bug Tracker': 'https://github.com/RanjitM007/sparkxform/issues',
        'Source Code': 'https://github.com/RanjitM007/sparkxform',
        'Documentation': 'https://github.com/RanjitM007/sparkxform/wiki'
    },
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database :: Front-Ends',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
)
