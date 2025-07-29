from setuptools import setup, find_packages

setup(
    name='watchlog-python',
    version='0.2.2',  # نسخه جدید برای تغییر مهم در عملکرد
    packages=find_packages(),
    install_requires=[],  # هیچ وابستگی‌ای نیاز نیست چون از urllib استفاده می‌کنیم
    include_package_data=True,
    license='MIT License',
    description='A simple and non-blocking Python package for sending custom metrics to Watchlog.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/watchlogserver/watchlog-python',
    author='mohammad',
    author_email='mohammadnajm75@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
