from setuptools import setup, find_packages

setup(
   name='meu_investimento_fiap_brunoamorim',
   version='0.1',
   packages=find_packages(),
   install_requires=[],
   author='Bruno Amorim',
   author_email='bwasistemas@gmail.com',
   description='Uma biblioteca para cálculos de investimentos.',
   url='https://github.com/bwasistemas/meu_investimento',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.6',
)