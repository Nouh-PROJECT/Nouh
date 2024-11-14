import json
import os
import re
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required

bp = Blueprint('lecture', __name__)

json_file_path = os.path.join(os.path.dirname(__file__), 'lectures.json')
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def lecture_add():
    # 하드코딩된 과목 데이터
    subjects = [
        {"id": 1, "name": "인프라 활용을 위한 파이썬"},
        {"id": 2, "name": "애플리케이션 보안"},
        {"id": 3, "name": "시스템/네트워크 보안 기술"},
        {"id": 4, "name": "클라우드 보안 기술"},
        {"id": 5, "name": "클라우드기반 시스템 운영/구축 실무"},
        {"id": 6, "name": "클라우드기반 취약점 진단 및 대응 실무"},
        {"id": 7, "name": "데이터 3법과 개인정보보호"},
        {"id": 8, "name": "클라우드 보안 컨설팅 실무"}
    ]

    

    # JSON 파일이 없으면 빈 파일 생성
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    if request.method == 'POST':
        subject_id = int(request.form.get('lecture-s'))
        lecture_name = request.form.get('lecture-name')
        video_link = request.form.get('video-link')

        if subject_id != 0 and lecture_name and video_link:
            # 선택된 과목 이름 가져오기
            subject_name = next((sub['name'] for sub in subjects if sub['id'] == subject_id), None)
            
            new_lecture = {
                "subject_id": subject_id,
                "subject_name": subject_name,
                "lecture_name": lecture_name,
                "lec_url": video_link
            }

            # JSON 파일에 저장
            try:
                with open(json_file_path, 'r+', encoding='utf-8') as file:
                    lectures = json.load(file)
                    lectures.append(new_lecture)
                    file.seek(0)
                    json.dump(lectures, file, ensure_ascii=False, indent=4)
                flash('강의가 성공적으로 추가되었습니다!', 'success')
            except (FileNotFoundError, json.JSONDecodeError):
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump([new_lecture], file, ensure_ascii=False, indent=4)
                flash('강의가 성공적으로 추가되었습니다!', 'success')
            
            return redirect(url_for('lecture.lecture_add'))
        else:
            flash('모든 필드를 입력해 주세요.', 'danger')

    return render_template('/lecture/lectureAdd.html', subjects=subjects)

@bp.route('/list', methods=['GET'])
@login_required
def lecture_list():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)
            print("Loaded lectures:", lectures)  # 디버깅용 출력
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON: {e}")
        lectures = []

    # 페이지네이션 설정
    page = request.args.get("page", 1, type=int)
    per_page = 10  # 페이지당 항목 수
    total_lectures = len(lectures)
    total_pages = (total_lectures + per_page - 1) // per_page

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)

    # 페이지에 해당하는 강의 슬라이싱
    offset = (page - 1) * per_page
    paginated_lectures = lectures[offset:offset + per_page]

    # 검색 기능 처리
    keyword = request.args.get('keyword', type=str)
    if keyword:
        paginated_lectures = [lecture for lecture in paginated_lectures if keyword.lower() in lecture['lecture_name'].lower()]

    return render_template(
        'lecture/lectureList.html',
        lectures=paginated_lectures,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )




@bp.route('/lecture/<int:id>', methods=['GET'])
def lecture_detail(id):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)
            lecture = lectures[id] if id < len(lectures) else None
    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        lecture = None

    if not lecture:
        return "강의를 찾을 수 없습니다.", 404

    # 유튜브 URL을 embed URL로 변환
    youtube_url_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(youtube_url_pattern, lecture['lec_url'])
    if match:
        video_id = match.group(1)
        lecture['lec_url'] = f"https://www.youtube.com/embed/{video_id}"

    return render_template('/lecture/lecture.html', lecture=lecture)
