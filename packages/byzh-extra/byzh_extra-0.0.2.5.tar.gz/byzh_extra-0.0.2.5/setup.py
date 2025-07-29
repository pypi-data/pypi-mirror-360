from setuptools import setup, find_packages
import byzh_extra

setup(
    name='byzh_extra',
    version=byzh_extra.__version__,
    author="byzh_rc",
    description="基于byzh_core的扩展包",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'byzh_core>=0.0.2.1',
        'python-pptx',
        'pdf2image'
    ],
    package_data={
        'byzh_extra': ['bin/*']
    }
)
