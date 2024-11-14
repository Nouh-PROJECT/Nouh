import json
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required

bp = Blueprint('lecture', __name__)

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
                with open('lectures.json', 'r+', encoding='utf-8') as file:
                    lectures = json.load(file)
                    lectures.append(new_lecture)
                    file.seek(0)
                    json.dump(lectures, file, ensure_ascii=False, indent=4)
                flash('강의가 성공적으로 추가되었습니다!', 'success')
            except (FileNotFoundError, json.JSONDecodeError):
                # 파일이 없거나 JSON 형식에 문제가 있는 경우
                with open('lectures.json', 'w', encoding='utf-8') as file:
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
        with open('lectures.json', 'r', encoding='utf-8') as file:
            lectures = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        lectures = []

    return render_template('/lecture/lectureList.html', lectures=lectures)


@bp.route('/lecture/<int:id>', methods=['GET'])
def lecture_detail(id):
    try:
        with open('lectures.json', 'r', encoding='utf-8') as file:
            lectures = json.load(file)
            lecture = lectures[id] if id < len(lectures) else None
    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        lecture = None

    if not lecture:
        return "강의를 찾을 수 없습니다.", 404

    return render_template('lecture.html', lecture=lecture)