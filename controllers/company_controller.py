from flask import abort, jsonify, Blueprint, request
from models import db
from models.company_model import Company

company_bp = Blueprint('company', __name__)

@company_bp.route('/', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies])

@company_bp.route('/', methods=['POST'])
def add_company():
    if not request.json:
        abort(400)

    company = Company(
        company_name=request.json['company_name'],
        rep_name=request.json.get('rep_name', None),
        company_type=request.json['company_type'],
        industry=request.json['industry'],
        employ_num=request.json.get('employ_num', None),
        est_date=request.json.get('est_date', None),
        homepage=request.json.get('homepage', None),
        address=request.json.get('address', None),
    )
    
    # 채용 공고 저장
    try:
        db.session.add(company)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500

    return jsonify(company.to_dict()), 201