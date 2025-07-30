import os
import sys
import subprocess
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.build_py import build_py

# 🔧 Flag to skip native build in CI or wheel builds
SKIP_NATIVE_BUILD = bool(os.getenv('DSNIFF_SKIP_NATIVE_BUILD', False))


class PostInstallCommand(install):
    """Custom install command to build and install dsniff C binaries."""
    def run(self):
        # If skipping native build, create empty bin directory and proceed
        if SKIP_NATIVE_BUILD:
            print("Skipping native build due to DSNIFF_SKIP_NATIVE_BUILD=1")
            dest_bin = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dsniff_py', 'bin')
            if os.path.exists(dest_bin):
                shutil.rmtree(dest_bin)
            os.makedirs(dest_bin, exist_ok=True)
            print("""
⚠️ Note: This package was installed without native binaries.
To use dsniff tools, install via 'pip install .' or use system binaries.
""")
            return super().run()

        # Otherwise, proceed with native build
        cwd = os.path.abspath(os.path.dirname(__file__))
        tmp_dir = os.path.join(cwd, 'tmp')
        build_dir = os.path.join(cwd, 'build')
        c_src_dir = os.path.join(cwd, 'dsniff-old')

        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(build_dir, exist_ok=True)

        env = os.environ.copy()
        env['TMPDIR'] = tmp_dir

        libpcap = env.get('DSNIFF_LIBPCAP', '/usr/local/opt/libpcap')
        libnet = env.get('DSNIFF_LIBNET', '/usr/local/opt/libnet')
        libnids = env.get('DSNIFF_LIBNIDS', '/usr/local/opt/libnids')
        openssl = env.get('DSNIFF_OPENSSL', '/usr/local/opt/openssl')

        db_path = None
        if not os.getenv('CI'):
            db_path = env.get('DSNIFF_DB_PATH')
            ...

        if db_path:
            env['CPPFLAGS'] = env.get('CPPFLAGS', '') + f' -I{db_path}/include'
            env['LDFLAGS'] = env.get('LDFLAGS', '') + f' -L{db_path}/lib'

        old_cwd = os.getcwd()
        os.chdir(c_src_dir)

        try:
            config_cmd = [
                './configure',
                f'--with-libpcap={libpcap}',
                f'--with-libnet={libnet}',
                f'--with-libnids={libnids}',
                f'--with-openssl={openssl}',
                '--without-x',
                f'--sbindir={os.path.join(build_dir, "bin")}',
                f'--prefix={build_dir}',
            ]

            if db_path:
                config_cmd.insert(1, f'--with-db={db_path}')
            elif sys.platform == 'darwin' or os.getenv('CI'):
                config_cmd.insert(1, '--with-db=no')

            if os.getenv('CI'):
                env['ac_cv_header_pcap_bpf_h'] = 'no'
                env['ac_cv_header_pcap_nopacketinfo_h'] = 'yes'
                env['ac_cv_header_pcap_linux_types_h'] = 'no'

            print(f"Running configure in {c_src_dir}")
            subprocess.check_call(config_cmd, env=env)
            subprocess.check_call(['make'], env=env)
            subprocess.check_call(['make', 'install'], env=env)

        finally:
            os.chdir(old_cwd)

        dest_bin = os.path.join(cwd, 'dsniff_py', 'bin')
        if os.path.exists(dest_bin):
            shutil.rmtree(dest_bin)
        shutil.copytree(os.path.join(build_dir, 'bin'), dest_bin)

        super().run()


class ConditionalBuild(build_py):
    """Skip native build during wheel creation."""
    def run(self):
        if self.distribution.script_args[0] in ('bdist_wheel', 'build_sphinx'):
            print("Skipping native build for wheel")
            return super().run()
        print("Building native components...")
        PostInstallCommand.run(self)


long_description = ''
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='dsniff',
    version='0.1.0',
    author='Modified Dug Song dsniff by Josh James',
    author_email='josh@rocketnow.com',
    description='Python wrapper for dsniff network utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'arpspoof=dsniff_py.cli:main',
            'dnsspoof=dsniff_py.cli:main',
            'dsniff=dsniff_py.cli:main',
            'filesnarf=dsniff_py.cli:main',
            'mailsnarf=dsniff_py.cli:main',
            'msgsnarf=dsniff_py.cli:main',
            'urlsnarf=dsniff_py.cli:main',
            'macof=dsniff_py.cli:main',
            'sshow=dsniff_py.cli:main',
            'sshmitm=dsniff_py.cli:main',
            'webmitm=dsniff_py.cli:main',
            'webspy=dsniff_py.cli:main',
            'tcpkill=dsniff_py.cli:main',
            'tcpnice=dsniff_py.cli:main',
            'dsniff-menu=dsniff_py.menu:main',
        ]
    },
    cmdclass={
        'install': PostInstallCommand,
        'build_py': ConditionalBuild,
    },
    python_requires='>=3.6',
    data_files=[],
    zip_safe=False,
)