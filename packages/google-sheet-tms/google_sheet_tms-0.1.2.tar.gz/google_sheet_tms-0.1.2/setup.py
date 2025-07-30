from setuptools import setup, find_packages

setup(
    name = 'google_sheet_tms',
    version = '0.1.2',
    author = 'Walery Wysotsky',
    author_email = 'dev@wysotsky.info',
    description = 'Use Google Sheet as TMS',
    packages = ['google_sheet_tms'],
    install_requires = [
          'dotenv',
          'gspread',
          'oauth2client'
    ],
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries'
    ]
)