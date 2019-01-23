import json
import boto3
import os
import uuid

# The schema library helps us to ensure the data stored matches a certain schema
from schema import Schema

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
    SCHEMA = Schema(dict)
    # The files will be stored in the raw folder
    name = 'raw'

    @classmethod
    def validate(cls, obj):
        assert cls.SCHEMA._schema == dict or type(cls.SCHEMA._schema) == dict
        return cls.SCHEMA.validate(obj)

    @classmethod
    def save(cls, obj):
        # We affect an id if there isn't one
        object_id = obj.setdefault('id', str(uuid.uuid4()))
        obj = cls.validate(obj)
        s3.put_object(
            Bucket=BUCKET,
            Key=f'{cls.name}/{object_id}',
            Body=json.dumps(obj),
        )
        return obj

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