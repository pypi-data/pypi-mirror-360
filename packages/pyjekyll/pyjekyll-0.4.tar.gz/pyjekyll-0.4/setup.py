from setuptools import setup

setup(
    name='pyjekyll',
    version='0.4',
    description='A Jekyll Python library for handling Jekyll static sites',
    author='Stefan Nožinić',
    author_email='stefan@lugons.org',
    url='https://github.com/fantastic001/pyjekyll',  # use the URL to the GitHub repo
    download_url='https://github.com/fantastic001/pyjekyll/tarball/0.3',  # I'll explain this in a second
    keywords=['jekyll'],  # arbitrary keywords
    packages=['pyjekyll'],  # this must be the same as the name above
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        # Add dependencies here, e.g., 'requests', 'numpy'
    ],
    python_requires='>=3.7',  # Specify the minimum Python version
)
