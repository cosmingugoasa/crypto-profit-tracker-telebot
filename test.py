import json
#from util import getTokenBalanceFromBSCscan

def rewrite_json(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def update_json(json_data):
    with open("users.json") as f:        
        data = json.load(f)
        for user in data:
            if(user == str(json_data)[2:].split("'")[0]):
                data[user].append((json_data["dax"])[0])
                return data

        data.update(json_data)        
        return data

json_data = {
    'gelmo' : [{
        'crypto' : 'feg',
        'investment' : '25'
    }]
}

json_contract = {
    'name' : 'address'
}
