''' Init Applicatio
Shell command: saas --name [name] --path [path] --git [git url]; 

e.g
    sudo saas --name example_project --path ./example_project --git https://gitee.com/TonyDon/saas-cli.git

Args:
    --name: project name. to replace configrue files.
    --path: init project path. if it's null then init project by shell directory.
    --git: git url, if it's null clone by default.
    
Note
    More helpe doc. to read project README.MD
'''

import os
import sys


def CMD():
    try:
        args = buildArgs(sys.argv)
        cmd_line = "".join(["sudo git clone ", args["git"], " ", args["path"]])
        result = os.system(cmd_line)
        if result == 0:
            if args["name"]:
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/manage.py")
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/app_name/asgi.py")
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/app_name/wsgi.py")
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/make/cfg-example.ini")
                result = os.system(
                    "sudo sed -i 's/{service_name}/'"+args['name']+"'/g' " + args['path']+"/make/docker_init.ini")
                result = os.system("".join(
                    ["sudo mv ", args['path'], "/app_name ", " ", args['path'], "/", "/", args["name"]]))
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/DockerFile.arm")
                result = os.system(
                    "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/DockerFile.x86")
                if result == 0:
                    result = os.system(
                        "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' "+args['path']+"/"+args['name']+"/settings.py")
                    result = os.system(
                        "sudo sed -i 's/{project_name}/'"+args['name']+"'/g' " + args['path']+"/make/uwsgi.example.ini")
                    result = os.system("sudo rm -rf "+args['path']+"/.git")
                result= os.system("sudo cp -r"+args['path']+"/make/cfg-example.ini"+args["path"]+"/config/development.ini")
                result= os.system("sudo cp -r"+args['path']+"/make/cfg-example.ini"+args["path"]+"/config/test.ini")
        else:
            print('git clone error.')
    except Exception as e:
        print(e)


def buildArgs(args):
    result = {
        "name": "project_name",
        "path": os.path.abspath(os.curdir),
        "git": "https://gitee.com/TonyDon/saas-cli.git"
    }
    if args:
        o = 0
        while True:
            if o+1 >= len(args):
                break
            lower_cmd = args[o].lower()
            if lower_cmd == "--name" or lower_cmd == "--n":
                o += 1
                result["name"] = args[o]
            elif lower_cmd.lower() == "--path" or lower_cmd == "--p":
                o += 1
                result["path"] = args[o]
            elif lower_cmd.lower() == "--git" or lower_cmd == "--g":
                o += 1
                result["git"] = args[o]
            o += 1
    return result


if __name__ == '__main__':
    CMD()