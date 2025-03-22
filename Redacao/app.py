from dotenv import load_dotenv
load_dotenv()


from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Essay
from config import Config
from auth import auth_bp
from essay_evaluator import evaluate_essay
from visualization import radar_chart
import plotly
import json



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Cria as tabelas (apenas para desenvolvimento; em produção, use migrations)
    with app.app_context():
        db.create_all()
    
    # Registra Blueprint de autenticação
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/')
    def index():
        # Página inicial (pode redirecionar para login se preferir)
        return redirect(url_for('auth_bp.login'))
    
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        
        user = User.query.get(session['user_id'])
        
        # Pega todas as redações do usuário
        essays = Essay.query.filter_by(user_id=user.id).all()
        
        # Calcula média, melhor nota etc. (exemplo simples)
        if essays:
            total_scores = [e.score_total for e in essays if e.score_total is not None]
            if total_scores:
                avg_score = sum(total_scores) / len(total_scores)
                best_score = max(total_scores)
            else:
                avg_score = 0
                best_score = 0
        else:
            avg_score = 0
            best_score = 0
        
        return render_template('dashboard.html', user=user, essays=essays,
                               avg_score=avg_score, best_score=best_score)
    
    @app.route('/submit_essay', methods=['GET', 'POST'])
    def submit_essay():
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        
        user = User.query.get(session['user_id'])
        
        if request.method == 'POST':
            if user.credits <= 0:
                flash('Você não possui créditos suficientes.')
                return redirect(url_for('dashboard'))
            
            title = request.form.get('title')
            text = request.form.get('text')
            
            # Envia para avaliação GPT-4
            feedback_data = evaluate_essay(text)
            
            # Salva no banco
            # Extraia cada competência
            comp1 = feedback_data["competencias"][0]
            comp2 = feedback_data["competencias"][1]
            comp3 = feedback_data["competencias"][2]
            comp4 = feedback_data["competencias"][3]
            comp5 = feedback_data["competencias"][4]

            essay = Essay(
                user_id=user.id,
                title=title,
                text=text,
                feedback=feedback_data,  # Armazena o JSON completo se quiser
                score_total=feedback_data["nota_total"],

                comp1_score=comp1["nota"],
            comp2_score=comp2["nota"],
            comp3_score=comp3["nota"],
            comp4_score=comp4["nota"],
            comp5_score=comp5["nota"],
        )

            db.session.add(essay)
            db.session.commit()
            # Decrementa crédito
            user.credits -= 1
            db.session.commit()
            
            return redirect(url_for('feedback_page', essay_id=essay.id))
        
        return render_template('submit_essay.html')
    
    @app.route('/feedback/<int:essay_id>')
    def feedback_page(essay_id):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        
        essay = Essay.query.get_or_404(essay_id)
        
        # Verifica se a redação pertence ao usuário
        if essay.user_id != session['user_id']:
            return redirect(url_for('dashboard'))
        
        feedback_data = essay.feedback
        
        # Gera radar chart
        comp_scores = [
            essay.comp1_score or 0,
            essay.comp2_score or 0,
            essay.comp3_score or 0,
            essay.comp4_score or 0,
            essay.comp5_score or 0
        ]
        radar_fig = radar_chart(comp_scores)
        
        # Converte figura Plotly para div HTML
        radar_div = plotly.offline.plot(radar_fig, include_plotlyjs=False, output_type='div')
        
        return render_template('feedback.html',
                               essay=essay,
                               feedback_data=feedback_data,
                               radar_div=radar_div)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
