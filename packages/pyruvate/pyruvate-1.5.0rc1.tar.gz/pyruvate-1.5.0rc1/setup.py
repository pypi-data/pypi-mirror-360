from setuptools import setup
from setuptools_rust import Binding, RustExtension


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name="pyruvate",
    version="1.5.0rc1",
    description="WSGI server implemented in Rust.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Rust",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
    ],
    keywords='WSGI',
    author='tschorr',
    author_email='t_schorr@gmx.de',
    url='https://gitlab.com/tschorr/pyruvate',
    rust_extensions=[
        RustExtension(
            "pyruvate.pyruvate",
            binding=Binding.PyO3,
            debug=True,
            native=False)],
    packages=["pyruvate"],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [
            'aiohttp',
            'pytest',
            'pytest-asyncio',
            'requests',
            ]},
    entry_points={
        'paste.server_runner': [
            'main=pyruvate:serve_paste',
        ],
    },
)
