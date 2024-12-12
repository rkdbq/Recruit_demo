import time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # GUI 없이 실행
options.add_argument("--no-sandbox")  # 샌드박스 없이 실행
options.add_argument("--disable-dev-shm-usage")  # /dev/shm 메모리 부족 문제 해결
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')  # User-Agent 설정

driver = webdriver.Chrome(options=options) 

def crawl_company(num):
    try:
        # 순회할 URL 패턴 설정
        base_url = 'https://www.wanted.co.kr/company/'
        
        # for param in range(20001, 30001):
        url = f"{base_url}{num}"
        print(f"[회사 API] {url}로 이동합니다.")
        
        # 페이지 로드
        driver.get(url)
        time.sleep(.1)  # 페이지 로드 대기 (필요에 따라 조정 가능)
        
        try:
            # CompanyInfoTable 정보 파싱
            info_table = driver.find_element(By.CLASS_NAME, 'CompanyInfoTable_wrapper__ip8TX')
            if info_table:
                definitions = info_table.find_elements(By.CLASS_NAME, 'CompanyInfoTable_definition__lynJc')
                
                company_info = {}
                company_name = driver.find_element(By.CLASS_NAME, 'wds-1n0snwn').text
                company_info['회사명'] = company_name
                
                address = driver.find_elements(By.CLASS_NAME, 'CompanyInfo_CompanyInfo__Text__oLsJ6.wds-ozue28')[1].text
                company_info['회사주소'] = address
                
                for definition in definitions:
                    try:
                        key = definition.find_element(By.CLASS_NAME, 'CompanyInfoTable_definition__dt__TZgn2').text
                        value = definition.find_element(By.CLASS_NAME, 'CompanyInfoTable_definition__dd__O_0tI').text
                        value = value.replace('\n', '')
                        
                        company_info[key] = value
                    except Exception as e:
                        print(f"[회사 API] 정보 파싱 중 오류 발생: {e}")
                
                for key, value in company_info.items():
                    if value == '-':
                        company_info[key] = None
                        
                # 회사 정보를 API에 POST 요청으로 전송
                try:
                    api_url = 'http://113.198.66.75:10164/companies'  # API 엔드포인트 URL
                    employ_num_str = company_info.get('고용보험 가입 사원수').replace('명', '').strip()
                    employ_num = int(employ_num_str) if employ_num_str.isdigit() else None  # 사원 수를 정수형으로 변환
                    
                    # 회사 정보에서 연도 추출 (예: "2010년 설립"에서 2010만 추출)
                    est_year = company_info.get('연혁', '').split('(')[-1].replace('년 설립)', '').strip()
                    est_date = None
                    # 연도만 추출하여 "1월 1일" 날짜로 설정
                    if est_year.isdigit():  # 연도가 숫자형으로 잘 파싱되었는지 확인
                        est_date = est_year + "-01-01"
                    
                    company_type = company_info.get('기업유형')
                    if not company_type:
                        company_type = company_info.get('회사구분')
                        
                    payload = {
                        'company_name': company_info.get('회사명'),
                        'rep_name': company_info.get('대표자명'),
                        'company_type': company_type,
                        'industry': company_info.get('표준산업분류'),
                        'employ_num': employ_num,
                        'est_date': est_date,
                        'homepage': company_info.get('홈페이지'),
                        'address': company_info.get('회사주소')
                    }
                    response = requests.post(api_url, json=payload)
                    if response.status_code == 201:
                        print(f"[회사 API] ({num})가 성공적으로 저장되었습니다.")
                    else:
                        print(f"[회사 API] ({num}) 저장 실패. 상태 코드: {response.status_code}")
                except Exception as e:
                    print(f"[회사 API] 요청 중 오류 발생: {e}")
            else:
                print(f"[회사 API] {url}에서 CompanyInfoTable이 없습니다.")
                
        except Exception as e:
            print(f"[회사 API] {url}에서 정보 파싱 중 오류 발생: {e}")

    except Exception as e:
        print(f"[회사 API] 오류 발생: {e}")

    finally:
        # 브라우저 닫기
        driver.quit()
