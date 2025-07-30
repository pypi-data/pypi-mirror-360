from setuptools import setup, find_packages

setup(
    name='moviecli',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['cli', 'torrent_downloader', 'utils', 'ytswebs', 'config'],
    install_requires=[
        'click',
        'InquirerPy',
        'torrentp',
        'beautifulsoup4',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'moviecli=cli:search',
        ],
    },
    author='yannickRafael',
    author_email='yannickrafael286@gmail.com',
    description='CLI tool for searching and downloading movies from yts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yannickRafael/moviecli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
)