from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
		name="linksdk",
		version="0.0.1a101",
		author="Linkplay",
		author_email="tao.jiang@linkplay.com",
		description="A Python-based API interface for controlling and communicating with WiiM audio devices.",
		url="https://github.com/WiimHome/wiim",
		license="MIT",
		package_dir={"": "src"},
		packages=find_packages(where="src"),
		package_data={"linksdk": ["py.typed"]},
		include_package_data=True,
		classifiers=[
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		]
	)
