from setuptools import setup, find_packages

setup(
    name='fileasy',
    version='0.1.2',
    license='Apache-2.0',

    py_modules=['fileasy'],
    
    entry_points={
        'console_scripts': [
            'fileasy=fileasy:main',
        ],
    },

    author= "Nazim Adda",
    author_email = "adda.nazim7@gmail.com",

    url='https://nazimadda.github.io/fileasy/',
    project_urls={
        'Bug Reports': 'https://github.com/nazimadda/fileasy/issues',
        'Source': 'https://github.com/nazimadda  ',
    },

    
    description='Fileasy is a simple CLI tool to convert images to PDFs and vice versa, and merge PDFs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Environment :: Console',
    ],
    platforms=['Unix', 'Windows', 'MacOS'],
    
    keywords='file conversion pdf image merge cli',

    zip_safe=False,
    
    install_requires=[
        "pdf2image>=1.17.0",
        "pillow>=9.0.0",
        "PyPDF2>=3.0.0"
    ],

    python_requires='>=3.7',
)
