from setuptools import setup

setup(
    name="haven",
    version='1.0.12',
    zip_safe=False,
    platforms='any',
    packages=['haven'],
    install_requires=['events', 'netkit'],
    url="https://github.com/dantezhu/haven",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="flask's style binary server framework",
)
