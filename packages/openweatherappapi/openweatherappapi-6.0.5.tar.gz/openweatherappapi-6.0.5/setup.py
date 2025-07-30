import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='openweatherappapi',
	version='6.0.5',
	author='__token__',
	author_email='alikushbaev2@gmail.com',
	description='Weather App',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/alikushbaevYT/weatherapp',
	project_urls={
		'Documentation': 'https://github.com/alikushbaevYT/weatherapp',
	},
	packages=['openweatherappapi'],
	install_requires=["datetime", "pytz", "pillow", "requests", "geopy", "timezonefinder", "pystray"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)