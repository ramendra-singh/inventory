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
import json , re

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
	parser.add_argument('-f', '--filename', required=False, action='store',
						help='Filename to store data')
	parser.add_argument('-r', '--pattern', required=False, action='store',
						help='Pattern to Match vm/app-template')
	args = parser.parse_args()
	return args


def PrintVmInfo(vm, host,user,password,pattern, depth=1):
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
			PrintVmInfo(c, host,user,password,pattern,depth + 1)
		return

	# if this is a vApp, it likely contains child VMs
	# (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
	if isinstance(vm, vim.VirtualApp):
		vmList = vm.vm
		for c in vmList:
			PrintVmInfo(c, host,user,password,pattern,depth + 1)
		return

	summary = vm.summary
	boot_time = str(vm.runtime.bootTime).split()
	if boot_time:
		uptime = boot_time[0]
	else:
		uptime = ''

	try:
		hostname = vm.runtime.host.name
	except:
		hostname = ''

	details = {'Name': vm.summary.config.name,
			   'Instance UUID': vm.summary.config.instanceUuid,
			   'Bios UUID': vm.summary.config.uuid,
			   'Path to VM': vm.summary.config.vmPathName,
			   'Guest OS id': vm.summary.config.guestId,
			   'Guest OS name': vm.summary.config.guestFullName,
			   'Host Name': hostname,
			   'Last booted timestamp': uptime,
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
				  uptime,vm_type]

	if pattern:
		pattern_list = pattern.split(',')
		print ('Matching the pattern [%s] in %s' % (vm.summary.config.name,
													  pattern_list))
		for _pattern in pattern_list:
			if re.search( _pattern, vm.summary.config.name, re.IGNORECASE):
				print ("Found a Match")
				print(array_item)
				vm_list.append(array_item)
	else:
		print (array_item)
		vm_list.append(array_item)


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

	if args.filename:
		fname = args.filename
	else:
		fname = 'data.txt'

	if args.pattern:
		pattern = args.pattern
	else:
		pattern = ''

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
				PrintVmInfo(vm,args.host,args.user,password,pattern)

	with open(fname, 'w') as outfile:
		outfile.write("{ \"aaData\":")
		json.dump(vm_list, outfile)
		outfile.write("}")
		outfile.close()

	print ("END")
	return 0


# Start program
if __name__ == "__main__":
	main()
