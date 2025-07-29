from setuptools import setup, find_packages
from setuptools.command.install import install
from jupyter_client.kernelspec import install_kernel_spec

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        install_kernel_spec('onescript_kernel', kernel_name='onescript', user=True, replace=True)

setup(
    name='onescript-kernel',
    version='1.0.4',
    packages=find_packages(),
    author='Nikolay Krasnov',
    author_email='nikolay@krasnov.cf',
    description='OneScript kernel for Jupyter',
    long_description='A kernel that allows running OneScript code in Jupyter notebooks',
    long_description_content_type='text/markdown',  # если long_description в markdown
    url='https://github.com/yourname/onescript-kernel',  # желательно указать
    package_data={
        'onescript_kernel': ['kernel.json'],
    },
    include_package_data=True,
    install_requires=[
        'jupyter_client',
        'ipykernel'
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
)