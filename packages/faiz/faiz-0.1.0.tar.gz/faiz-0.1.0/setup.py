from setuptools import setup, find_packages

setup(
    name='faiz',
    version='0.1.0',
    author='Faiz Rajput',
    author_email='faizrajput1510@gmail.com',
    description='A personal multipurpose command-line tool (env, git, images, etc.)',
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,   # This is key to include MANIFEST.in files
    install_requires=[
        'requests',
        'beautifulsoup4',
        'python-dotenv',
        'pyautogui',
    ],
    entry_points={
        'console_scripts': [
            'faiz=faiz.faiz:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.6',
)
