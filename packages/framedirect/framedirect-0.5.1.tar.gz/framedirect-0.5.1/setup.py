from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='framedirect',
    version='0.5.1',
    author='gneval9 Software',
    author_email='gneval99@gmail.com',
    description='Una librería para dibujar píxeles usando el framebuffer de Linux en Python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/gneval9/FrameDirect',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics',
        'Intended Audience :: Developers',
    ],
)

