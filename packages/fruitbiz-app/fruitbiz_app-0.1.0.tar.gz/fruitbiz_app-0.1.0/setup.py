from setuptools import setup, find_packages

setup(
    name='fruitbiz-app',
    version='0.1.0',
    description='A business-focused Flask web application',
    author='Manan Shah',
    author_email='mananshah256462@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.0',
        'Flask-SQLAlchemy',
    ],
    entry_points={
        'console_scripts': [
            'fruitbiz-app = run_launcher:launch',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
