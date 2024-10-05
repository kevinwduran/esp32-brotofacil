from flask import Blueprint, session, redirect, url_for, request, render_template


auth_bp = Blueprint('auth', __name__)

# Definindo credenciais de exemplo (para fins de teste)
USUARIO_VALIDO = 'admin'
SENHA_VALIDO = 'senha123'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDO:
            session['usuario_autenticado'] = True
            return redirect(url_for('dashboard.dashboard'))
        else:
            return render_template('login.html', erro='Credenciais inválidas')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('usuario_autenticado', None)
    return redirect(url_for('home.index'))