from setuptools import setup, find_packages

setup(
    name='patternq',
    version='0.0.0',
    packages=find_packages(),
    description='A tool for quantifying subcellular fluorescence pattern changes',
    author='Ira Novianti',
    url='https://patternq.org',
    license='BSD-2-Clause',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning',
    ],
    python_requires='>=3.6',
)
