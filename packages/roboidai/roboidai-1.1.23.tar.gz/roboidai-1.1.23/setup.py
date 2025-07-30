from setuptools import setup, find_packages

setup(
	name="roboidai",
	version="1.1.23",
	author="Kwang-Hyun Park",
	author_email="akaii@kw.ac.kr",
	description="Python Package for Roboid AI",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	install_requires=["roboid", "ifaddr", "pyttsx3", "pynput", "pandas", "matplotlib", "scikit-learn", "numpy", "mediapipe", "fer", "opencv-python", "tensorflow", "tf_keras"],
	packages=find_packages(exclude=["examples", "tests"]),
	python_requires=">=3",
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		"License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)"
	]
)