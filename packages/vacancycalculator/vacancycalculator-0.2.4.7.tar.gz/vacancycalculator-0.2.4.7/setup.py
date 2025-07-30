from setuptools import setup, find_packages

setup(
    name='vacancycalculator',
    version='0.2.4.7',
    author='E.Bringa-S.Bergamin-SiMaF',
    author_email='santiagobergamin@gmail.com',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    url='https://github.com/TiagoBe0/VFScript-SiMaF',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['scikit-learn', 'pandas', 'xgboost','ovito','numpy'],
    include_package_data=True,
)
