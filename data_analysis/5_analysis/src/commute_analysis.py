"""
출·퇴근 시간대 지하철 혼잡이 특정 역과 노선에 집중되는지 확인하기 위해
역·호선 단위로 승하차 인원을 집계하고, 승하차 총합 기준 상위 10개 역을 추출한다.
"""

### 상위 10개 역 추출하기 

# 승차 인원이 많은 역을 확인하기 위해 승차총승객수 기준으로 내림차순 정렬 
df_sorted_drive = df.sort_values(by='승차총승객수', ascending=False)
# 하차 인원이 많은 역을 확인하기 위해 하차총승객수 기준으로 내림차순 정렬
df_sorted_getoff = df.sort_values(by='하차총승객수', ascending=False)

# 역별·호선별 통행량을 파악하기 위해 호선명과 역명을 기준으로 그룹화 후 승차/하차 인원 합산
df_grouped = df.groupby(['호선명', '역명'])[['승차총승객수', '하차총승객수']].sum().reset_index()]

# 역별 전체 이용 규모를 파악하기 위해 승차 + 하차 인원의 총합 컬럼 생성
df_grouped['승하차총합'] = df_grouped['승차총승객수'] + df_grouped['하차총승객수']

# 승하차 총합 기준으로 혼잡도가 가장 높은 상위 10개 역 추출
top_df = df_grouped.sort_values(by='승하차총합', ascending=False).head(10)

"""
승하차 총합 기준 상위 10개 역의 이용 규모를 시각화한다.
역별 혼잡이 특정 노선에 집중되는지 직관적으로 확인하기 위해 노선에 따라 색상을 구분하여 막대 그래프를 생성한다.
"""

### 시각화 

def plot_top10_stations(df):
    # 특정 역(예: 서울역)을 기준으로 노선별 구분을 시각적으로 강조
    colors = df.apply(
        lambda row: '#0066CC' if row['역명'] == '서울역' else '#26A65B',
        axis=1
    )
    
    # 상위 10개 역의 승하차 총합을 막대 그래프로 시각화
    plt.figure(figsize=(12,6))
    plt.bar(df['역명'], df['승하차총합'], color=colors)
    # 그래프 해석을 돕기 위한 제목 및 축 라벨 설정
    plt.title('상위 10개 역 승하차 총합')
    plt.xlabel('역명')
    plt.ylabel('승하차총합')
    plt.xticks(rotation=45)

    # 노선별 색상 구분에 대한 범례 추가
    legend_patches = [
        mpatches.Patch(color='#0066CC', label='1호선'),
        mpatches.Patch(color='#26A65B', label='2호선')
    ]
    plt.legend(handles=legend_patches)
    plt.tight_layout()
    plt.show()
