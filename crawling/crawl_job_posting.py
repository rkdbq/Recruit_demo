import time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from crawl_company import crawl_company

options = Options()
options.add_argument("--headless")  # GUI 없이 실행
options.add_argument("--no-sandbox")  # 샌드박스 없이 실행
options.add_argument("--disable-dev-shm-usage")  # /dev/shm 메모리 부족 문제 해결
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')  # User-Agent 설정

driver = webdriver.Chrome(options=options) 

try:
    # 순회할 URL 패턴 설정
    base_url = 'https://www.wanted.co.kr/wd/'
    
    for param in range(230000, 220000, -1):
        url = f"{base_url}{param}"
        print(f"[채용 공고 API] {url}로 이동합니다.")
        
        # 페이지 로드
        driver.get(url)
        time.sleep(.1)  # 페이지 로드 대기 (필요에 따라 조정 가능)
        
        try:
            job_info = {}
            
            job_info['company_name'] = driver.find_element(By.CLASS_NAME, 'JobHeader_JobHeader__Tools__Company__Link__zAvYv').text
            company_page_num = driver.find_element(By.CLASS_NAME, 'JobHeader_JobHeader__Tools__Company__Link__zAvYv').get_attribute('data-company-id')
            
            try:
                crawl_company(company_page_num)
            finally:
                company_id = None
                try:
                    api_url = f'http://113.198.66.75:10164/companies?company_name={job_info["company_name"]}'  # API 엔드포인트 URL
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        company_id = response.json()['data'][0]['id']
                        
                except Exception as e:
                        print(f"[채용 공고 API] 회사 API 요청 중 오류 발생: {e}")    

                if company_id:
                    job_info['company_id'] = company_id
                    summary = driver.find_elements(By.CLASS_NAME, 'JobHeader_JobHeader__Tools__Company__Info__yT4OD.wds-rgovpd')
                    job_info['location'] = summary[0].text
                    job_info['experience'] = summary[1].text
                    job_info['title'] = driver.find_element(By.CLASS_NAME, 'JobHeader_JobHeader__PositionName__kfauc.wds-jtr30u').text
                    job_info['salary'] = "회사 내규에 따름"
                    job_info['tech_stack'] = []
                    job_info['tags'] = []
                    
                    tech_stack = driver.find_element(By.CLASS_NAME, 'JobSkillTags_JobSkillTags__list__01GRk')
                    tag = driver.find_element(By.CLASS_NAME, 'CompanyTags_CompanyTags__list__WjcTV')
                    
                    if tech_stack:
                        skills = tech_stack.find_elements(By.CLASS_NAME, 'wds-1m3gvmz')
                        for skill in skills:
                            job_info['tech_stack'].append(skill.text)
                        
                    if tag:
                        tags = tag.find_elements(By.CLASS_NAME, 'wds-1m3gvmz')
                        for t in tags:
                            job_info['tags'].append(t.text)
                    
                    # 채용 공고 정보를 API에 POST 요청으로 전송
                    try:
                        api_url = 'http://113.198.66.75:10164/jobs'  # API 엔드포인트 URL

                        payload = {
                            'title': job_info.get('title'),
                            'location': job_info.get('location'),
                            'experience': job_info.get('experience'),
                            'salary': None,
                            'tech_stack': job_info.get('tech_stack'),
                            'company_id': job_info.get('company_id'),
                            'position': job_info.get('title'),
                            'keywords': job_info.get('tags')
                        }
                        response = requests.post(api_url, json=payload)
                        if response.status_code == 201:
                            print(f"[채용 공고 API] ({company_page_num}: {job_info['title']})가 성공적으로 저장되었습니다.")
                        else:
                            print(f"[채용 공고 API] ({company_page_num}: {job_info['title']}) 저장 실패. 상태 코드: {response.status_code}")
                    except Exception as e:
                        print(f"[채용 공고 API] 요청 중 오류 발생: {e}")
                    
        except Exception as e:
            print(f"[채용 공고 API] {url}에서 정보 파싱 중 오류 발생: {e}")

except Exception as e:
    print(f"[채용 공고 API] 오류 발생: {e}")

finally:
    # 브라우저 닫기
    driver.quit()
