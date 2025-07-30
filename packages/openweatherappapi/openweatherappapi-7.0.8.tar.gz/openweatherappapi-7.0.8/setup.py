import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='openweatherappapi',
	version='7.0.8',
	author='__token__',
	author_email='alikushbaev2@gmail.com',
	description='Weather App',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/alikushbaevyt/weatherapp',
	project_urls={
		'Documentation': 'https://github.com/alikushbaevyt/weatherapp',
	},
	packages=['openweatherappapi'],
	install_requires=["timezonefinder", "pillow", "pystray", "datetime", "pytz", "requests", "geopy"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)