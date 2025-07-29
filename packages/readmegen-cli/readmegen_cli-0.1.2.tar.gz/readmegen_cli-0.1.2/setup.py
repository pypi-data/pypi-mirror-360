from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='readmegen-cli',
    version='0.1.2',
    author='Ganesh Sonawane',
    author_email='sonawaneganu3101@gmail.com',
    description='Generate professional README.md files using AI\n "Use readmegen-cli ." to generate a README.md file for your project.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/inevitablegs/git-readme',  # ✅ Updated to the new repo URL
    packages=find_packages(),
    license='MIT',  # Simple string declaration
    install_requires=[
        'google-generativeai==0.8.4',
        'python-dotenv==1.0.1',
    ],
    entry_points={
    'console_scripts': [
        'readmegen-cli=readmegen_core.cli:main',  # ✅ change from readmegen → readmegen-cli
    ],
},

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)