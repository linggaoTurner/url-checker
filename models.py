
from peewee import *
import peewee
from datetime import datetime

database = SqliteDatabase('urlchecker.db')
class BaseModel(Model):
    class Meta:
        database = database


class users(BaseModel):
    userName = CharField(unique=True)
    userPassword = CharField(null=True)

    def __unicode__(self):
        return self.userName


class urlInventory(BaseModel):
    id = IntegerField(primary_key=True)
    urlName = CharField(null=True)
    urlDomain = CharField(unique=True)
    frequency = CharField(null=True)
    expectedStatus = CharField(null=True)
    expectedString = CharField(null=False)

    def __unicode__(self):
        return self.urlName

class urlLog(BaseModel):
    id = IntegerField(primary_key=True)
    urlDomain = CharField(null=True)
    timeChecked = DateTimeField(default=datetime.now)
    statusCode = CharField(null=True)
    healthyState = CharField(null=True)

    def __unicode__(self):
        return (self.id, self.urlDomain, self.healthState)

def init_db():
    try:
        database.create_tables([admin,urlInventory,urlLog])
    except peewee.OperationalError:
        print ("tables already exists!")
