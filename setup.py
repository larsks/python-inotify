from setuptools import setup

with open('requirements.txt') as fd:
    setup(name='Python inotify',
          version='1.0',
          description='Low level inotify interface',
          author='Lars Kellogg-Stedman',
          author_email='lars@oddbit.com',
          url='http://blog.oddbit.com/',
          install_requires=fd.readlines(),
          packages = ['inotify'],
         )

