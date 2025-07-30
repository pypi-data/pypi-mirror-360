from setuptools import setup, find_packages

setup(
    name='django_persian_currency',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    description='A Django app to work with Iranian currency.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mohammad Javad',
    author_email='ramezanpourmohammadjavad@gmail.com',
    url='https://github.com/MohammadJavadRamezanpour/django_persian_currency',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
