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
# app.py
from models import db, User, Essay, CompetenceFeedback



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
            
            # Chama a função que avalia a redação via GPT-4 e retorna o JSON
            feedback_data = evaluate_essay(text)
            
            # Salva o registro da redação (opcional: também salvando o JSON completo)
            essay = Essay(
                user_id=user.id,
                title=title,
                text=text,
                feedback=feedback_data,  # opcional, se quiser manter o JSON
                score_total=feedback_data["nota_total"],
                comp1_score=feedback_data["competencias"][0]["nota"],
                comp2_score=feedback_data["competencias"][1]["nota"],
                comp3_score=feedback_data["competencias"][2]["nota"],
                comp4_score=feedback_data["competencias"][3]["nota"],
                comp5_score=feedback_data["competencias"][4]["nota"],
            )
            db.session.add(essay)
            db.session.commit()  # Para obter o ID da redação
            
            # Agora, para cada competência, crie um registro na nova tabela
            for comp in feedback_data["competencias"]:
                cf = CompetenceFeedback(
                    essay_id=essay.id,
                    numero=comp["numero"],
                    nome=comp["nome"],
                    nota=comp["nota"],
                    justificativa=comp["justificativa"],
                    # Se os dados forem listas, converta para string:
                    pontos_fortes=", ".join(comp["pontos_fortes"]) if comp.get("pontos_fortes") else None,
                    pontos_fracos=", ".join(comp["pontos_fracos"]) if comp.get("pontos_fracos") else None,
                    sugestoes=", ".join(comp["sugestoes"]) if comp.get("sugestoes") else None,
                )
                db.session.add(cf)
            # Finalize a transação
            db.session.commit()
            
            # Redireciona para a página de feedback
            return redirect(url_for('feedback_page', essay_id=essay.id))
        
        return render_template('submit_essay.html')

    
    @app.route('/feedback/<int:essay_id>')
    def feedback_page(essay_id):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        
        essay = Essay.query.get_or_404(essay_id)
        
        if essay.user_id != session['user_id']:
            return redirect(url_for('dashboard'))
        
        # Buscar os feedbacks detalhados da nova tabela
        competence_feedbacks = CompetenceFeedback.query.filter_by(essay_id=essay.id).order_by(CompetenceFeedback.numero).all()
        
        # Gerar o gráfico de radar, se necessário
        comp_scores = [cf.nota for cf in competence_feedbacks]
        radar_fig = radar_chart(comp_scores)
        radar_div = plotly.offline.plot(radar_fig, include_plotlyjs=False, output_type='div')
        
        return render_template('feedback.html', essay=essay, competence_feedbacks=competence_feedbacks, radar_div=radar_div)

    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
