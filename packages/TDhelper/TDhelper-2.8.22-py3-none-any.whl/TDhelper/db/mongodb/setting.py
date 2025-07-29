db_cfg = {
    'url': None,
    'db': None,
    'user':"",
    'pwd':""
}

def define(uri,db,user="",pwd=""):
    global db_cfg 
    db_cfg= {
        'url':uri,
        'db':db,
        'user':user,
        'pwd':pwd
    }