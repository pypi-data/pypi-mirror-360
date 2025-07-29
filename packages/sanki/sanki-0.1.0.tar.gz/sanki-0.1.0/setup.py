from setuptools import setup, find_packages

setup(
    name='sanki',
    version='0.1.0',
    packages=find_packages(),
    description='Custom AI training library by Sanki',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Sanki',
    author_email='schoudhary112566@gmail.com',
    keywords=['machine learning', 'ai', 'sanki'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)