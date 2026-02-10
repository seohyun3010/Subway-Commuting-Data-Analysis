"""
서울시 지하철 시간대별 승하차 데이터를 활용하여 출·퇴근 시간대 혼잡이 특정 노선과 역에 집중되는지 분석한다.
분석 범위는 2020년 1월 ~ 2025년 7월이며, 주요 분석은 2025년 최신 데이터를 중심으로 수행한다.
"""

# 서울시 지하철 호선별·역별·시간대별 승하차 인원 데이터 로드
df_time = pd.read_csv(
    'data/seoul_subway_time.csv',
    encoding='cp949'
)

# 출퇴근 혼잡이 가장 두드러지는 2호선 데이터만 추출
df_2line = df_time[df_time['호선명'] == '2호선']

# 분석 일관성을 위해 최근 5년(2020.01 ~ 2025.07) 데이터만 사용
df_2line_selected = df_2line[
    (df_2line['사용월'] >= 202001) &
    (df_2line['사용월'] <= 202507)
]

"""
출퇴근 혼잡이 집중되는 주요 업무지구 및 상업지역 역을 중심으로 시간대별 승차 패턴을 분석하기 위해 대상 역을 선정한다.
"""

target_stations = [
    '강남', '잠실(송파구청)', '홍대입구', '구로디지털단지',
    '삼성(무역센터)', '신림', '선릉', '역삼', '성수'
]

# 선정한 주요 역만 필터링
df_2line_selected_stations = df_2line_selected[
    df_2line_selected['지하철역'].isin(target_stations)
]

# 분석 대상 기간: 2025년 1월 ~ 7월
df_period = df_2line_selected_stations[
    (df_2line_selected_stations['사용월'] >= 202501) &
    (df_2line_selected_stations['사용월'] <= 202507)
]

# 컬럼명이 '승차인원'을 포함하는 시간대 컬럼만 동적으로 추출
geton_col = [col for col in df_period.columns if '승차인원' in col]

# 역별 시간대 승차 인원 데이터만 추출
df_geton = df_period[['지하철역'] + geton_col]

# 월별 데이터가 존재하므로 동일 역 기준으로 시간대별 승차 인원 합산
geton_count = (
    df_geton.groupby('지하철역')[geton_col]
    .sum()
    .reset_index()
)

"""
출근 시간대(07~10시)에 승차 인원이 집중되는 호선 및 지하철역을 파악하기 위한 분석
"""
# 출근 시간대 승차 인원 컬럼만 선택
new_cols = [
    '사용월', '호선명', '지하철역',
    '07시-08시 승차인원', '08시-09시 승차인원', '09시-10시 승차인원'
]
df_commute = df_time[new_cols]

# 출근 시간대 승차 인원 합계 지표 생성
df_commute_period['승차합'] = df_commute_period[geton_cols].sum(axis=1)

# 호선·역 단위로 출근 시간대 승차 수요 집계
df_commute_group = (
    df_commute_period
    .groupby(['호선명', '지하철역'], as_index=False)['승차합']
    .sum()
)

# 출근 시간대 승차 인원이 가장 많은 상위 10개 역 추출
top10_commute = df_commute_group.sort_values(
    by='승차합', ascending=False
).head(10)


"""
출근 시간대 승차 인원이 많은 상위 10개 역을 시각화하여 혼잡이 특정 노선에 집중되는 구조를 직관적으로 확인한다. 
색상은 호선 구분을 위해 다르게 지정한다.
"""
# 역별 소속 노선을 시각적으로 구분하기 위한 색상 매핑
def commute_get_color(row):
    if row['지하철역'] == '서울역':
        return '#0066CC'   # 1호선
    elif row['지하철역'] == '연신내':
        return '#FFA500'   # 3호선
    elif row['지하철역'] == '쌍문':
        return '#0000FF'   # 4호선
    elif row['지하철역'] in ['까치산', '화곡']:
        return '#800080'   # 5호선
    else:
        return '#26A65B'   # 2호선

"""
퇴근 시간대(17~20시)는 출근 시간대와 반대로 업무지구에서 주거지로 이동하는 수요가 집중되는 시간대이므로,
승차 인원이 많은 역을 기준으로 혼잡 패턴을 비교 분석한다.
"""
