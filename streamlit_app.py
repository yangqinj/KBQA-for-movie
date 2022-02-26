"""
@author: Qinjuan Yang
@time: 2022-02-26 15:36
@desc: 
"""
import streamlit as st

from app.bot import QABot
from config import Config


@st.cache(allow_output_mutation=True)
def get_bot():
    return QABot(Config.fuseki_endpoint,
                 Config.dict_paths)


bot = get_bot()
st.title("豆瓣TOP250电影 KBQA Demo")

st.text_area('Demo支持的问题类型', """1. 某个演员出演了什么电影？
2. 某个电影有哪些演员参演？
3. 评分为X/以上/以上/之间的电影有哪些？
4. 某个人导演的评分为X/以上/以下/之间的电影
5. 演员A和演员B共同出演的电影？
6. 某个演员即出演又是导演的电影？
7. 某个国家上映的电影
8. 某个演员出演了哪些类型的电影
9. 某个演员出演的某个类型的电影有哪些
10. 某个演员出演了多少部电影""", height=270)

question = st.text_input("请输入你的问题：")
if question:
    st.text(bot.answer(question))
