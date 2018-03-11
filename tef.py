from flask import Flask, render_template, json, request

from flask_mysqldb import MySQL
import os, sys, time
from subprocess import PIPE, Popen
import logging
import random
import glob
from logging.handlers import RotatingFileHandler
from shutil import copyfile

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.url_map.strict_slashes = False
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'
app.config['MYSQL_HOST'] = 'localhost'
app.config['cron_location'] = '/var/spool/cron/root'
app.config['app_location'] = '/app'
app.config['app_log_location'] = '/var/log/inventory'
app.config['theme'] = os.environ['logo']
mysql.init_app(app)

logger = logging.getLogger('inventory')
logger.setLevel(logging.DEBUG)
format = logging.Formatter(
	"%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)


class BaseDataTables:
	def __init__(self, request, columns, collection):

		self.columns = columns
		self.collection = collection

		# values specified by the datatable for filtering, sorting, paging
		self.request_values = request.values

		# results from the db
		self.result_data = None

		# total in the table after filtering
		self.cardinality_filtered = 0

		# total in the table unfiltered
		self.cadinality = 0

		self.run_queries()

	def output_result(self):

		output = {}
		aaData_rows = []

		for row in self.result_data:
			aaData_row = []
			data = ''
			for i in range(len(self.columns)):
				try:
					if self.columns[i] == 'Log Link':
						log_link = "<a href=\"" + row[
							'Log Link'] + "\" target=\"_blank\">Log Link</a>"
						data = log_link
					elif self.columns[i] == 'Id':
						task_id = str(row['Id'])
						data = '<input type=\"radio\" name=\"id\" value=' + \
							   task_id + '></input>'
					else:
						data = str(row[self.columns[i]]).replace('"', '\\"')
				except Exception as e:
					print e

				aaData_row.append(data)
			aaData_rows.append(aaData_row)

		output['aaData'] = aaData_rows

		return output

	def run_queries(self):

		self.result_data = self.collection
		self.cardinality_filtered = len(self.result_data)
		self.cardinality = len(self.result_data)


def cmdline(command):
	app.logger.info("Running command : " + command)
	process = Popen(
		args=command,
		stdout=PIPE,
		shell=True
	)
	app.logger.info(process.communicate()[0])
	return process.communicate()[0]


@app.route('/')
def main():
	columns = ['Select', 'Ip', 'Name', 'Status', 'Up Time',
			   'CPU', 'Memory', 'VCenter', 'Type']
	cur = None
	try:
		cur = mysql.connection.cursor()
		count_stmt1 = (
			"select count(*) as Status from inventory where status= %s"
		)
		data1 = ('poweredOn',)

		cur.execute(count_stmt1, data1)
		rv1 = cur.fetchall()

		count_stmt2 = (
			"select count(*) as Status from inventory where status= %s and "
			"vm_type != %s"
		)
		data2 = ('poweredOff', 'template',)

		cur.execute(count_stmt2, data2)
		rv2 = cur.fetchall()

		count_stmt3 = (
			"select count(*) as AppTemplate from inventory where vm_type= %s"
		)
		data3 = ('template',)

		cur.execute(count_stmt3, data3)
		rv3 = cur.fetchall()

		d = {}
		d['On'] = rv1[0][0]
		d['Off'] = rv2[0][0]
		d['AppTemplate'] = rv3[0][0]

		mysql.connection.commit()

	except Exception as e:
		return json.dumps(
			{'html': '<span>Error While Fetching the History.</span>'})

	finally:
		cur.close()

	return render_template('dashboard.html', columns=columns, sample_data=d,
						   theme=app.config['theme'])


@app.route('/dashboard')
def showDashboard():
	columns = ['Select', 'Ip', 'Name', 'Status', 'Up Time', 'CPU', 'Memory',
			   'VCenter', 'Type']

	try:
		cur = mysql.connection.cursor()
		count_stmt1 = (
			"select count(*) as Status from inventory where status= %s"
		)
		data1 = ('poweredOn',)

		cur.execute(count_stmt1, data1)
		rv1 = cur.fetchall()

		count_stmt2 = (
			"select count(*) as Status from inventory where status= %s and "
			"vm_type != %s"
		)
		data2 = ('poweredOff', 'template')

		cur.execute(count_stmt2, data2)
		rv2 = cur.fetchall()

		count_stmt3 = (
			"select count(*) as AppTemplate from inventory where vm_type= %s"
		)
		data3 = ('template',)

		cur.execute(count_stmt3, data3)
		rv3 = cur.fetchall()

		d = {}
		d['On'] = rv1[0][0]
		d['Off'] = rv2[0][0]
		d['AppTemplate'] = rv3[0][0]

		mysql.connection.commit()

	except Exception as e:
		return json.dumps(
			{'html': '<span>Error While Fetching the History.</span>'})
	finally:
		cur.close()

	return render_template('dashboard.html', columns=columns, sample_data=d,
						   theme=app.config['theme'])


@app.route('/settings')
def showSettings():
	columns = ['Select', 'Host', 'User', 'Password', 'Pattern']
	return render_template('settings.html', columns=columns,
						   theme=app.config['theme'])


@app.route('/store')
def showStore():
	columns = ['#', 'Host', 'User', 'Password', 'Key']
	return render_template('store.html', columns=columns,
						   theme=app.config['theme'])

@app.route('/_server_data')
def get_server_data():
	columns = ['Id', 'Host', 'User', 'Password', 'Pattern']
	cur = mysql.connection.cursor()
	cur.execute(
		'''SELECT id,host,user,password,pattern from inventory_credential''')
	rv = cur.fetchall()
	cur.close()

	collection = []

	for i in range(len(rv)):
		_item = dict(zip(columns, rv[i]))
		collection.append(_item)

	results = BaseDataTables(request, columns, collection).output_result()

	# return the results as a string for the datatable
	return json.dumps(results)


@app.route('/_store_data')
def get_store_data():
	columns = ['#', 'Host', 'User', 'Password', 'Key']
	cur = mysql.connection.cursor()
	cur.execute(
		'''SELECT id,host,user,password,hostkey from host_credential''')
	rv = cur.fetchall()
	cur.close()

	collection = []

	for i in range(len(rv)):
		_item = dict(zip(columns, rv[i]))
		collection.append(_item)

	results = BaseDataTables(request, columns, collection).output_result()

	# return the results as a string for the datatable
	return json.dumps(results)


@app.route('/deleteData', methods=['POST', 'GET'])
def delete_task_data():
	task_id = request.form['task_id']
	cmd = 'python ./scripts/destroy_vm.py '
	vcenter = ''
	vcenter_user = ''
	vcenter_password = ''
	try:

		cur = mysql.connection.cursor()
		select_stmt = (
			"SELECT id,vcenter,vcenter_user,vcenter_password from inventory "
			"where id = %s"
		)
		data = (task_id,)
		cur.execute(select_stmt, data)
		rv = cur.fetchall()
		data = rv[0]
		vcenter = data[1]
		vcenter_user = data[2]
		vcenter_password = data[3]

		cmd = 'python ./scripts/shutdown_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + task_id
		output = cmdline(cmd)
		print output[0]
		app.logger.info("Command Running On System :")
		app.logger.info("==========================")
		app.logger.info(cmd)
		app.logger.info("==========================")
		app.logger.info("Output:")
		app.logger.info(output[0])

		cmd = 'python ./scripts/destroy_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + task_id
		output = cmdline(cmd)
		print output[0]
		app.logger.info("Command Running On System :")
		app.logger.info("==========================")
		app.logger.info(cmd)
		app.logger.info("==========================")
		app.logger.info("Output:")
		app.logger.info(output[0])

		retrun_output = output[0]

		if retrun_output != -1:
			delete_stmt = (
				"DELETE from inventory where id = %s"
			)
			data = (task_id,)
			cur.execute(delete_stmt, data)
			mysql.connection.commit()

	except Exception as e:
		return json.dumps({'html': '<span>Error while deleting vm.</span>'})
	finally:
		cur.close()

	return json.dumps({'html': output[0]})


@app.route('/deleteProcess', methods=['POST', 'GET'])
def delete_trun_process():
	task_id = request.form['task_id']
	cmd = 'python shutdown_vm.py '
	vcenter = ''
	vcenter_user = ''
	vcenter_password = ''
	try:
		cur = mysql.connection.cursor()
		select_stmt = (
			"SELECT id,vcenter,vcenter_user,vcenter_password from inventory "
			"where id = %s"
		)
		data = (task_id,)
		cur.execute(select_stmt, data)
		rv = cur.fetchall()
		data = rv[0]
		vcenter = data[1]
		vcenter_user = data[2]
		vcenter_password = data[3]
		_ids = data[0].strip('\n')
		cmd = 'python ./scripts/shutdown_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + _ids
		output = cmdline(cmd)
		print output[0]
		app.logger.info("Command Running On System :")
		app.logger.info("==========================")
		app.logger.info(cmd)
		app.logger.info("==========================")
		app.logger.info("Output:")
		app.logger.info(output[0])

	except Exception as e:
		msg = 'Error while powering off vm.CMD : [%s]' % (cmd)
		return json.dumps({'html': msg, 'result': 'failure'})
	finally:
		cur.close()

	return json.dumps({'html': output[0]})


@app.route('/poweron', methods=['POST', 'GET'])
def poweron_vm():
	task_id = request.form['task_id']
	cmd = 'python ./scripts/poweronvm.py '
	vcenter = ''
	vcenter_user = ''
	vcenter_password = ''
	try:
		cur = mysql.connection.cursor()
		select_stmt = (
			"SELECT id,vcenter,vcenter_user,vcenter_password from inventory "
			"where id = %s"
		)
		data = (task_id,)
		cur.execute(select_stmt, data)
		rv = cur.fetchall()
		data = rv[0]
		vcenter = data[1]
		vcenter_user = data[2]
		vcenter_password = data[3]
		_ids = data[0].strip('\n')
		cmd = 'python ./scripts/poweron_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + _ids
		output = cmdline(cmd)
		print output[0]
		app.logger.info("Command Running On System :")
		app.logger.info("==========================")
		app.logger.info(cmd)
		app.logger.info("==========================")
		app.logger.info("Output:")
		app.logger.info(output[0])

	except Exception as e:
		msg = 'Error while powering on vm.CMD : [%s]' % (cmd)
		return json.dumps({'html': msg, 'result': 'failure'})
	finally:
		cur.close()

	return json.dumps({'html': output[0]})


@app.route('/refresh', methods=['POST', 'GET'])
def refresh_inventory():
	cmd = 'python ./scripts/getall_vm.py '
	vcenter = ''
	vcenter_user = ''
	vcenter_password = ''
	app.logger.info("Refresh Inventory -> Start")
	try:
		cur = mysql.connection.cursor()

		delete_stmt = ("Truncate table inventory")
		cur.execute(delete_stmt)
		mysql.connection.commit()

		path = app.config['app_log_location'] + "/data*.txt"
		file_list = glob.glob(path)
		app.logger.info("File List : = ")
		app.logger.info(file_list)
		# file_list = ['data.txt', 'data1.txt']
		for fname in file_list:
			# Read the file and Insert the record
			if os.path.isfile(fname):
				f = open(fname, 'r')
				if os.stat(fname).st_size != 0:
					data = f.read()
					data = json.loads(data)
					for _data in data['aaData']:
						insert_stmt = (
							"INSERT INTO inventory (id,name,ip,memory,"
							"cpu,vcenter,vcenter_user,vcenter_password,status,"
							"uptime,"
							"vm_type) "
							"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						)
						data = tuple(_data)
						cur.execute(insert_stmt, data)
						mysql.connection.commit()

	except Exception as e:
		msg = 'Error while getting vms list.CMD : [%s]' % (cmd)
		return json.dumps({'html': msg, 'result': 'failure'})
	finally:
		cur.close()

	app.logger.info("Refresh Inventory -> End")
	return json.dumps({'html': 'Successfully Refreshed Inventory'})


@app.route('/_task_data')
def get_task_data():
	columns = ['Id', 'Ip', 'Name', 'Status', 'Up Time', 'CPU', 'Memory',
			   'VCenter', 'Type']
	cur = mysql.connection.cursor()
	cur.execute('''SELECT id,ip,name,status,uptime,cpu
                        , memory, vcenter, vm_type from inventory
                        ''')
	rv = cur.fetchall()
	cur.close()

	collection = []

	for i in range(len(rv)):
		_item = dict(zip(columns, rv[i]))
		collection.append(_item)

	results = BaseDataTables(request, columns, collection).output_result()

	# return the results as a string for the datatable
	return json.dumps(results)


@app.route('/addCronJob', methods=['POST', 'GET'])
def addCronJob():
	_host = request.form['host_ip']
	_user = request.form['host_user']
	_passwd = request.form['host_password']
	_pattern = request.form['pattern']
	if _pattern:
		_pattern_str = ' -r ' + _pattern
	else:
		_pattern_str = ' '
	app.logger.info(_host)
	random_no = random.randint(1, 101)
	random_file = 'data_' + str(random_no) + ".txt"
	cron_script = app.config['app_log_location'] + '/cron_' + str(random_no)\
				  + \
				  ".sh"
	vm_log = 'getall_vm_' + str(random_no) + ".log"

	script_content = 'python ' + app.config[
		'app_location'] + '/scripts/getall_vm.py -s ' + _host + ' \
		-u ' + _user + ' -p ' + "\"" + _passwd + "\"" + ' -f ' + app.config[
						 'app_log_location'] + '/' + random_file + \
					 _pattern_str + \
					 ' > ' \
					 '' \
					 + \
					 app.config['app_log_location'] + '/' + vm_log + ' 2>&1'

	script_content = ' '.join(script_content.split())

	try:
		script_file = open(cron_script, 'w')
		script_file.write(script_content)
		script_file.write("\n")
		script_file.close()
	except Exception as e:
		app.logger.info(e)
		return json.dumps(
			{'html': '<span>Error while storing script '
					 'information.</span>'})

	cron_entry = '0 */2 * * * /usr/bin/bash ' + cron_script
	cron_entry = ' '.join(cron_entry.split())
	try:
		app.logger.info(cron_entry)
		cron_file = open('crontab', 'a')
		cron_file.write(cron_entry)
		cron_file.write("\n")
		cron_file.close()
	except Exception as e:
		app.logger.info(e)
		return json.dumps(
			{'html': '<span>Error while storing cron '
					 'information.</span>'})

	try:
		copyfile(app.config['app_location'] + '/crontab',
				 app.config['cron_location'])
		os.chmod(cron_script, 0755)
	except Exception as e:
		app.logger.info(e)
		return json.dumps(
			{'html': '<span>Error while copying cron '
					 'information.</span>'})

	try:
		cur = mysql.connection.cursor()
		insert_stmt = (
			"INSERT INTO inventory_credential (host,user,password,pattern) "
			"VALUES (%s,%s,%s,%s)"
		)
		data = (_host, _user, _passwd, _pattern)
		cur.execute(insert_stmt, data)
		mysql.connection.commit()
	except Exception as e:
		app.logger.info(e)
		return json.dumps(
			{'html': '<span>Error while adding cloud  '
					 'information in table.</span>'})

	return json.dumps({'html': '<span>Cron Set Successfully.</span>'})


@app.route('/addHost', methods=['POST', 'GET'])
def addHost():
	_host = request.form['host_ip']
	_user = request.form['host_user']
	_passwd = request.form['host_password']
	_key = request.form['host_key']

	try:
		cur = mysql.connection.cursor()
		insert_stmt = (
			"INSERT INTO host_credential (host,user,password,hostkey) "
			"VALUES (%s,%s,%s,%s)"
		)
		data = (_host, _user, _passwd, _key)
		cur.execute(insert_stmt, data)
		mysql.connection.commit()
	except Exception as e:
		app.logger.info(e)
		return json.dumps(
			{'html': '<span>Error while adding cloud  '
					 'information in table.</span>'})

	return json.dumps({'html': '<span>Information Stored Successfully.</span>'})


if __name__ == "__main__":
	logHandler = RotatingFileHandler(app.config['app_log_location'] +
									 '/inventory.log', backupCount=1)
	# set the log handler level
	logHandler.setLevel(logging.INFO)
	# set the app logger level
	app.logger.setLevel(logging.INFO)
	app.logger.addHandler(logHandler)
	app.run(port=5002, debug=True, host='0.0.0.0')
