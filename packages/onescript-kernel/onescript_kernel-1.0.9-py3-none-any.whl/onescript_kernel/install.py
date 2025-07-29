from jupyter_client.kernelspec import install_kernel_spec
import os

def main():
    kernel_dir = os.path.join(os.path.dirname(__file__), 'kernel_spec')
    install_kernel_spec(kernel_dir, kernel_name='onescript', user=True, replace=True)
    print("OneScript kernel installed for Jupyter.")
