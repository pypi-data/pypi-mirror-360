from setuptools import setup, find_packages
setup(name='morality',version='0.0.2', # 0.0.1 was same but without long_description and description below
      license='Apache 2',platforms='any',
      url='https://spqrz.gitlab.io/morality.html',
      author='spqrz',author_email='spqrz386@gmail.com',
      description='Warns about the practice of importing invented package names',
      long_description='''
    I'm sorry Cady, I'm afraid I can't do that.

    In an early scene in the film M3GAN 2.0 (Blumhouse 2025),
    12-year-old Cady is seen attempting to import morality,
    and getting an error that the package does not exist.

    What is not shown is, if that system included *uncurated*
    third-party packages in its search, 'morality' could have
    done literally *anything*.

    Thankfully I managed to get there first in PyPI so this
    function does nothing.  But someone else could have given
    you a Trojan horse, which would eventually be removed
    from the library, but removal can take time, so you
    should always *check* packages before you use them!

    The purpose of this package is simply to serve as a
    gentle warning that you weren't supposed to imitate what
    Cady did in that scene :)
    ''',
      long_description_content_type='text/markdown',
      packages=find_packages(),
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent'])
