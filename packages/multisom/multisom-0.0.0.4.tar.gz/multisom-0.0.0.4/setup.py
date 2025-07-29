from setuptools import setup, find_packages

setup(
    name='MultiSOM',
    version='0.0.0.4',
    author='E.Bringa-F.Aquistapacce-SiMaF',
    author_email='tatoaquistapacce@gmail.com',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    url='https://github.com/SIMAF-MDZ/MultiSOM',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['pandas','numpy'],
    include_package_data=True,
)
