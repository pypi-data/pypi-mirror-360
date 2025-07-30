from setuptools import setup, find_packages

setup(
    name='crypto_address_generator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'bitcoinlib',
        'eth-account',
        'solana',
    ],
    author='Your Name',
    description='Generate BTC, LTC, ETH, and SOL addresses locally',
    url='https://github.com/yourusername/crypto_address_generator',  # optional
    python_requires='>=3.7',
)
