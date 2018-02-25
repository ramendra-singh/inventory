#!/usr/bin/env python

"""
Python program for listing the vms on an ESX / vCenter host
"""

from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl
import json

vm_list = []

def GetArgs():
	"""
	Supports the command-line arguments listed below.
	"""
	parser = argparse.ArgumentParser(
		description='Process args for retrieving all the Virtual Machines')
	parser.add_argument('-s', '--host', required=True, action='store',
						help='Remote host to connect to')
	parser.add_argument('-o', '--port', type=int, default=443, action='store',
						help='Port to connect on')
	parser.add_argument('-u', '--user', required=True, action='store',
						help='User name to use when connecting to host')
	parser.add_argument('-p', '--password', required=False, action='store',
						help='Password to use when connecting to host')
	args = parser.parse_args()
	return args


def PrintVmInfo(vm, host,user,password, depth=1):
	"""
	Print information for a particular virtual machine or recurse into a folder
	or vApp with depth protection
	"""
	maxdepth = 10

	# if this is a group it will have children. if it does, recurse into them
	# and then return
	if hasattr(vm, 'childEntity'):
		if depth > maxdepth:
			return
		vmList = vm.childEntity
		for c in vmList:
			PrintVmInfo(c, host,user,password,depth + 1)
		return

	# if this is a vApp, it likely contains child VMs
	# (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
	if isinstance(vm, vim.VirtualApp):
		vmList = vm.vm
		for c in vmList:
			PrintVmInfo(c, host,user,password,depth + 1)
		return

	summary = vm.summary

	details = {'Name': vm.summary.config.name,
			   'Instance UUID': vm.summary.config.instanceUuid,
			   'Bios UUID': vm.summary.config.uuid,
			   'Path to VM': vm.summary.config.vmPathName,
			   'Guest OS id': vm.summary.config.guestId,
			   'Guest OS name': vm.summary.config.guestFullName,
			   'Host Name': vm.runtime.host.name,
			   'Last booted timestamp': str(vm.runtime.bootTime),
			   'Cpu':vm.summary.config.numCpu,
			   'Memory':vm.summary.config.memorySizeMB,
			   'State':vm.summary.runtime.powerState}

	vm_type = ''
	if vm.config.template:
		vm_type = 'template'
	else:
		vm_type = 'vm'

	annotation = summary.config.annotation
	if annotation != None and annotation != "":
		print("Annotation : ", annotation)

	if summary.guest != None:
		ip = summary.guest.ipAddress
		if ip != None and ip != "":
			details['IP'] = ip
		else:
			details['IP'] = ''
			ip = ''

	array_item = [vm.summary.config.name,vm.summary.config.name,
				  vm.summary.guest.ipAddress,vm.summary.config.memorySizeMB,
				  vm.summary.config.numCpu,host,
				  user,password,vm.summary.runtime.powerState,
				  str(vm.runtime.bootTime),vm_type]
	print (array_item)
	vm_list.append(array_item)
	'''
	if summary.runtime.question != None:
		print("Question  : ", summary.runtime.question.text)
	print("")
	'''

def main():
	"""
	Simple command-line program for listing the virtual machines on a system.
	"""

	args = GetArgs()
	if args.password:
		password = args.password
	else:
		password = getpass.getpass(prompt='Enter password for host %s and '
										  'user %s: ' % (args.host, args.user))

	context = None
	if hasattr(ssl, '_create_unverified_context'):
		context = ssl._create_unverified_context()
	si = SmartConnect(host=args.host,
					  user=args.user,
					  pwd=password,
					  port=int(args.port),
					  sslContext=context,
					  connectionPoolTimeout=900)
	if not si:
		print("Could not connect to the specified host using specified "
			  "username and password")
		return -1

	atexit.register(Disconnect, si)

	content = si.RetrieveContent()
	for child in content.rootFolder.childEntity:
		if hasattr(child, 'vmFolder'):
			datacenter = child
			vmFolder = datacenter.vmFolder
			vmList = vmFolder.childEntity
			count = 0
			for vm in vmList:
				PrintVmInfo(vm,args.host,args.user,password)
				'''
				count = count + 1
				if count == 5:
					break
				'''


	with open('data.txt', 'w') as outfile:
		outfile.write("{ \"aaData\":")
		json.dump(vm_list, outfile)
		outfile.write("}")
		outfile.close()

	return 0

	'''

	for _vm in vm_list:
		for name, value in _vm.items():
			print(
				u"  {0:{width}{base}}: {1}".format(name, value, width=25,
												   base='s'))
			print ("")
	return 0
	'''


# Start program
if __name__ == "__main__":
	main()
