# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='utube_server',
    version='0.4',
    description='Api server to work with utube',
    long_description='Used with youtube unity plugin',
    author='KRosa',
    author_email='aventurasmiudas@gmail.com',
    url='',
    packages=['youtube_dl_server'],
    entry_points={
        'console_scripts': [
            'youtube-dl-server = youtube_dl_server.server:main',
        ],
    },

    install_requires=[
        'Flask',
        'git+https://github.com/yt-dlp/yt-dlp.git',
        'pycryptodomex',
    ],

    classifiers=[
        'Topic :: Multimedia :: Video',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: Public Domain',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
