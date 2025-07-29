from setuptools import setup, find_packages

setup(
    name='multisom',              # opcionalmente pásalo a minúsculas
    version='0.0.0.8',
    author='E.Bringa-F.Aquistapacce-SiMaF',
    author_email='tatoaquistapacce@gmail.com',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    url='https://github.com/SIMAF-MDZ/MultiSOM',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'pandas',
        'numpy',
    ],
    include_package_data=True,
)
