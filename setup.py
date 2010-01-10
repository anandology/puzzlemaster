from setuptools import setup

setup(
    name='puzzlemaster',
    version='0.1',
    description='Utility to generare, solve and render puzzles',
    author='Anand Chitipothu',
    author_email='anandology@gmail.com',
    url=' http://anandology.github.com/puzzlemaster',
    packages=['puzzlemaster'],
    license="",
    platforms=["any"],
    entry_points = {
        'console_scripts': [
            'puzzlemaster = puzzlemaster.cli:main',
        ]
    }
 )

