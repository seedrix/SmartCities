import requests, sys

data = {'domain': open("domain.pddl", 'r').read(),
        'problem': open("problem.pddl", 'r').read()}

try:
    resp = requests.post('http://solver.planning.domains/solve',
                     verify=False, json=data).json()
except requests.ConnectionError or requests.exceptions.HTTPError as err:
    print(err)
                

if (resp["status"] == "error"):
    print(resp["result"]["output"])
else:
    print("parsed succesfully")
    print(resp["result"])    
    with open(sys.argv[3], 'w') as f:
        f.write('\n'.join([act['name'] for act in resp['result']['plan']]))