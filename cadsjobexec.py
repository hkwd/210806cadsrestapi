import base64
import requests
import pprint
import sys

args = sys.argv
#args=['ms183-win19:9080','Test/resttest','admin','password','VNAME','hogehoge']

#引数の確認
if len(args)<4 or len(args)%2!=0:
    print('usage: <url> <job_path> <user> <password> [parameter1_name] [parameter1_value] [parameter2_name] [parameter2_value]...')
    exit(1)
url_pre=args[0]
job_path=args[1]
user=args[2]
password=args[3]

parameters=[]
for i in range(4,len(args),2):
    parameters.append({'Name':args[i],'Value':args[i+1]})
#print(parameters)

#basic認証のためにbase64でencode
userpass=str(base64.b64encode((user+':'+password).encode()).decode("ascii"))

headers = {'Content-Type':'application/json',
           'Authorization': 'Basic {}'.format(userpass),
#          'Client-Accept-Language': 'en',
          'Accept-Language':'en'}

#接続確認
# url="http://"+url_pre+"/process/rest/job/getVersion"
# r_get = requests.get(url, headers=headers)
# print(r_get.status_code)
# print(r_get.text)

#ジョブ実行
body={
  "jobLocationURI": "spsscr:///"+job_path,
  "jobOptions": {
    "setNotificationEnabled": "true",
    "jobParameterValue": parameters
  }
}
url="http://"+url_pre+"/process/rest/job/submitJobWithOptions"
import json
r_submitJobWithOptions = requests.post(url, data=json.dumps(body),headers=headers)

#print(r_submitJobWithOptions.status_code)
if r_submitJobWithOptions.status_code!=200:
    print('Request failed. http status:{}'.format(r_submitJobWithOptions.status_code))
    exit(2)
print(r_submitJobWithOptions.text)

import re
execution_ID= re.match('Job is submitted with options and execution ID is (.+)',r_submitJobWithOptions.text).group(1)
#print(execution_ID)

#終了待ち
import time
url="http://"+url_pre+"/process/rest/job/getExecutionDetails?executionID="+execution_ID
r_getExecutionDetails = requests.get(url, headers=headers)
#1秒おきに終了確認
while r_getExecutionDetails.json()['executionState']!='ENDED' and r_getExecutionDetails.status_code==200:
    print ('.',end='',flush=True)
    time.sleep(1)
    r_getExecutionDetails = requests.get(url, headers=headers)
print('')

#print(type(r_getExecutionDetails.json()['executionSuccess'])
if r_getExecutionDetails.status_code!=200:
    print('Request failed. http status:{}'.format(r_getExecutionDetails.status_code))
    exit(2)

print('---getExecutionDetails---')
pprint.pprint(r_getExecutionDetails.json())

#ジョブステップの詳細取得
url="http://"+url_pre+"/process/rest/job/getJobStepExecutions?executionID="+execution_ID
r_getJobStepExecutions = requests.get(url, headers=headers)
#print(r_getJobStepExecutions.status_code)
if r_getJobStepExecutions.status_code!=200:
    print('Request failed. http status:{}'.format(r_getJobStepExecutions.status_code))
    exit(2)

print('---getJobStepExecutions---')
pprint.pprint(r_getJobStepExecutions.json())

#成否の判定
if r_getExecutionDetails.json()['executionSuccess']:
    print ('Success')
else:
    print('Execution failed')
    exit(3)

