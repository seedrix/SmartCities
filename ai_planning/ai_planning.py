import requests, sys

data = {'domain': open("domain.pddl", 'r').read(),
        'problem': open("problem.pddl", 'r').read()}

resp = requests.post('http://solver.planning.domains/solve',
                     verify=False, json=data).json()
if (resp["status"] == "error"):
    print("error:")
    print(resp["result"])
    print(resp["result"]["error"])      

else:
    print(resp["result"]["output"])
    plan = resp['result']['plan']
    for step in plan:
        action = step["action"]
        name = step["name"]
        print(name)
        # print(action)
     