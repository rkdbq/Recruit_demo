from flask import Blueprint, request
from flasgger import swag_from
from models import db
from models.job_posting_model import JobPosting, JobPostingKeyword, JobPostingSkill
from views.response import json_response

job_posting_bp = Blueprint('job_posting', __name__)

@job_posting_bp.route('/', methods=['GET'])
@swag_from('../api_docs/job_posting_apis/get_jobs.yml')
def get_jobs():
    page = request.args.get('page', 1, type=int)
    location = request.args.get('location', type=str)
    experience = request.args.get('experience', type=str)
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)
    tech_stack = request.args.get('tech_stack', type=str)
    company_id = request.args.get('company_id', type=int)
    position = request.args.get('position', type=str)
    keyword = request.args.get('keyword', type=str)  # 추가된 키워드 필터
    sort_by = request.args.get('sort_by', 'id', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = JobPosting.query
    
    # 필터링
    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    if experience:
        query = query.filter(JobPosting.experience.ilike(f"%{experience}%"))
    if salary_min is not None:
        query = query.filter(JobPosting.salary >= salary_min)
    if salary_max is not None:
        query = query.filter(JobPosting.salary <= salary_max)
    if tech_stack:
        query = query.join(JobPostingSkill).filter(JobPostingSkill.skill.ilike(f"%{tech_stack}%"))
    if company_id is not None:
        query = query.filter(JobPosting.company_id == company_id)
    if position:
        query = query.filter(JobPosting.position.ilike(f"%{position}%"))
    if keyword:
        query = query.join(JobPostingKeyword).filter(JobPostingKeyword.keyword.ilike(f"%{keyword}%"))
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(JobPosting, sort_by).desc())
    else:
        query = query.order_by(getattr(JobPosting, sort_by).asc())
    
    jobs = query.paginate(page=page, per_page=20, error_out=False)

    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        data=[job.to_summerized_dict() for job in jobs],
        )

@job_posting_bp.route('/<int:job_id>', methods=['GET'])
@swag_from('../api_docs/job_posting_apis/get_job_detail.yml')
def get_job_detail(job_id):
    job = JobPosting.query.get(job_id)
    try:
        job.views += 1
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())
    
    job_data = job.to_dict()
    job_data['keywords'] = [keyword.to_dict() for keyword in job.keywords]
    job_data['tech_stack'] = [skill.to_dict() for skill in job.skills]
    
    return json_response(
            code=200, 
            args=request.args.to_dict(), 
            data=[job_data],
            )

@job_posting_bp.route('/', methods=['POST'])
@swag_from('../api_docs/job_posting_apis/add_job.yml')
def add_job():
    if not request.json or not 'company_id' in request.json:
        return json_response(code=400, args=request.args.to_dict())

    job_posting = JobPosting(
        title=request.json['title'],
        location=request.json['location'],
        experience=request.json['experience'],
        salary=request.json.get('salary', None),
        company_id=request.json['company_id'],
        position=request.json['position'],
        views=request.json.get('views', None),
    )
    
    existing_job_posting = JobPosting.query.filter_by(title=job_posting.title).first()
    if existing_job_posting:
        return json_response(
            code=409, 
            args=request.args.to_dict(), 
            message="Job Posting already exists",
        )
    
    # 채용 공고 저장
    try:
        db.session.add(job_posting)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())

    for keyword in request.json['keywords']:
        job_posing_keyword = JobPostingKeyword(
            job_posting_id=job_posting.id,
            keyword=keyword,
        )
        try:
            db.session.add(job_posing_keyword)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
        
    for skill in request.json['tech_stack']:
        job_posing_skill = JobPostingSkill(
            job_posting_id=job_posting.id,
            skill=skill,
        )
        try:
            db.session.add(job_posing_skill)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
        
    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[job_posting.to_dict()],
        )

@job_posting_bp.route('/<int:id>', methods=['PUT'])
@swag_from('../api_docs/job_posting_apis/update_job.yml')
def update_job(id):
    existing_job_posting = JobPosting.query.get(id)
    if not existing_job_posting:
        return json_response(
            code=404, 
            args=request.args.to_dict(), 
            message="Job Posting not found",
            )
    
    new_job_posting = JobPosting(
        title=request.json.get('title', None),
        location=request.json.get('location', None),
        experience=request.json.get('experience', None),
        salary=request.json.get('salary', None),
        company_id=request.json.get('company_id', None),
        position=request.json.get('position', None),
        views=request.json.get('views', None),
    )
    
    # 채용 공고 저장
    try:
        for (key, value) in new_job_posting.to_dict().items():
            if value:
                setattr(existing_job_posting, key, value)
        db.session.commit() 
        
    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())
        
    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[existing_job_posting.to_dict()],
        )

@job_posting_bp.route('/<int:id>', methods=['DELETE'])
@swag_from('../api_docs/job_posting_apis/delete_job.yml')
def delete_job(id):
    if not request.json:
        json_response(code=400, args=request.args.to_dict())
        
    job_posting = JobPosting.query.get(id)
    if not job_posting:
        return json_response(
            code=404, 
            args=request.args.to_dict(), 
            message="Job Posting not found",
            )
    
    try:
        db.session.delete(job_posting)
        db.session.commit()
        
    except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())
    
    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        message=f"Job Posting with ID {job_posting.id} has been deleted",
        )
