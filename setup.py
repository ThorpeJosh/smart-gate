from setuptools import setup

setup(
    name='smart-gate',
    version='0.0.1',
    url='https://github.com/ThorpeJosh/smart-gate',
    license='MIT',
    author='Joshua Thorpe',
    author_email='josh@thorpe.engineering',
    description='IOT inspired Raspberry Pi controller for a motorised gate.',
    long_description=''.join(open('README.md', encoding='utf-8').readlines()),
    long_description_content_type='text/markdown',
    keywords=['IOT', 'RPi', 'smart', 'gate'],
    packages=['rpi_src'],
    include_package_data=True,
    install_requires=['pyserial>=3.4', 'pathlib==1.0.1', 'schedule>=0.6.0', 'gpiozero>=1.5.0',
                      'RPI.GPIO>=0.7.0', 'jsonschema>=3.0.0'],
    extras_require={"dev": ["pytest>=6.0.0", "pylint<=2.5.3", "tox>= 3.0.0"]},
    python_requires='>=3.5',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
    ]
)
