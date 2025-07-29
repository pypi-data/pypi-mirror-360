from TDhelper.generic.dynamic.base.Meta import Meta,dynamic_creator

    

if __name__=="__main__":
    pass
    '''
    bb=[{'rpc':['ABC','DEFG']},{'bb':['bbc','bbd']}]
    def p(cls_name,name,*args,**kwargs): 
        print("p")
        print(cls_name+"."+name)
        print(args)
        print(kwargs)

    def ec(cls_name,name,*args,**kwargs): 
        print("ec")
        print(cls_name+"."+name)
        print(args)
        print(kwargs)

    cc=type("RPC",(dynamic_creator,),{"__construct__":bb,"__hook_method__":p})()
    #cc.rpc.__set_hook__(ec)
    cc.rpc.ABC(**{"R":"abc method."})
    cc.rpc.DEFG(**{"R":"DEFG method."})
    '''

    

    """
    ast create function.
    import ast
    
    code_1=def __method_router__(*args,**kwargs):
        print("__method_router__-------------")
        print(sys._getframe().f_code.co_name)
        print(args)
        print(kwargs)
        print(__name__)"""
    '''
    print(ast.dump(ast.parse(code_1)))
    foo_compile = compile(code_1 , "", "exec")
    foo_code = [ i for i in foo_compile.co_consts][0]
    #[ i for i in foo_compile.co_consts if isinstance(i, CodeType)][0]
    print(foo_code)
    ggg=FunctionType(foo_code,globals())
    ggg()

    from ast import *
    import types
    print(python_version())

    def create_func(func_name):
        function_ast = FunctionDef(
            name=func_name,
            args=arguments(args=[], vararg=None, kwarg=None, defaults=[],kwonlyargs=[],posonlyargs=[],kw_defaults=[]),
            body=[
                Assign(
                    targets=[Name(id='__name__',ctx= Store(),lineno=0,col_offset=0)],
                    value=Str(func_name,lineno=0,col_offset=1),
                    lineno=0,
                    col_offset=0
                ),
                Expr(
                    value=Call(
                        func=Name(id="print",ctx=Load(),lineno=1,col_offset=0),
                        args=[
                            Name(id='__name__',ctx= Load(),lineno=1,col_offset=1)
                        ],
                        keywords=[],
                        lineno=1,
                        col_offset=0
                    ),
                    lineno=1,
                    col_offset=0
                ),
                Return(value=Num(n=42, lineno=2, col_offset=0), lineno=2, col_offset=0,type_comment=None)
            ],
            decorator_list=[],
            type_comment=None,
            lineno=1,
            col_offset=0
        )
        return function_ast

    module_ast = Module(body=[create_func("dynamic_create_func")],type_ignores=[])
    module_code = compile(module_ast, "", "exec")
    function_code = [c for c in module_code.co_consts if isinstance(c, types.CodeType)][0]
    func = types.FunctionType(function_code, globals())
    print(func())
    '''