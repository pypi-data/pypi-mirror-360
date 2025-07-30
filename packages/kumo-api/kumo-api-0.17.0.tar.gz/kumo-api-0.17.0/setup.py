import os
import os.path as osp

from grpc_tools import protoc
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        proto_dirs = [  # Compile all `*.proto` files:
            osp.join('kumoapi', 'rfm', 'protos'),
        ]

        for proto_dir in proto_dirs:
            proto_files = [
                osp.join(proto_dir, f) for f in os.listdir(proto_dir)
                if f.endswith('.proto')
            ]
            assert len(proto_files) > 0

            protoc.main([
                'protoc',
                f'--proto_path={proto_dir}',
                f'--python_out={proto_dir}',
                *proto_files,
            ])

        super().run()


setup(cmdclass={'build_py': build_py})
