import setuptools

with open('README.md') as readme_file:
    README = readme_file.read()

setuptools.setup(
    name='takeme_mailgun',
    version='1.0.5',
    description='Python Wrapper for Mailgun API',
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests'
    ],
    keywords='mailgun mail TakeMe',
    url='https://github.com/takeme-pay/mailgun',
    author='Yukitaka Maeda',
    author_email='yukitaka.maeda@japanfoodie.jp',
    license='GPLv3+',
    packages=setuptools.find_packages(),
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)

