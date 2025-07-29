from setuptools import setup, find_packages

setup(
   name='meu_investimento_ackeley',
   version='0.1',
   packages=find_packages(),
   install_requires=[],
   author='Ackeley Lennon',
   author_email='ackeley@hotmail.com',
   description='Uma biblioteca para cálculos de investimentos.',
   url='https://github.com/ackeley/fiap',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.11.5',
)