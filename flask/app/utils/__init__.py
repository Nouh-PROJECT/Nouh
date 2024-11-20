def Pagination(**kwargs):
    page = kwargs.get("page", 1, type=int)
    total_pages = 0
    start_page = 0
    end_page = kwargs.get()
    per_page = kwargs.get("per_page", 10, type=int)
    offset = (page - 1) * per_page

    # 페이지 계산
    
    # 페이지 데이터 불러오기

    return ""