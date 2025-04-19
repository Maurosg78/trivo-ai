from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from app.models import SupervisorRule
from app.extensions import db

@app.route('/supervisor/add_rule', methods=['GET', 'POST'])
def add_rule():
    if request.method == 'POST':
        rule_type = request.form.get('rule_type')
        rule_description = request.form.get('rule_description')
        positive_example = request.form.get('positive_example')
        negative_example = request.form.get('negative_example')
        priority = request.form.get('priority')
        recipe_category = request.form.get('recipe_category') or None
        
        try:
            # Crear una nueva regla en la base de datos
            new_rule = SupervisorRule(
                rule_type=rule_type,
                description=rule_description,
                positive_example=positive_example,
                negative_example=negative_example,
                priority=priority,
                recipe_category=recipe_category,
                created_at=datetime.now()
            )
            db.session.add(new_rule)
            db.session.commit()
            
            # Actualizar la lista de reglas en el supervisor
            from app.llm_supervisor import LLMSupervisor
            LLMSupervisor.refresh_rules()
            
            flash('Regla agregada con éxito', 'success')
            return redirect(url_for('supervisor_status'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar la regla: {str(e)}', 'danger')
    
    return render_template('supervisor_add_rule.html') 