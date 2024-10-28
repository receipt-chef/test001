from flask import Flask, render_template
import pandas as pd
import folium
from folium import plugins
from clovax import ClovaX
import time

app = Flask(__name__)

# 데이터 불러오기
station_df = pd.read_excel('data/서울시 지하철역 주소,위도,경도 ver0.7.xlsx')
restroom_df = pd.read_csv('data/역별 화장실 주소.csv')
편의점_df = pd.read_csv('data/편의점 주소.csv')

@app.route('/')
def index():
    # Folium 맵 생성
    mapping = folium.Map(location=[station_df['위도'].mean(), station_df['경도'].mean()], zoom_start=14)

    # 그룹별 나누기
    fg = folium.FeatureGroup(name='편의시설 보기')
    mapping.add_child(fg)

    restroom_group = folium.FeatureGroup(name='화장실')
    mapping.add_child(restroom_group)

    info_group = folium.FeatureGroup(name='편의점')
    mapping.add_child(info_group)

    # 마커 추가 함수
    def add_markers(df, color, icon, group=None):
        for n in df.index:
            if icon == 'subway':
                folium.Marker(
                    [df['위도'][n], df['경도'][n]],
                    popup='<h2><a href="/info/'+df['역명'][n]+'">주변정보</a></h2>',
                    icon=folium.Icon(color=color, icon=icon, prefix='fa'),
                    tooltip=df['역명'][n]
                ).add_to(mapping)
            elif icon =='store':
                folium.Marker([df['위도'][n], df['경도'][n]], 
                            popup = '<h1>편의점</h1><br>information',
                            #df['역명'][n],
                            icon = folium.Icon(
                                color=color,
                                icon=icon,
                                prefix ='fa'),
                            tooltip = df['이름'][n]
                            ).add_to(mapping)             
            else:
                folium.Marker(
                    [df['위도'][n], df['경도'][n]],
                    popup=df['이름'][n],
                    icon=folium.Icon(color=color, icon=icon, prefix='fa')
                ).add_to(group)

    add_markers(station_df, 'purple', 'subway')  # 지하철역
    # add_markers(restroom_df, 'blue', 'restroom', restroom_group)  # 화장실
    # add_markers(편의점_df,'red','store',info_group) # 편의점

    # 기본적으로 보이지 않도록 설정
    # layer1 = folium.TileLayer(tiles=None, name="지하철역", show=False, attribution="Group 1 Data").add_to(mapping)
    # layer2 = folium.TileLayer(tiles=None, name="화장실", show=False, attribution="Group 2 Data").add_to(mapping)
    # layer3 = folium.TileLayer(tiles=None, name="편의점", show=False, attribution="Group 3 Data").add_to(mapping)

    # 미니맵 추가
    minimap = plugins.MiniMap()
    mapping.add_child(minimap)

    plugins.LocateControl().add_to(mapping)
    # 초기 로딩 시 그룹들을 비활성화
    mapping.keep_in_front()
    folium.LayerControl(collapsed=False).add_to(mapping)

    # HTML로 맵 출력
    return mapping._repr_html_()

@app.route('/info/<name>')
def information(name):
  c = ClovaX()
  c.get_cookie("clova-x.naver.com_cookies.txt")
  # log = c.start("Hello world!")
  # print(log["text"])
  result = c.start(name + "역 주변정보를 알려줘.")
  print(result['text'])
  # result = None
  # while result is None:
  #     try:
  #       result = eval(c.conversation(name + "역 주변정보를 알려줘."))
  #     except Exception:
  #       time.sleep(1)
  
  return render_template("information.html", name = name, result = result['text'])
    
if __name__ == '__main__':
    #app.run(debug=True)
    app.run()