from flask import Blueprint, request
from flasgger import swag_from
from models import db
from models.company_model import Company
from views.response import json_response

company_bp = Blueprint('company', __name__)

@company_bp.route('/', methods=['GET'])
@swag_from('../api_docs/company_apis/get_companies.yml')
def get_companies():
    companies = Company.query.all()
    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        data=[company.to_dict() for company in companies],
        )

@company_bp.route('/', methods=['POST'])
@swag_from('../api_docs/company_apis/add_company.yml')
def add_company():
    if not request.json:
        return json_response(code=400, args=request.args.to_dict())

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
        return json_response(code=500, args=request.args.to_dict())

    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[company.to_dict()],
        )
