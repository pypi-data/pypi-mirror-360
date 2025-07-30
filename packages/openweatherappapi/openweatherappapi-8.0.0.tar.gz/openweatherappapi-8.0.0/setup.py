import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='openweatherappapi',
	version='8.0.0',
	author='__token__',
	author_email='alikushbaev2@gmail.com',
	description='Weather App',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/alikushbaev/Weatherapp',
	project_urls={
		'Documentation': 'https://github.com/alikushbaev/Weatherapp',
	},
	packages=['openweatherappapi'],
	install_requires=["geopy", "pystray", "datetime", "pytz", "requests", "timezonefinder", "pillow"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)