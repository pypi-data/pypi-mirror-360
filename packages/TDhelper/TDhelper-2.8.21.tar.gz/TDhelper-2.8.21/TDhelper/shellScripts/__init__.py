'''
can insert console_scripts module by setup.py; after module install success,can use shell command.
e.g. 'console_scripts': [
            #'foo = demo:test',
            #'bar = demo:test',
            'saas = TDhelper.shellScripts.saasHelper:CMD'
        ],

e.g. shell command: saas --name [name] --path [path] --git [git url]
'''