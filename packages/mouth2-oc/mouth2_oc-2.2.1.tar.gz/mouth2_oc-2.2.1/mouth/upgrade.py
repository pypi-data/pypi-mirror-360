# coding=utf8
""" Upgrade

Method to upgrade the necessary mouth tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2025-03-14"

# Ouroboros imports
from config import config
from upgrade_oc import upgrade as oc_upgrade
from rest_mysql import Record_MySQL

# Python imports
from os.path import abspath, expanduser
from pathlib import Path

def run() -> int:
	"""Run

	Entry point into the upgrade process. Will upgrades required files, \
	tables, records, etc. for the service

	Returns:
		int
	"""

	# Add the global prepend
	Record_MySQL.db_prepend(config.mysql.prepend(''))

	# Add the primary mysql DB
	Record_MySQL.add_host(
		'mouth',
		config.mysql.hosts[config.mouth.mysql('primary')]({
			'host': 'localhost',
			'port': 3306,
			'charset': 'utf8mb4',
			'user': 'root',
			'passwd': ''
		})
	)

	# Get the path to the data folder
	sData = config.mouth.data('./.data')
	if '~' in sData:
		sData = expanduser(sData)
	sData = abspath(sData)

	# Run the upgrade scripts avaialble and store the new version number
	return oc_upgrade(
		data_path = sData,
		module_path = Path(__file__).parent.resolve(),
		mode = 'module'
	)