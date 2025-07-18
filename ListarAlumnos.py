import boto3
import pymysql
import json
import os

def lambda_handler(event, context):
    # Nombre del secreto en Secrets Manager
    secret_name = os.environ['SECRET_NAME']
    region_name = os.environ.get('AWS_REGION', 'us-east-1')

    # Obtener el secreto
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Si el secreto es una cadena JSON
        secret = get_secret_value_response['SecretString']
        secret_dict = json.loads(secret)

        host = secret_dict['host']
        user = secret_dict['user']
        password = secret_dict['password']
        database = secret_dict['database']

        # Conectar a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if 'connection' in locals() and connection:
            connection.close()
