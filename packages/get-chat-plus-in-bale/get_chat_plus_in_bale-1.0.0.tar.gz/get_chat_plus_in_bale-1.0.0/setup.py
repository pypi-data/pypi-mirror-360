from setuptools import setup, find_packages

setup(
    name='get_chat_plus_in_bale',
    version='1.0.0',
    author='MohammadReza',
    author_email='narnama.room@gmail.com',
    description='get_chat_plus_in_bale . 🐍✨',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4',
        'aiohttp'
    ],
    project_urls={
        'صفحه من ❤️' : 'https://apicode.pythonanywhere.com/',
    },
)