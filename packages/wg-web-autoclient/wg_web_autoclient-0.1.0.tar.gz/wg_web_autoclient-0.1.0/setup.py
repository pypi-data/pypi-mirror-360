from setuptools import setup, find_packages

setup(
    name='wg_web_autoclient',
    version='0.1.0',
    description='WireGuard automation client with async support using Selenium and aiohttp',
    author='Zurlex',
    author_email='your_email@example.com',  # можешь указать свою почту или удалить строку
    url='https://github.com/Zurlex/wg_client_work',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',
        'webdriver-manager>=4.0.0',
        'aiohttp>=3.8.0',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: System :: Networking',
    ],
    python_requires='>=3.8',
)
