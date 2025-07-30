import json

import boto3


def get_secret(name: str, region: str = "us-east-1") -> dict[str, str]:
    """
    Returns a secret value by name from AWS `secretsmanager`_.

    :param name: An AWS `secretsmanager`_ name.
    :type name: :py:obj:`str`
    :param region: An AWS region name. Default is :py:obj:`"us-east-1"`.
    :type region: :py:obj:`str`
    :returns: A secret value dictionary.
    :rtype: :py:obj:`dict`\[:py:obj:`str`, :py:obj:`str`\]


    .. _secretsmanager: https://docs.aws.amazon.com/secretsmanager/

    """
    session = boto3.Session(profile_name="terminusgps-site-role")
    client = session.client(service_name="secretsmanager", region_name=region)
    secret = client.get_secret_value(**{"SecretId": name})["SecretString"]
    return json.loads(secret)
