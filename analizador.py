from flask import Flask, request, render_template_string
import re
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = (
    'PR', 'ID', 'NUM', 'SYM', 'STRING', 'LE', 'PLUSPLUS'
)

t_PR = r'\b(for|if|else|while|return)\b'
t_ID = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
t_NUM = r'\b\d+\b'
t_STRING = r'\".*?\"'
t_LE = r'<='
t_PLUSPLUS = r'\+\+'
t_SYM = r'[;{}()\[\]=<>!+-/*]'

t_ignore = ' \t\n'

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# Definición de la gramática para el analizador sintáctico
def p_statement_for(p):
    '''statement : PR "(" declaration ";" condition ";" increment ")" "{" body "}"'''
    p[0] = "Sintaxis correcta"

def p_declaration(p):
    '''declaration : ID ID "=" NUM'''

def p_condition(p):
    '''condition : ID LE NUM'''

def p_increment(p):
    '''increment : ID PLUSPLUS'''

def p_body(p):
    '''body : expression'''
    
def p_expression(p):
    '''expression : PR "(" STRING ")" SYM'''

def p_error(p):
    p[0] = "Error sintáctico"

parser = yacc.yacc()

# Plantilla HTML para mostrar resultados
html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Analizador Léxico, Sintáctico y Semántico</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f8f9fa;
        margin: 0;
        padding: 20px;
      }
      h1 {
        color: #343a40;
        text-align: center;
      }
      h2 {
        color: #495057;
      }
      div.container {
        max-width: 800px;
        margin: 0 auto;
        background-color: #ffffff;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
      }
      textarea {
        width: 100%;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 10px;
        margin-bottom: 10px;
        font-size: 16px;
        resize: vertical;
      }
      input[type="submit"] {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 16px;
      }
      input[type="submit"]:hover {
        background-color: #0056b3;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
      }
      table, th, td {
        border: 1px solid #dee2e6;
      }
      th, td {
        padding: 12px;
        text-align: left;
      }
      th {
        background-color: #f1f1f1;
      }
      pre {
        background-color: #f8f9fa;
        padding: 10px;
        border: 1px solid #ced4da;
        border-radius: 4px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Analizador Léxico, Sintáctico y Semántico</h1>
      <form method="post">
        <textarea name="code" rows="10" cols="50">{{ code }}</textarea><br>
        <input type="submit" value="Analizar">
      </form>
    </div>
    <div class="container">
      <h2>Analizador Léxico</h2>
      <table>
        <tr>
          <th>Tokens</th><th>PR</th><th>ID</th><th>Números</th><th>Símbolos</th><th>Error</th>
        </tr>
        {% for row in lexical %}
        <tr>
          <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td>
        </tr>
        {% endfor %}
        <tr>
          <td>Total</td><td>{{ total['PR'] }}</td><td>{{ total['ID'] }}</td><td>{{ total['NUM'] }}</td><td>{{ total['SYM'] }}</td><td>{{ total['ERR'] }}</td>
        </tr>
      </table>
    </div>
    <div class="container">
      <h2>Analizador Sintáctico y Semántico</h2>
      <table>
        <tr>
          <th>Sintáctico</th><th>Semántico</th>
        </tr>
        <tr>
          <td>{{ syntactic }}</td><td>{{ semantic }}</td>
        </tr>
      </table>
      <h2>Código Corregido</h2>
      <pre>{{ corrected_code }}</pre>
    </div>
  </body>
</html>
'''

def analyze_lexical(code):
    lexer.input(code)
    results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    for line in code.split('\n'):
        row = [''] * 6
        lexer.input(line)
        while True:
            tok = lexer.token()
            if not tok:
                break
            results[tok.type] += 1
            row[list(tokens).index(tok.type)] = 'x'
        rows.append(row)
    return rows, results

def correct_syntactic(code):
    # Corrección sintáctica del bucle 'for'
    corrected_code = re.sub(r'\bfor\s*\(\s*.*\s*\)\s*\{', r'for (int i = 1; i <= 19; i++) {', code)
    corrected_code = re.sub(r'\{.*\}', r'{\n    System.out.println("i");\n}', corrected_code, flags=re.DOTALL)
    corrected_code = re.sub(r'system\.out\.println\s*\((.*?)\)\s*', r'System.out.println(\1);', corrected_code)
    return corrected_code

def correct_semantic(code):
    # Corrección semántica del uso de 'System.out.println'
    corrected_code = re.sub(r'\bSystem\.out\.println\s*\((.*?)\)\s*', r'System.out.println(\1);', code)
    return corrected_code

def analyze_syntactic(code):
    # Análisis sintáctico utilizando ply.yacc
    try:
        result = parser.parse(code)
        return result, code
    except Exception as e:
        corrected_code = correct_syntactic(code)
        return f"Error sintáctico: {e}", corrected_code

def analyze_semantic(code):
    # Análisis semántico simplificado
    errors = []
    if not re.search(r'\bSystem\.out\.println\s*\(\s*".*"\s*\)\s*;', code):
        errors.append("Error semántico en System.out.println. Asegúrate de usar 'System.out.println()' correctamente con comillas dobles para las cadenas.")
        corrected_code = correct_semantic(code)
    else:
        corrected_code = code

    if not errors:
        return "Uso correcto de System.out.println", corrected_code
    else:
        return " ".join(errors), corrected_code

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    corrected_code = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result, corrected_code = analyze_syntactic(code)
        semantic_result, corrected_code = analyze_semantic(corrected_code)
    return render_template_string(html_template, code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result, corrected_code=corrected_code)

if __name__ == '__main__':
    app.run(debug=True)
