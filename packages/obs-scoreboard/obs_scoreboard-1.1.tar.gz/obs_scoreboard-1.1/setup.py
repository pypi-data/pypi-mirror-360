from pathlib import Path
from setuptools import setup

readme_file = Path(__file__).parent.resolve() / 'README.md'
readme_contents = readme_file.read_text()

setup(
    name="obs-scoreboard",
    version="1.1",
    description='Simple python-powered scoreboard for use with my online webcasts.',
    url='https://github.com/gsl4295/scores',
    license='MIT',
    packages=['scores'],
    package_data={"scores": ["fonts/*.ttf", "images/*.png"],},
    include_package_data=True,
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    author="",
    install_requires=["dearpygui"],
    entry_points={
        'gui_scripts': ['scoreboard=scores.scores:main']
    }
)