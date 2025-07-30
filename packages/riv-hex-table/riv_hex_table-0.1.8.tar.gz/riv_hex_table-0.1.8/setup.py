from setuptools import setup, find_packages

setup(
    name='riv_hex_table',
    version='0.1.8', # You can update this version number
    author='Abhishek Pandey', # Replace with your name
    author_email='abhi0008pandey@gmail.com', # Replace with your email
    description='A Python package to generate Hex styled HTML tables from Pandas DataFrames.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/styled-html-tables', # Replace with your project's URL (e.g., GitHub repo)
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0', # Specify the minimum pandas version required
        'ipython>=7.0.0' # Specify the minimum ipython version required, as IPython.core.display is used
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # REMOVE THIS LINE: 'Framework :: Pandas', <--- This was the problematic line
        'Topic :: Scientific/Engineering :: Information Analysis', # New, relevant
        'Topic :: Software Development :: Libraries :: Python Modules', # New, relevant
        'Topic :: Text Processing :: Markup :: HTML',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers', # New, relevant
        'Intended Audience :: Science/Research', # New, relevant
    ],
    python_requires='>=3.7', # Specify minimum Python version
)