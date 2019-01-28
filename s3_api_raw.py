import json
from functools import wraps
from s3_model import S3Model


def handle_api_error(func):
    """
        This define a decorator to format the HTTP response of the lambda:
        - a status code
        - the body of the response as a string
    """
    
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return {
                'statusCode': 200,
                'body': json.dumps(func(*args, **kwargs)),
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': str(e),
            }
    return wrapped_func

class S3ApiRaw(object):
    """
        A class providing the lambda handlers for the HTTP requests of an S3Model class
        Class attribute:
         - s3_model_cls: an S3Model class providing the schema of the object and the helper functions to mange the S3 data
    """
    s3_model_cls = S3Model

    @classmethod
    @handle_api_error
    def get(cls, event, context):
        obj_id = event['pathParameters']['id']
        return cls.s3_model_cls.load(obj_id)

    @classmethod
    @handle_api_error
    def put(cls, event, context):
        obj_id = event['pathParameters']['id']
        obj = cls.s3_model_cls.load(obj_id)

        updates = json.loads(event['body'])
        obj.update(updates)

        return cls.s3_model_cls.save(obj)

    @classmethod
    @handle_api_error
    def post(cls, event, context):
        obj = json.loads(event['body'])
        if 'id' in obj:
            raise Exception('Do not specify id in resource creation')
        return cls.s3_model_cls.save(obj)

    @classmethod
    @handle_api_error
    def delete(cls, event, context):
        obj_id = event['pathParameters']['id']
        return cls.s3_model_cls.delete_obj(obj_id)

    @classmethod
    @handle_api_error
    def all(cls, event, context):
        return [cls.s3_model_cls.load(obj_id) for obj_id in cls.s3_model_cls.list_ids()]

    #This method is a little bit clumsy but we need the lambda handlers to be module functions
    @classmethod
    def get_api_methods(self):
        return self.get, self.post, self.put, self.delete, self.all
