from setuptools import setup, find_packages

setup(
    name="haven",
    version='2.0.2',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    python_requires='>=3',
    install_requires=['events', 'netkit', 'setproctitle', 'gevent', 'gevent-websocket'],
    url="https://github.com/dantezhu/haven",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="flask's style binary server framework",
)
