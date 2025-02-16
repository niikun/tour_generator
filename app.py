import os
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from typing import Optional
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, tool
import googlemaps

load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
os.environ["HF_TOKEN"] = os.getenv('HUGGINGFACE_TOKEN')


@tool
def get_travel_duration(start_location: str, destination_location: str, transportation_mode: Optional[str] = None) -> str:
    """Gets the travel time between two places.
        Args:
            start_location: the place from which you start your ride
            destination_location: the place of arrival
            transportation_mode: The transportation mode, in 'driving', 'walking', 'bicycling', or 'transit'. Defaults to 'driving'.
        Returns:
            The travel time between the two places.
        
    """

    gmaps = googlemaps.Client(key=google_api_key)
    if transportation_mode is None:
        transportation_mode = "driving"
    try:
        directions_result = gmaps.directions(
            start_location,
            destination_location,
            mode=transportation_mode,
            departure_time=datetime.now(),
        )
        if len(directions_result) == 0:
            return "指定された移動手段では、これらの場所間の経路が見つかりませんでした。"
        return directions_result[0]["legs"][0]["duration"]["text"]
    except Exception as e:
        return str(e)

search_tool = DuckDuckGoSearchTool()
agent = CodeAgent(tools=[get_travel_duration, search_tool], model=HfApiModel(token=os.getenv('HUGGINGFACE_TOKEN')), additional_authorized_imports=["datetime"])

def main():
    st.title("いろんな都市周辺の1日旅行プラン提案アプリ")
    city = st.text_input("どの町を希望しますか？")
    option = st.selectbox("移動手段を選択してください", ["徒歩", "自転車", "車", "バス", "電車"])
    if city == "":
        st.stop()

    if st.button("旅行プランを提案"):
        query = f"{city}周辺で素敵な1日旅行のプランをいくつかの場所と時間付きで提案してもらえますか？市内でも郊外でも構いませんが、1日で回れる範囲がいいです。日本語で出力してください。{option}だけで移動します。"
        with st.spinner("提案を生成中..."):
            try:
                response = agent.run(query)
                st.code(response, language='text')
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
