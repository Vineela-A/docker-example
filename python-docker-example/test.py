#!/usr/bin/python
#!/usr/bin/env python
import json
from enum import Enum
from pprint import pprint
import xml.etree.ElementTree as ET
import os
from os.path import isfile,abspath,isdir,dirname,realpath
import csv
from collections import namedtuple
import sys
from datetime import datetime,timedelta
import getopt
import requests
import pathlib
import ssl

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

class ChannelManager(object):
	def __init__(self):
		self.iOSFlavorPath=""
		self.flav=""
		self.tempResults = {}
		self.finalResults = {}
		self.regions = {}

	def processData(self):
		exclusionList=['Ebox', 'ACS', 'Arkwest','Auburn', 'flavors.json', '.DS_Store', 'DirectLink']
		if not self.flav in exclusionList:
			internalConfigPath = "{}/{}/{}-ProductConfig.json".format(self.iOSFlavorPath, self.flav, self.flav)
			p_internalConfigPath = pathlib.Path(internalConfigPath);
		# 	print(repo + '-------------------------------->>>>')
			# print("                  ", p_internalConfigPath.absolute())
			if p_internalConfigPath.exists():
				self.parse_product_config_json(self.flav, internalConfigPath)
			else:
				print("                  ", 'ERROR! config-manager files not available for ' + self.flav)
			self.checkAndCreateFolderOrFile("./jsons-dynamic")
			self.checkAndCreateFolderOrFile("./jsons-dynamic/regions")
			self.checkAndCreateFolderOrFile("./jsons-dynamic/channels")
			
			for flav in self.finalResults:
				for env in self.tempResults[flav]['deployment_environments']:
					print("===========", flav, env)
					self.finalResults[flav]['deployment_environments'] = {}
					self.finalResults[flav]['deployment_environments'][env] = {}
					if self.tempResults[flav]['deployment_environments'][env]['auth_host'] != "" and self.tempResults[flav]['deployment_environments'][env]['host'] != "":
						self.getChannelDatafor(flav, self.tempResults[flav]['vid'], env, self.tempResults[flav]['deployment_environments'][env], 0, 'national')
					with open("./jsons-dynamic/regions/{}_{}_r.json".format(flav, env), "w") as outfile:
						print("")
						print("regions found in accounts")
						print(self.regions)
						if self.regions.get(flav) is not None:
							json.dump(self.regions, outfile, indent=4)
					with open("./jsons-dynamic/channels/{}_{}_c.json".format(flav, env), "w") as outfile:
						if self.finalResults.get(flav) is not None:
							json.dump(self.finalResults, outfile, indent=4)

	def checkAndCreateFolderOrFile(self, filepath, type='folder'):
		if not os.path.exists(filepath):
			os.makedirs(filepath)


	def parse_product_config_json(self, flav, internalConfigPath):
		with open(internalConfigPath) as f:
			data = json.load(f)
			#if data['rules'][0]['value'].get('access_token.lifetime.secs') is not None:
			if data is not None:
				self.finalResults[flav] = {}
				self.tempResults[flav] = {}
				self.regions[flav] = {}
				self.tempResults[flav]['vid'] = {}
				self.tempResults[flav]['vid']['carrier'] = data['vid_carrier']
				self.tempResults[flav]['vid']['product'] = data['vid_product']
				self.tempResults[flav]['vid']['version'] = data['vid_version']
				self.finalResults[flav]['deployment_environments'] = {}
				self.regions[flav]['deployment_environments'] = {}
				self.tempResults[flav]['deployment_environments'] = {}
				for dataEnvironments in data['deployment_environments']:
					if data['deployment_environments'].get(dataEnvironments) is not None:
						# if data['deployment_environments'].get('dev') is not None and data['deployment_environments']['dev'].get('custom_oauth_keys') and data['deployment_environments']['dev']['custom_oauth_keys']['client_id'] != 'FIXME_KEY_NOT_PART_OF_MUST_SPEC':
						# 	self.finalResults[flav]['deployment_environments']['dev'] = data['deployment_environments']['dev']
						# removing FIXME_KEY_NOT_PART_OF_MUST_SPEC check some flavors like Buckeye dont need custom_oauth_keys configured
						# if data['deployment_environments'].get(dataEnvironments) is not None and data['deployment_environments'][dataEnvironments].get('custom_oauth_keys') and data['deployment_environments'][dataEnvironments]['custom_oauth_keys']['client_id'] != 'FIXME_KEY_NOT_PART_OF_MUST_SPEC':
						if data['deployment_environments'].get(dataEnvironments) is not None and data['deployment_environments'][dataEnvironments].get('custom_oauth_keys') and data['deployment_environments'][dataEnvironments]['auth_host'] != 'FixMe' and data['deployment_environments'][dataEnvironments]['host'] != 'FixMe':
							self.tempResults[flav]['deployment_environments'][dataEnvironments] = data['deployment_environments'][dataEnvironments]
							self.finalResults[flav]['deployment_environments'][dataEnvironments] = {}
							self.regions[flav]['deployment_environments'][dataEnvironments] = {}

	def getChannelDatafor(self, flav, vid, envname, envdetails, offset, regions):
		self.getChannelsData(flav, vid, envname, envdetails, offset, regions)
		if self.finalResults[flav]['deployment_environments'][envname].get('hits') is not None:
			total = self.finalResults[flav]['deployment_environments'][envname]['total']
			hits = self.finalResults[flav]['deployment_environments'][envname]['hits']
			print(flav, "total =", total, "hits =", len(hits))
			if total > len(hits):
				self.getChannelDatafor(flav, vid, envname, envdetails, len(hits), regions)


	def getChannelsUrl(self, flav, vid, envname, envdetails, offset, regions):
		return "https://{}/guide/v5.2/search/{}/{}/{}/search/shared/details.json?offset={}&ref_types=channel&sort_by=channel_number&sort_direction=asc".format(envdetails['auth_host'], vid['carrier'], vid['product'], vid['version'], offset, regions)


	def getChannelsData(self, flav, vid, envname, envdetails, offset, regions):
		print("---------------->>>")
		url = self.getChannelsUrl(flav, vid, envname, envdetails, offset, regions)
		print("getChannelsData", url)

		try:
			session = requests.session()
			session.mount('https://', TLSAdapter())
			response = session.get(
				url=url,
				headers={
					"Content-Type": "application/json; charset=utf-8",
				},
				timeout=20
			)
			jsonResponse = response.json()

			dt = datetime.now()
			if jsonResponse.get('total') is not None:
				if jsonResponse.get('hits') is not None:
					for hitsData in jsonResponse.get('hits'):
						if hitsData["result"] is not None:
							if hitsData["result"]["channel"] is not None:
								if hitsData["result"]["channel"]["regions"] is not None:
									if self.regions[flav]['deployment_environments'][envname].get('regions') is None:
										self.regions[flav]['deployment_environments'][envname]['regions'] = []
									for region in hitsData["result"]["channel"]["regions"]:
										if (region in self.regions[flav]['deployment_environments'][envname]['regions']) == False:
											self.regions[flav]['deployment_environments'][envname]['regions'].append(region)
					if self.finalResults[flav]['deployment_environments'][envname].get('hits') is None:
						self.finalResults[flav]['deployment_environments'][envname] = jsonResponse
					else:
						self.finalResults[flav]['deployment_environments'][envname]['hits'].extend(jsonResponse['hits'])
				else:
					print(flav, "total=", jsonResponse['total'])
			if jsonResponse.get('hits') is None:
				print(flav, envname)
				# print('HTTP {} -> Body: {}'.format(response.status_code, jsonResponse))
			# self.finalResults[flav]['deployment_environments'][envname]['results'][user]['idam']['time_readable'] = dt_string

		except HTTPError as http_err:
			print('HTTP error occurred: {http_err}')
		except Exception as err:
			print('Other error occurred: {err}')


