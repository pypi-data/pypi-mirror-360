from setuptools import setup, find_packages

setup(
    name='hiplt',
    version='0.2.2',
    description='hiplt — компонентная плагин-система, команды, API и конфиги в одном.',
    long_description='Hip — модульный фреймворк для Python с поддержкой плагинов, конфигураций и встроенного API.',
    long_description_content_type='text/markdown',
    author='CSOforyou',
    author_email='defolt032@gmail.com',
    url='https://github.com/CSOforyou/hip',  # исправлено
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='hip plugins modular cli api configuration framework',
    project_urls={
        'Bug Tracker': 'https://github.com/CSOforyou/hip/issues',  # исправлено
        'Source': 'https://github.com/CSOforyou/hip',             # исправлено
    },
)