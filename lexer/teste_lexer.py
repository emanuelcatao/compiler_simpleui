from lexer import lexer

source_code = '''
    let x = 10;
    function metodo1() {
        repeat 5 times {
            createWindow();
            addElement(x);
        }
    }
    '''
    
try:
    tokens = lexer(source_code)
    for token in tokens:
        print(token)
except SyntaxError as e:
    print(e)