# curl -i -H  -H "x-mobitv-profile-id: 7931cd70-706d-4e50-ad85-1d7d0d2ce0ed" -H "x-mobitv-operator: forsythcablenet" -H "x-mobitv-app-version: 1.29.0.13" -H "x-mobitv-sid: 078BD76E-6D8C-4D7E-88F9-0B6D8CA35016" -H "x-mobitv-device-id: 8118D7CB-B93C-4376-86CB-63A924D06682" -H "User-Agent: Mozilla/5.0 (iOS; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B91" "https://data-production.forsythcable.com/core/v5/session/forsythcablenet/paytv/1.0/current/profile.json"
# curl -i -H "x-mobitv-operator: forsythcablenet" -H "x-mobitv-sid: 078BD76E-6D8C-4D7E-88F9-0B6D8CA35016" -H "x-mobitv-profile-id: 7931cd70-706d-4e50-ad85-1d7d0d2ce0ed" -H "x-mobitv-device-id: 8118D7CB-B93C-4376-86CB-63A924D06682" -H "User-Agent: Mozilla/5.0 (iOS; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B91" -H "Authorization: Bearer {AccessToken}" -H "x-mobitv-app-version: 1.29.0.13" "https://data-production.forsythcable.com/core/v5/purchase/forsythcablenet/paytv/1.0/7931cd70-706d-4e50-ad85-1d7d0d2ce0ed/purchases.json?expired_purchases=include"

# config file path can be given as -c "path" or --config "path"
def main(argv):
	iOSFlavorPath = "/flavors"
	# iOSFlavorPath = "/Volumes/DriveA/code/MobiTV/mobi-client-connect-ios-swift5/MobiConnect/MobiConnect/Flavors"
	flav = ""

	try:
	 	opts, args = getopt.getopt(argv, "flav",["flav="])
	except getopt.GetoptError as err:
	 	print(err)
	 	sys.exit()
	for opt, arg in opts:

		# if opt in ("-f", "--flavorspath"):
			# iOSFlavorPath = arg
		if opt in ("-flav", "--flav"):
			flav = arg

	if not isdir(iOSFlavorPath):
		print("Please provide flavors path -f where ios is cloned", iOSFlavorPath)
		sys.exit()

	print("iOSFlavorPath", iOSFlavorPath)

	starttime = datetime.now()
	accManager = ChannelManager()
	accManager.iOSFlavorPath = iOSFlavorPath
	accManager.flav = flav
	accManager.processData()
	endTime =datetime.now()
	print("Completed {} in".format(flav), str((endTime - starttime).total_seconds())+"s")

if __name__ == "__main__":
	main(sys.argv[1:])
