from .company_controller import company_bp
from .job_posting_controller import job_posting_bp
from .auth_controller import auth_bp
from .application_controller import application_bp
from .bookmark_controller import bookmark_bp

def register_blueprints(app):
    app.register_blueprint(company_bp, url_prefix='/companies')
    app.register_blueprint(job_posting_bp, url_prefix='/jobs')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(application_bp, url_prefix='/applications')
    app.register_blueprint(bookmark_bp, url_prefix='/bookmarks')