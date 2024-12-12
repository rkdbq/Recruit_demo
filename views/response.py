from flask import jsonify

def json_response(code: int, args: dict, data=None, message=None):
    """
    Args:
        status_code (int): HTTP 상태 코드
        args (dict): 요청의 쿼리 매개변수 정보
        data (list or dict): 결과로 반환할 데이터
        
    Returns:
        response (json): 정리된 응답 데이터
    """
    res = {
        "status_code": code,
        "args": args,
        "data": {},
    }
    
    if 200 <= code and code <= 299:
        res["message"] = "Success"
    elif code == 400:
        res['message'] = "Bad Request"
    elif code == 404:
        res['message'] = "User Not Found"
    elif code == 500:
        res['message'] = "Database error occured"
    
    if message:
        res['message'] = message
    if data:
        res['data'] = data
        
    return jsonify(res), code
