import json
import boto3
import os, datetime
import uuid
import dicttoxml
from jsonschema import Draft4Validator
#from schema import Schema

# We use boto3 to interact with AWS services 
s3 = boto3.client('s3')

# This is the environment variable defined in the serverless.yml
BUCKET = os.getenv('BUCKET')

class S3Model(object):
    """
        This is a base class that will store and load data in an S3 Bucket
        Class attributes:
            - SCHEMA: a schema.Schema instance (https://github.com/keleshev/schema). 
                This specify the structure of the data we store
            - name: A string that will define the folder on the S3 bucket
                    in which we will store the file (this will allow for multiple models to be stored on the same bucket)
    """
    
    # By default: All dictionnaries are valid 
    #SCHEMA = Schema(dict)
    # The files will be stored in the raw folder
    name = 'raw'
    @classmethod
    def beautify(cls,path, instance, message, validator_value):
        if 'is not of type' in message:
            #return '\''+path[-1] +' = '  + str(instance) +'\' debe ser de tipo ' + type(validator_value)
            return 'El campo \''+path[-1] +'\' con el valor \''  + str(instance) +'\' debe ser de tipo ' + cls.type(validator_value)
        elif 'is a required property' in message:
            return 'El campo '+message.replace('is a required property','es obligatorio')
        elif 'is too short' in message and len(instance)==0:
            return 'El campo \''+path[-1] +'\' es obligatorio'
        else:
            return message

    @classmethod
    def validate(cls, obj):
        ##assert cls.SCHEMA._schema == dict or type(cls.SCHEMA._schema) == dict
        ##return cls.SCHEMA.validate(obj)
        v = Draft4Validator(cls.SCHEMA)
        errors = []
        for error in sorted(v.iter_errors(obj), key=str):
            #print('.'.join([str(elem) for elem in error.path ]), beautify(error.path,error.message, error.validator_value))
            errors.append({'mensaje':cls.beautify(error.path, error.instance,error.message, error.validator_value),
                            'ubicacion':'.'.join([str(elem) for elem in error.path ])})
        if len(errors) == 0:
            errors.append({'mensaje':'Recibido'})
        return errors

    @classmethod
    def type(cls,name):
        types = {'string' : 'caracter', 'number' : 'numérico'}
        if name in types:
            return types[name]

    @classmethod
    def savejson(cls, obj, formato):
        # We affect an id if there isn't one
        object_id = obj.setdefault('id', str(uuid.uuid4()))
        resp = cls.validate(obj)
        if 'ubicacion' in resp[0]:
            return resp
        nit = obj["Valorable"]["Invoice"][0]["IdentificacionEmisor"]
        fechaHora = datetime.datetime.now().strftime("%Y%m%d%H%M%S")        
        s3.put_object(
            Bucket=BUCKET,
            Key=f'{cls.folder}/{nit}/{nit}{cls.efactura}/{nit}_{fechaHora}_{object_id}.{formato}',
            Body=json.dumps(obj)
        )
        return resp

    @classmethod
    def savexml(cls, obj):
        # We affect an id if there isn't one
        object_id = obj.setdefault('id', str(uuid.uuid4()))
        resp = cls.validate(obj)
        if 'ubicacion' in resp[0]:
            return resp
        nit = obj["Valorable"]["Invoice"][0]["IdentificacionEmisor"]
        fechaHora = datetime.datetime.now().strftime("%Y%m%d%H%M%S")        
        s3.put_object(
            Bucket=BUCKET,
            Key=f'{cls.folder}/{nit}/{nit}{cls.efactura}/{nit}_{fechaHora}_{object_id}.xml',
            Body=dicttoxml.dicttoxml(obj, custom_root='FactElectronica')
        )
        return resp

    @classmethod
    def load(cls, object_id):
        obj = s3.get_object(
            Bucket=BUCKET,
            Key=f'{cls.name}/{object_id}',
        )
        obj = json.loads(obj['Body'].read())
        return cls.validate(obj)

    @classmethod
    def delete_obj(cls, object_id):
        s3.delete_object(
            Bucket=BUCKET,
            Key=f'{cls.name}/{object_id}',
        )
        return {'deleted_id': object_id}

    @classmethod
    def list_ids(cls):
        bucket_content = s3.list_objects_v2(Bucket=BUCKET)
        object_ids = [
            file_path['Key'].lstrip(f'{cls.name}/')
            for file_path in bucket_content.get('Contents', [])
            if file_path['Size'] > 0
        ]
        return object_ids