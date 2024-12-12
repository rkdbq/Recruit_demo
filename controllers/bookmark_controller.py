import datetime
from flask import g, Blueprint, request
from flasgger import swag_from
from models import db
from models.user_model import Bookmark
from services.jwt_service import jwt_required
from views.response import json_response

bookmark_bp = Blueprint('bookmark', __name__)

@bookmark_bp.route('/', methods=['POST'])
@jwt_required
@swag_from('../api_docs/bookmark_apis/toggle_bookmark.yml')
def toggle_bookmark():
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    if not request.json or not 'job_posting_id' in request.json:
        json_response(code=400, args=request.args.to_dict())
            
    new_bookmark = Bookmark(
        user_id=existing_user.id,
        job_posting_id=request.json['job_posting_id'],
        bookmarked_date=datetime.datetime.now(),
    )
    
    existing_bookmark = Bookmark.query.filter_by(job_posting_id=new_bookmark.job_posting_id,
                                                       user_id=new_bookmark.user_id).first()
    
    bookmark = existing_bookmark
    if not existing_bookmark:
        bookmark = new_bookmark
        try:
            db.session.add(bookmark)
            db.session.commit()
            return json_response(
                code=201, 
                args=request.args.to_dict(), 
                data=[bookmark.to_dict()],
                )
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
    else:
        try:
            db.session.delete(bookmark)
            db.session.commit()
            return json_response(
                code=200, 
                args=request.args.to_dict(), 
                message=f"Bookmark with ID {bookmark.id} has been deleted",
                )
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
        
@bookmark_bp.route('/', methods=['GET'])
@jwt_required
@swag_from('../api_docs/bookmark_apis/get_bookmarks.yml')
def get_bookmarks():
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
            
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'bookmarked_date', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = Bookmark.query.filter_by(user_id=existing_user.id)
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(Bookmark, sort_by).desc())
    else:
        query = query.order_by(getattr(Bookmark, sort_by).asc())
        
    bookmarks = query.paginate(page=page, per_page=20, error_out=False)
    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        data=[bookmark.to_dict() for bookmark in bookmarks],
        )
