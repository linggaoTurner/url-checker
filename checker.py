from flask import Flask, jsonify, request, abort, session, flash,redirect,render_template,url_for
from functools import wraps
from flask_restful import Resource, Api
from models import admin, urlLog, urlInventory
import requests
from queue import Queue
import threading
from multiprocessing import Process, Queue
import sendEmail

app = Flask(__name__)
api = Api(app, prefix="/api/v1")
app.secret_key = 'r*s^a!vtz_7y/d8x)y&*#o$inn$381dzqqyzycshv(b8n(bd+g'

def askFor_APIKey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        keys = admin.select(admin.apikey)
        if request.args.get('api') and request.args.get('api') in keys:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


class urlInventory(Resource):
    #Get urls info from database
    @askFor_APIKey
    def get(self):
        if urlInventory.select().count() > 0:
            for data in urlInventory.select():
                result = {}
                result['urlName'] = data.urlName
                result['urlDomain'] = data.urlDomain
                result['frequency'] = data.frequency
                result['expectedStatus'] = data.expectedStatus
                result['expectedString'] = data.expectedString
        return jsonify(result)

    #Post new url info from database
    @askFor_APIKey
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('urlName', type=str, required=True, location='json')
        parser.add_argument('urlDomain', type=str, required=True, location='json')
        parser.add_argument('frequency', type=str, required=True, location='json')
        parser.add_argument('expectedStatus', type=str, required=True, location='json')
        parser.add_argument('expectedString', type=str, required=False, location='json')

        args = parser.parse_args(strict=True)
        url = {'urlName': args['urlName'],
                'urlDomain': args['urlDomain'],
                'frequency': args['frequency'],
                'expectedStatus': args['expectedStatus'],
                'expectedString': args['expectedString']}

        if urlInventory.select().where(urlInventory.urlDomain==url['urlDomain']).count()==0:
            urlInventory.create(urlName = url['urlName'],urlDomain = url['urlDomain'],frequency=url['frequency'],expectedStatus=url['expectedStatus'],expectedString=url['expectedString'])
        else:
            return jsonify({'success': False,'error':'Existed URL'})
        return jsonify(url)

@auth.error_handler
def unauthorized():
    return jsonify({'success': False,'error': 'Unauthorized access'}), 401

#index page
@app.route('/')
def index():
    session.pop('key', None)
    return render_template('index.html')

#login
@app.route('/login',methods=['POST'])
def login():

    if request.method == 'POST':
        data = dict()
        for item in request.form:
            data[item] = request.form[item]

        if admin.select().where(admin.userName==data['username']).count() == 1:
            if admin.select().where(admin.userName==data['username']).get().userPassword == data['password']:
                session['key'] = admin.select().where(admin.userName==data['username']).get().apikey
                return redirect(url_for('admin'))
            else:
                return jsonify({'success': False,'error': 'Invalid password'})
        else:
            return jsonify({'success': False,'error': 'Invalid username'})
    return

#admin page
@app.route('/admin')
def admin():
    if 'key' in session:
        session.pop('domain', None)
        dataset = []
        if urlLog.select().count() > 0:
            for data in urlLog.select():
                result = {}
                result['urlDomain'] = data.urlDomain
                result['timeChecked'] = data.timeChecked
                result['healthyState'] = data.healthyState
                dataset.append(result)
        return render_template('admin.html',dataset=dataset)
    return jsonify({'success': False,'error': 'Please log in'})

#search Domain
@app.route('/searchDomain',methods=['POST'])
def searchDomain():
    if request.method == 'POST':
        session.pop('domain', None)
        domain = request.form['name']
        if urlInventory.select().where(urlInventory.urlName==domain).count() == 1:
            session['domain'] = domain
            return jsonify({'success': True, 'Url domain': session['domain']})
        else:
            return jsonify({'success': False, 'error': 'Invalid domain'})
    return

#logs page
@app.route('/logs',methods=['POST'])
def logs():
    if 'key' in session:
        if 'domain' in session:
            dataset = []
            if urlLog.select().count() > 0:
                for data in urlLog.select():
                    result = {}
                    result['urlDomain'] = data.urlDomain
                    result['timeChecked'] = data.timeChecked
                    result['healthyState'] = data.healthyState
                    dataset.append(result)
            return render_template('logs.html',dataset=dataset)
        return jsonify({'success': False, 'error': 'Please search domain name'})
    return jsonify({'success': False, 'error': 'Please log in'})

api.add_resource(url_inventory, '/urlInventory')




if __name__ == '__main__':
    models.init_db()
    startTimer()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
