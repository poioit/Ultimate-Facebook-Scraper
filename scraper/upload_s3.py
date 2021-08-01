import boto3
import urllib
import requests
from io import BytesIO
from boto.s3.key import Key
from botocore.exceptions import NoCredentialsError
import os


S3_IMG_URL = 'https://di93lo4zawi3i.cloudfront.net'


class S3uploader:
    def __init__(self, access_key, secret_key, buckid_id):
        self.ACCESS_KEY = access_key
        self.SECRET_KEY = secret_key
        self.BUCKET_ID = buckid_id
        pass

    def upload(self, url, user_id):
        if self.ACCESS_KEY == '':
            print("upload without S3 access key")
            return
        filename = user_id + '.jpg'
        try:
            conn = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY,
                                aws_secret_access_key=self.SECRET_KEY)
            bucket_name = self.BUCKET_ID
            # 'Like' a file object
            file_object = requests.get(url).content
            with open(filename, 'wb') as handler:
                handler.write(file_object)
            try:
                conn.upload_file(filename, bucket_name, filename)
                print("Upload Successful")
                os.remove(filename)
                return 'https://s3.ap-northeast-1.amazonaws.com/org.handoutdocs.innovtest.store/' + filename
            except FileNotFoundError:
                print("The file was not found")
                return False
            except NoCredentialsError:
                print("Credentials not available")
                return False
            return "Success"

        except Exception as e:
            return e

    def upload_to_aws(self, local_file, bucket, s3_file):
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False


# uploaded = upload_to_aws('local_file', BUCKET_ID, 's3_file_name')
