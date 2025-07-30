import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="adi_spo2_watch",
    version="6.10.0",
    author="Analog Devices, Inc.",
    author_email="healthcare-support@analog.com",
    license='BSD 3-Clause License',
    description="ADI SpO2 Watch Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/analogdevicesinc/spo2-watch-sdk",
    packages=["adi_spo2_watch",
              "adi_spo2_watch.core",
              "adi_spo2_watch.core.enums",
              "adi_spo2_watch.application",
              "adi_spo2_watch.core.packets",
              "adi_spo2_watch.core.data_types",
              "adi_spo2_watch.application.vsm_mb_sb",
              "adi_spo2_watch.application.study_watch",
              ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.6',
    install_requires=['pyserial==3.5', 'tqdm==4.61.0', 'libusb1==3.0.0'],
)
