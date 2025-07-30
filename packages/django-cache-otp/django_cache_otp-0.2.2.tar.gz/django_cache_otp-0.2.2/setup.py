from setuptools import setup, find_packages


setup(
    name="django-cache-otp",
    version="0.2.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=4.0",
        "cryptography>=41.0.5"
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    author="Ali Joghataee",
    author_email="alijoghataee77@gmail.com",
    description="OTP system based on cache",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alijoghataee/django_cache_otp",
    project_urls={
        "GitHub": "https://github.com/alijoghataee/django_cache_otp",
    },
    license="MIT",
)
