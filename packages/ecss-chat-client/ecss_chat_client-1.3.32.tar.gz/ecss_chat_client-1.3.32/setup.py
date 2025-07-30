from setuptools import find_packages, setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='ecss_chat_client',
    version='1.3.32',
    author='maxstolpovskikh, LedxDelivery',
    author_email='maximstolpovskikh@gmail.com, korstim18@gmail.com',
    description='This is the simplest module HTTP API EcssChatServer',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['requests>=2.32.3'],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='ecss_chat_client',
    python_requires='>=3.12.3',
)
