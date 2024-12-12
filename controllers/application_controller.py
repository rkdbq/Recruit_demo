import datetime
from flask import g, Blueprint, request
from flasgger import swag_from
from models import db
from models.user_model import Application
from services.jwt_service import jwt_required
from views.response import json_response

application_bp = Blueprint('application', __name__)

@application_bp.route('/', methods=['POST'])
@jwt_required
@swag_from('../api_docs/application_apis/apply.yml')
def apply():
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    if not request.json or not 'job_posting_id' in request.json:
        return json_response(code=400, args=request.args.to_dict())
            
    new_application = Application(
        job_posting_id=request.json['job_posting_id'],
        user_id=existing_user.id,
        status="지원 완료",
        applied_date=datetime.datetime.now(),
        resume=request.json.get('resume', None)
    )
    
    existing_application = Application.query.filter_by(job_posting_id=new_application.job_posting_id,
                                                       user_id=new_application.user_id).first()
    
    application = existing_application
    if not existing_application:
        application = new_application
        try:
            db.session.add(new_application)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
    elif existing_application.status == "지원 취소":
        try:
            existing_application.status = "지원 완료"
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
    else:
        return json_response(
            code=409, 
            args=request.args.to_dict(),
            message=f"Application with Id {application.id} is already applied",
        )

    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[application.to_dict()],
        )

@application_bp.route('/', methods=['GET'])
@jwt_required
@swag_from('../api_docs/application_apis/get_applications.yml')
def get_applications():
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = Application.query.filter_by(user_id=existing_user.id)

    # 필터링
    if status:
        query = query.filter(Application.status.ilike(f"%{status}%"))
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(Application, sort_by).desc())
    else:
        query = query.order_by(getattr(Application, sort_by).asc())
        
    applications = query.paginate(page=page, per_page=20, error_out=False)
    
    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        data=[app.to_dict() for app in applications],
        )

@application_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required
@swag_from('../api_docs/application_apis/delete_application.yml')
def delete_application(id):
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    application = Application.query.filter_by(id=id,
                                              user_id=existing_user.id).first()
    if not application:
        return json_response(
            code=404, 
            args=request.args.to_dict(), 
            message="Application not found",
            )

    try:
        if application.status == "지원 취소":
            return json_response(
                code=409, 
                args=request.args.to_dict(),
                message=f"Application with Id {application.id} is already canceled",
                )
        application.status = "지원 취소"
        db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())

    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        message=f"Application with ID {application.id} has been deleted",
        )
