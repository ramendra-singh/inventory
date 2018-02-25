from flask import Flask, render_template, json, request, url_for, send_from_directory
from flask import jsonify
from flask_mysqldb import MySQL
import os, datetime, paramiko, sys
from time import sleep
from subprocess import PIPE, Popen
from shutil import copyfile
import logging

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.url_map.strict_slashes = False
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)



logger = logging.getLogger('TEST AUTO')
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)

custom_cloud_list = ['custom', 'custom2.0', 'centurylink', 'oracle', 'gcp']

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
                        log_link = "<a href=\""+ row['Log Link'] + "\" target=\"_blank\">Log Link</a>"
                        data = log_link
                    elif self.columns[i] == 'Id':
                        task_id = str(row['Id'])
                        data = '<input type=\"radio\" name=\"id\" value=' + task_id + '></input>'
                    else:
                        data = str(row[ self.columns[i] ]).replace('"','\\"')
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
    print "Running command : " + command
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()


@app.route('/_server_data')
def get_server_data():
    columns = [ 'Id', 'Cloud', 'Host', 'User', 'Tclevel', 'Tctype']
    cur = mysql.connection.cursor()
    cur.execute('''SELECT TaskID,CloudType,Host,User,tclevel,tctype from Task_History order by TaskID desc''')
    rv = cur.fetchall()
    cur.close()

    collection = []

    for i in range(len(rv)):
        _item = dict(zip(columns, rv[i]))
        collection.append(_item)

    results = BaseDataTables(request, columns, collection).output_result()

    # return the results as a string for the datatable
    return json.dumps(results)


@app.route('/')
def main():
	columns = ['Select', 'Ip', 'Name', 'Status', 'Up Time',
			   'CPU', 'Memory', 'VCenter', 'Type']

	try:
		cur = mysql.connection.cursor()
		count_stmt1 = (
			"select count(*) as Status from inventory where status= %s"
		)
		data1 = ('poweredOn',)

		cur.execute(count_stmt1, data1)
		rv1 = cur.fetchall()

		count_stmt2 = (
			"select count(*) as Status from inventory where status= %s"
		)
		data2 = ('poweredOff',)

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

	return render_template('dashboard.html', columns=columns, sample_data=d)


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
			"select count(*) as Status from inventory where status= %s"
		)
		data2 = ('poweredOff',)

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
		return json.dumps({'html': '<span>Error While Fetching the History.</span>'})
	finally:
		cur.close()

	return render_template('dashboard.html', columns=columns, sample_data=d)

@app.route('/deleteData',methods=['POST','GET'])
def delete_task_data():
    task_id = request.form['task_id']
    try:
        cur = mysql.connection.cursor()
        delete_stmt = (
          "DELETE from task_status where id = %s"
        )
        data = (task_id,)
        cur.execute(delete_stmt, data)
        mysql.connection.commit()

    except Exception as e:
        return json.dumps({'html':'<span>Error while deleting record.</span>'})
    finally:
        cur.close()

    return json.dumps({'html':'<span>Successfully Deleted Record.</span>'})

@app.route('/deleteProcess',methods=['POST','GET'])
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
        cmd = 'python shutdown_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + _ids
        output = cmdline(cmd)
        print output[0]

    except Exception as e:
        msg = 'Error while powering off vm.CMD : [%s]' % (cmd)
        return json.dumps({'html':msg,'result':'failure'})
    finally:
        cur.close()

    return json.dumps({'html':output[0]})

@app.route('/poweron',methods=['POST','GET'])
def poweron_vm():
    task_id = request.form['task_id']
    cmd = 'python poweronvm.py '
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
        cmd = 'python poweron_vm.py  -s ' + vcenter + ' -u ' \
			  + vcenter_user + ' -p \"' + vcenter_password + '\" -v ' + _ids
        output = cmdline(cmd)
        print output[0]

    except Exception as e:
        msg = 'Error while powering on vm.CMD : [%s]' % (cmd)
        return json.dumps({'html':msg,'result':'failure'})
    finally:
        cur.close()

    return json.dumps({'html':output[0]})

@app.route('/refresh',methods=['POST','GET'])
def refresh_inventory():
    cmd = 'python getall_vm.py '
    vcenter = ''
    vcenter_user = ''
    vcenter_password = ''
    try:
        cur = mysql.connection.cursor()

        delete_stmt = ("Truncate table inventory")
        cur.execute(delete_stmt)
        mysql.connection.commit()

        # Read the file and Insert the record
        f = open('data.txt','r')
        data = f.read()
        data = json.loads(data)
        for _data in data['aaData']:
			insert_stmt = (
				"INSERT INTO inventory (id,name,ip,memory,"
				"cpu,vcenter,vcenter_user,vcenter_password,status,uptime,"
				"vm_type) "
				"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			)
			data = tuple(_data)
			cur.execute(insert_stmt, data)
			mysql.connection.commit()

    except Exception as e:
        msg = 'Error while getting vms list.CMD : [%s]' % (cmd)
        return json.dumps({'html':msg,'result':'failure'})
    finally:
        cur.close()

    return json.dumps({'html':'Successfully Refreshed Inventory'})

@app.route('/_task_data')
def get_task_data():
    columns = [ 'Id', 'Ip', 'Name', 'Status', 'Up Time', 'CPU', 'Memory',
			   'VCenter', 'Type' ]
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


@app.route('/deleteConfig',methods=['POST','GET'])
def delete_config_data():
    task_id = request.form['task_id']
    try:
        cur = mysql.connection.cursor()
        delete_stmt = (
          "DELETE from Task_History where TaskID = %s"
        )
        data = (task_id,)
        cur.execute(delete_stmt, data)
        mysql.connection.commit()

    except Exception as e:
        return json.dumps({'html':'<span>Error while deleting record.</span>'})
    finally:
        cur.close()

    return json.dumps({'html':'<span>Successfully Deleted Record.</span>'})

if __name__ == "__main__":
    app.run(port=5002,debug=True)
