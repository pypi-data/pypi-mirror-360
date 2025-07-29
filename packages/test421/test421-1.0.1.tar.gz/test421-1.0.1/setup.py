from setuptools import setup
from setuptools.command.install import install


class InstallCommand(install):
    def run(self):
        # Only raise error when this is a genuine installation, not during the build process
        if not self.dry_run and not getattr(self.distribution, '_is_building', False):
            raise RuntimeError("You are trying to install a dummy package that is not meant to be installed. Check your registry configuration.")
        install.run(self)


setup(
    name='test421',
    version='1.0.1',
    author='Seznam',
    author_email='security@firma.seznam.cz',
    url='https://seznam.cz/',
    # Use description_file instead of readme to avoid warning
    long_description="""This is a security placeholder package.""",
    long_description_content_type='text/markdown',
    description='A package preventing Dependency Confusion attacks against Seznam.',
    cmdclass={
        'install': InstallCommand,
    },
)