from s3_api_raw import S3ApiRaw
from s3_model import S3Model
from schema import Schema, Use

#We define the model
class User(S3Model):
    """
        User:
        - name: "user"
        - schema: 
           id: string
           first_name: str,
           last_name: str,
           birthday: str,
    """
    name = 'user'
    SCHEMA = Schema({
        'id': str,
        'first_name': str,
        'last_name': str,
        'birthday': str,
        'age': int
    })

# Next we define the resource
class UserResource(S3ApiRaw):
    s3_model_cls = User

# Finally we declare the lambda handlers as module functions
get, post, put, delete, all = UserResource.get_api_methods()