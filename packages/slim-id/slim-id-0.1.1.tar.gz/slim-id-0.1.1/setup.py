
from setuptools import setup
# 公開用パッケージの作成 [ezpip]
import ezpip

# 公開用パッケージの作成 [ezpip]
with ezpip.packager(develop_dir = "./_develop_slim_id/") as p:
	setup(
		name = "slim-id",
		version = "0.1.1",
		description = "This is a tool that automatically generates short IDs",
		author = "bib_inf",
		author_email = "contact.bibinf@gmail.com",
		url = "https://github.co.jp/",
		packages = p.packages,
		install_requires = ["ezpip", "sout>=1.2.1", "relpath"],
		long_description = p.long_description,
		long_description_content_type = "text/markdown",
		license = "CC0 v1.0",
		classifiers = [
			"Programming Language :: Python :: 3",
			"License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"
		],
		entry_points = {	# コマンドラインからの利用
			'console_scripts': [
				'slim_id = slim_id:cmd_func',
				'slim-id = slim_id:cmd_func',
			],
		}
	)
