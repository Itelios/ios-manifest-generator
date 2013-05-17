#!/usr/bin/python

from optparse import OptionParser
from os.path import basename
import shutil
import fileinput
import os
import sys
import glob
import subprocess
import plistlib
import urlparse
import string
import fnmatch

parser = OptionParser()
# parser.add_option('-f', '--app-bundle', action='store', dest='app_bundle', help='Path to app biundle')
# parser.add_option('-a', '--archive-name', action='store', dest='archive_name', help='Legacy archive filename')
# parser.add_option('-d', '--deployment-address', action='store', dest='deployment_address', help='Remote deployment path, where the app will eventually be hosted')
# parser.add_option('-c', '--changes-page-url', action='store', dest='changes_page_url', help='URL describing the changes that went into this build')

parser.add_option('-a', '--app-bundle', action='store', dest='app_bundle', help='The path of the .app build by XCode before generating an IPA')
parser.add_option('-d', '--deployment-url', action='store', dest='deployment_address', help='The URL where the IPA will be available for user')

(options, args) = parser.parse_args()

if options.app_bundle == None:
	parser.error("Please specify the file path to the app bundle.")
elif options.deployment_address == None:
	parser.error("Please specify the deployment address.")
# elif options.archive_name == None:
#	parser.error("Please specify the filename of the legacy archive.")
# elif options.changes_page_url == None:
#	parser.error("Please specify a URL to a page listing the changes in this build.")

class ManifestGenerator(object):
	"Locates the app's Info.plist"
	def info_plist_filename(self):
		filename = 'Info.plist'
		for file in os.listdir(options.app_bundle):
			if fnmatch.fnmatch(file, '*Info.plist'):
				filename = file
				break
		return filename

	"Generate manifest by parsing values from the app's Info.plist"
	def generate_manifest(self, app_name):
		filename = self.info_plist_filename()
		info_plist_filepath = os.path.join(options.app_bundle, filename)
		info_plist_xml_filename = 'info_plist.xml'
		# Use plutil to ensure that we are dealing with XML rather than the binary format
		subprocess.Popen('plutil -convert xml1 -o ' + info_plist_xml_filename + ' ' + "'" + info_plist_filepath + "'", shell=True).wait()
		info_plist_xml_file = open(info_plist_xml_filename, 'r')
		app_plist = plistlib.readPlist(info_plist_xml_file)
		os.remove(info_plist_xml_filename)
		MANIFEST_FILENAME = basename(app_name) + '.plist' # app_name + '.plist' #  'manifest.plist'
		manifest_plist = {
				'items' : [
					{
						'assets' : [
							{
								'kind' : 'software-package',
								'url' : options.deployment_address,
								}
							],
						'metadata' : {
							'bundle-identifier' : app_plist['CFBundleIdentifier'],
							'bundle-version' : app_plist['CFBundleVersion'],
							'kind' : 'software',
							'title' : app_plist['CFBundleName'],
							}
						}
					]
				}
		plistlib.writePlist(manifest_plist, MANIFEST_FILENAME)
		return MANIFEST_FILENAME

generator = ManifestGenerator()
app_name = os.path.splitext(options.app_bundle)[0]
manifest_filename = generator.generate_manifest(app_name)
