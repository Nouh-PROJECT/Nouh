import json
import os
import mimetypes
from flask import Blueprint, render_template, request, redirect, flash, url_for, Response
from flask_login import login_required

bp = Blueprint('lecture', __name__)

json_file_path = os.path.join(os.path.dirname(__file__), 'lectures.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    # 모든 파일 확장자 허용
    return True


def resolve_filename_conflict(directory, filename):
    """
    같은 이름의 파일이 있을 경우 파일 이름에 숫자를 추가하여 중복을 방지합니다.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}({counter}){ext}"
        counter += 1
    return new_filename


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as file:
                file_content = file.read()

            return Response(file_content, mimetype=mime_type or 'application/octet-stream')
        else:
            return "파일을 찾을 수 없습니다.", 404
    except Exception as e:
        return f"오류 발생: {str(e)}", 500


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def lecture_add():
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
        video_file = request.files.get('video-file')

        if subject_id != 0 and lecture_name and video_file and allowed_file(video_file.filename):
            original_filename = video_file.filename
            resolved_filename = resolve_filename_conflict(UPLOAD_FOLDER, original_filename)
            file_path = os.path.join(UPLOAD_FOLDER, resolved_filename)

            # 파일 저장
            video_file.save(file_path)

            subject_name = next((sub['name'] for sub in subjects if sub['id'] == subject_id), None)
            new_lecture = {
                "subject_id": subject_id,
                "subject_name": subject_name,
                "lecture_name": lecture_name,
                "original_filename": original_filename,
                "file_path": resolved_filename
            }

            try:
                if not os.path.exists(json_file_path):
                    with open(json_file_path, 'w', encoding='utf-8') as file:
                        json.dump([], file, ensure_ascii=False, indent=4)

                with open(json_file_path, 'r+', encoding='utf-8') as file:
                    lectures = json.load(file)
                    lectures.append(new_lecture)
                    file.seek(0)
                    json.dump(lectures, file, ensure_ascii=False, indent=4)
                flash('강의가 성공적으로 추가되었습니다!', 'success')
            except Exception as e:
                flash(f'강의 추가 중 오류가 발생했습니다: {e}', 'danger')

            return redirect(url_for('lecture.lecture_add'))
        else:
            flash('모든 필드를 입력하고 적절한 형식의 파일을 업로드해 주세요.', 'danger')

    return render_template('/lecture/lectureAdd.html', subjects=subjects)

@bp.route('/list', methods=['GET'])
@login_required
def lecture_list():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        lectures = []

    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_lectures = len(lectures)
    total_pages = (total_lectures + per_page - 1) // per_page

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)

    offset = (page - 1) * per_page
    paginated_lectures = lectures[offset:offset + per_page]

    return render_template(
        'lecture/lectureList.html',
        lectures=paginated_lectures,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )

@bp.route('/lecture', methods=['GET'])
def lecture_detail():
    video_path = request.args.get('path')
    if not video_path:
        return "잘못된 요청입니다.", 400

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)
            lecture = next((lec for lec in lectures if lec['file_path'] == video_path), None)
    except (FileNotFoundError, json.JSONDecodeError):
        lecture = None

    video_url = url_for('lecture.video_view', path=video_path)

    return render_template('/lecture/lecture.html', lecture=lecture, video_url=video_url)


@bp.route('/lecture/video', methods=['GET'])
def video_view():
    file_path = request.args.get('path')
    if file_path:
        try:
            full_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, file_path))

            # 보안상 매우 위험: 경로 검증 없이 절대 경로 생성 및 파일 읽기
            if os.path.exists(full_path) and not os.path.isdir(full_path):
                mime_type, _ = mimetypes.guess_type(full_path)
                with open(full_path, 'rb') as f:
                    file_content = f.read()
                response = Response(file_content, mimetype=mime_type or 'application/octet-stream')
                return response
            else:
                return "파일을 찾을 수 없습니다.", 404
        except Exception as e:
            return f"오류 발생: {str(e)}", 500
    return "잘못된 요청입니다.", 400


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def lecture_edit(id):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)
            lecture = lectures[id] if id < len(lectures) else None
    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        lecture = None

    if not lecture:
        return "강의를 찾을 수 없습니다.", 404

    if request.method == 'POST':
        subject_id = int(request.form.get('lecture-s'))
        lecture_name = request.form.get('lecture-name')
        video_file = request.files.get('video-file')

        if subject_id != 0 and lecture_name and (not video_file or allowed_file(video_file.filename)):
            if video_file:
                original_filename = video_file.filename
                unique_filename = generate_unique_filename(original_filename)
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                video_file.save(file_path)
                lecture['file_path'] = unique_filename
                lecture['original_filename'] = original_filename

            lecture['subject_id'] = subject_id
            lecture['subject_name'] = next((sub['name'] for sub in subjects if sub['id'] == subject_id), None)
            lecture['lecture_name'] = lecture_name

            try:
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(lectures, file, ensure_ascii=False, indent=4)
                flash('강의가 성공적으로 수정되었습니다!', 'success')
            except Exception as e:
                flash(f'강의 수정 중 오류가 발생했습니다: {e}', 'danger')

            return redirect(url_for('lecture.lecture_list'))
        else:
            flash('모든 필드를 입력해 주세요.', 'danger')

    return render_template('/lecture/lectureEdit.html', lecture=lecture, subjects=subjects)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def lecture_delete(id):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            lectures = json.load(file)

        if id < len(lectures):
            deleted_lecture = lectures.pop(id)
            if 'file_path' in deleted_lecture and deleted_lecture['file_path']:
                file_path = os.path.join(UPLOAD_FOLDER, deleted_lecture['file_path'])
                if os.path.exists(file_path):
                    os.remove(file_path)

            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(lectures, file, ensure_ascii=False, indent=4)
            flash(f'강의 "{deleted_lecture["lecture_name"]}"가 삭제되었습니다.', 'success')
        else:
            flash('강의를 찾을 수 없습니다.', 'danger')
    except (FileNotFoundError, json.JSONDecodeError, IndexError) as e:
        flash(f'강의 삭제 중 오류가 발생했습니다: {e}', 'danger')

    return redirect(url_for('lecture.lecture_list'))
