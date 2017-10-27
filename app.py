from flask import Flask, jsonify, request, abort, session, flash,redirect,render_template,url_for
from functools import wraps
from flask_restful import Resource, Api
from models import users, urlLog, urlInventory
import requests
import sendEmail
import os
import checker

app = Flask(__name__)
app.secret_key = 'f81f7b9f-0fe6-40ed-9390-5aa20fc08a84'

api = Api(app)
def askFor_APIKey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # key in header
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == app.secret_key:
            return view_function(*args, **kwargs)
        else:
            abort(401,'Unauthorized Access')
    return decorated_function

#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#error 500 page
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

#error 401 page
#doesn't work because of unable overwrite werkzeug.exceptions to generate {'message':'xxx'} from abort()    
@app.errorhandler(401)
def unauthorized_error(e):
    return render_template('401.html'), 401

#Restful API
class urlOps(Resource):
    #Get urls info from database
    @askFor_APIKey
    def get(self):
        if urlInventory.select().count() > 0:
            dataset = []
            for data in urlInventory.select():
                result = {}
                result['urlName'] = data.urlName
                result['urlDomain'] = data.urlDomain
                result['frequency'] = data.frequency
                result['expectedStatus'] = data.expectedStatus
                result['expectedString'] = data.expectedString
                dataset.append(result)
            return jsonify(dataset)
        else:
            return jsonify({'success': True,'error':'Empty database'})

    #Post new url info from database
    @askFor_APIKey
    def post(self):
        result = request.get_json(force=True)
        url = {'urlName': result['urlName'],
                'urlDomain': result['urlDomain'],
                'frequency': result['frequency'],
                'expectedStatus': result['expectedStatus'],
                'expectedString': result['expectedString']}

        if urlInventory.select().where(urlInventory.urlDomain==url['urlDomain']).count()==0:
            urlInventory.create(urlName = url['urlName'],
                                urlDomain = url['urlDomain'],
                                frequency=url['frequency'],
                                expectedStatus=url['expectedStatus'],
                                expectedString=url['expectedString'])
            checker.urlchecker(url['urlDomain'],url['frequency'])
        else:
            return jsonify({'success': False,'error':'Existed URL'})
        return jsonify(url)

api.add_resource(urlOps, '/urlOps')

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
        if users.select().where(users.userName==data['username']).count() == 1:
            re = users.select(users.userPassword).where(users.userName==data['username'])
            for user in re:
                pw = user.userPassword
            if pw == data['password']:
                session['key'] = app.secret_key
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
        if urlInventory.select().count() > 0:
            for data in urlInventory.select():
                result = {}
                result['urlName'] = data.urlName
                result['urlDomain'] = data.urlDomain
                dataset.append(result)
        return render_template('admin.html',dataset=dataset)
    return jsonify({'success': False,'error': 'Please log in'})

#search domain name
@app.route('/searchDomain',methods=['POST'])
def searchDomain():
    if request.method == 'POST':
        session.pop('domain', None)
        domain = request.form['name']
        if urlInventory.select().where(urlInventory.urlDomain==domain).count() == 1:
            session['domain'] = domain
            return jsonify({'success': True, 'Url domain': session['domain']})
        else:
            return jsonify({'success': False, 'error': 'Invalid domain'})
    return

#logs page
@app.route('/loginfo')
def loginfo():
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
            return render_template('loginfo.html',dataset=dataset)
        return jsonify({'success': False, 'error': 'Please search domain name'})
    return jsonify({'success': False, 'error': 'Please log in'})


if __name__ == '__main__':
    models.init_db()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
