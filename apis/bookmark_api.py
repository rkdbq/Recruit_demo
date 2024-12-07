import datetime
from flask import abort, g, jsonify, Blueprint, request
from models import db
from models.user_model import Bookmark
from services.jwt_service import jwt_required

bookmark_bp = Blueprint('bookmark', __name__)

@bookmark_bp.route('/', methods=['POST'])
@jwt_required
def toggle_bookmark():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    if not request.json or not 'job_posting_id' in request.json:
        abort(400)
            
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
            return jsonify(bookmark.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
    else:
        try:
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({'message': f'Bookmark with ID {bookmark.id} has been deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
        
@bookmark_bp.route('/', methods=['GET'])
@jwt_required
def get_bookmark():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
            
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
    return jsonify([bookmark.to_dict() for bookmark in bookmarks])
