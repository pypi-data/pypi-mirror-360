import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='VakSmsApi',
	version='1.0.1',
	author='LunaModules',
	author_email='probeb589@gmail.com',
	description='Модуль для связи API (vak-sms.com)',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Nelliprav/VakSmsApi',
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)