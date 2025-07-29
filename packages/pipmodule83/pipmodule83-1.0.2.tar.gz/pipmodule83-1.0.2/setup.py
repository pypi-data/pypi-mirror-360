from setuptools import setup, find_packages
import os

# Specify encoding as utf-8 when reading the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pipmodule83',
    packages=find_packages(),
    include_package_data=True,
    version="1.0.2",
    description='Bangladeshi Robi/Airtel Circle Information Tools!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='CyberSH',
    author_email='cybershbd@gmail.com',
    #install_requires=[],

    keywords=["cybershbd","cyber sh","circleinfo","circle info","circle number to info","circle username to information","circle nickname to information","robi Airtel circle"],
    classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
            'Environment :: Console',
    ],
    
    license='MIT',
    entry_points={
            'console_scripts': [
                'pipmodule83 = pipmodule83.pipmodule83:circleinfo',
            ],
    },
    python_requires='>=3.9.5'
)
