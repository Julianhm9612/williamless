from s3_api_raw import S3ApiRaw
from s3_model import S3Model
#from schema import Schema
from jsonschema import Draft4Validator
import json

#We define the model
class User(S3Model):
    def load_file(name):
        with open(name) as f:
            return json.load(f)
    name = 'user'
    folder = 'XMLRecibidos'
    extension = 'json'
    efactura = 'EFactura'
    SCHEMA = load_file('factura.schema.json')

# Next we define the resource
class UserResource(S3ApiRaw):
    s3_model_cls = User

# Finally we declare the lambda handlers as module functions
get, post, put, delete, all = UserResource.get_api_methods()