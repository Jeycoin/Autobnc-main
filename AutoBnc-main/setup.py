from setuptools import setup, find_packages

setup(
    name='autotx-cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'pandas',
        'mplfinance',
        'binance',
        'autogen',
    ],
    entry_points={
        'console_scripts': [
            'autotx=your_script_name:run_autotx',
        ],
    },
)
