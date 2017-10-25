from flask import Flask, make_response
from flask_restful import Resource, Api
from models import admin, urlLog, urlInventory

app = Flask(__name__)
api = Api(app, prefix="/api/v1")
auth = HTTPBasicAuth()

@auth.verify_password
def verify(APIkey):
    if not (APIkey):
        return False
    elif admin.select().where(admin.apikey == APIkey):
        return True
    else:
        return False

#Get urls info from database
class url_inventory(Resource):
    @auth.login_required
    def get(self):

        return {"meaning_of_life": 42}

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

#admin page
@app.route('/admin')
def admin():
    if 'email' in session:
        if admin.select().where(Users.email==session['email']).get().permission == "admin":
            dataset = []
            if Requests.select().count() > 0:
                for data in Requests.select():
                    result = {}
                    result['title'] = data.title
                    result['link'] = data.link
                    if data.livestream == 1:
                        result['livestream'] = 'Yes'
                    else:
                        result['livestream'] = 'No'
                    dataset.append(result)
            return render_template('admin.html',dataset=dataset)
        else:
            return 'Please sign in as Admin'
    return 'Please log in'

api.add_resource(url_inventory, '/urlInventory')



if __name__ == '__main__':
    app.run(debug=True)
