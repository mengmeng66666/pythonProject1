import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Radar, TreeMap
from pyecharts import options as opts
import re
import string
import streamlit.components.v1 as components

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def remove_punctuation(text):
    all_punctuations = string.punctuation + '！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟⚗｢｣､、〃》「」『』【】〔〕〖〗📐 indeb‘’‛“”„‟…‧﹏。 '
    table = str.maketrans('', '', all_punctuations)
    return text.translate(table)
def tokenize_and_count(text, top_n=20):
    words = [word for word in jieba.lcut(text) if word and not word.isspace()]
    word_counts = Counter(words)
    return word_counts.most_common()

def fetch_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        return text
    except requests.RequestException as e:
        st.error(f"无法抓取URL: {e}")
        return None
def ensure_valid_format(word_freq):
    valid_data = []
    for item in word_freq:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            valid_data.append(item)
        else:
            print(f"Invalid data format: {item}")
    return valid_data
def draw_wordcloud(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        wordcloud = WordCloud()
        wordcloud.add("", word_freq, word_size_range=[20, 100])
        return wordcloud
    except Exception as e:
        print(f"Error drawing word cloud: {e}")
        return None
def draw_bar(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        bar = Bar()
        bar.add_xaxis([word for word, _ in word_freq])
        bar.add_yaxis("词频", [count for _, count in word_freq])
        return bar
    except Exception as e:
        print(f"Error drawing bar chart: {e}")
        return None

def draw_line(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        line = Line()
        line.add_xaxis([word for word, _ in word_freq])
        line.add_yaxis("词频", [count for _, count in word_freq])
        return line
    except Exception as e:
        print(f"Error drawing line chart: {e}")
        return None

def draw_pie(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        pie = Pie()
        pie.add("", word_freq)
        return pie
    except Exception as e:
        print(f"Error drawing pie chart: {e}")
        return None
def draw_scatter(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        scatter = Scatter()
        scatter.add_xaxis([word for word, _ in word_freq])
        scatter.add_yaxis("词频", [count for _, count in word_freq])
        return scatter
    except Exception as e:
        print(f"Error drawing scatter plot: {e}")
        return None
def draw_radar(word_freq, top_n=6):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq or len(word_freq) < top_n:
        return None

    try:
        # Select the top N words for radar chart
        top_words = word_freq[:top_n]
        max_value = max([count for _, count in top_words])

        radar = Radar()
        # Define schema for each word as a dimension
        radar_schema = [{"name": word, "max": max_value} for word, _ in top_words]
        radar.add_schema(schema=radar_schema)

        # Prepare data for the radar chart
        radar_data = [
            {
                "value": [count for _, count in top_words],
                "name": "词频"
            }
        ]
        radar.add("", radar_data, areastyle_opts=opts.AreaStyleOpts(opacity=0.1))

        return radar
    except Exception as e:
        print(f"Error drawing radar chart: {e}")
        return None

def draw_treemap(word_freq):
    word_freq = ensure_valid_format(word_freq)
    if not word_freq:
        return None

    try:
        treemap = TreeMap()
        data = [{"name": word, "value": count} for word, count in word_freq]
        treemap.add("", data)
        return treemap
    except Exception as e:
        print(f"Error drawing treemap: {e}")
        return None

def main():
    st.title("文本分析与可视化")

    st.sidebar.header("设置")
    url = st.sidebar.text_input("输入文章URL")
    min_freq = st.sidebar.slider("过滤低频词 (最小频率)", 1, 100, 1)
    chart_type = st.sidebar.selectbox("选择图表类型",
                                      ["词云", "柱状图", "折线图", "饼图", "散点图", "雷达图", "树状图"])

    if url:
        st.write(f"正在分析: [{url}]({url})")

        text = fetch_text_from_url(url)
        if text is None:
            return

        text_cleaned = remove_html_tags(text)
        text_cleaned = remove_punctuation(text_cleaned)

        word_freq = tokenize_and_count(text_cleaned)
        filtered_word_freq = [(word, count) for word, count in word_freq if count >= min_freq]

        top_20_words = filtered_word_freq[:20]
        st.write("词频最高的20个词:")
        for word, count in top_20_words:
            st.write(f"{word}: {count}")

        chart = None
        if chart_type == "词云":
            chart = draw_wordcloud(filtered_word_freq)
        elif chart_type == "柱状图":
            chart = draw_bar(filtered_word_freq)
        elif chart_type == "折线图":
            chart = draw_line(filtered_word_freq)
        elif chart_type == "饼图":
            chart = draw_pie(filtered_word_freq)
        elif chart_type == "散点图":
            chart = draw_scatter(filtered_word_freq)
        elif chart_type == "雷达图":
            chart = draw_radar(filtered_word_freq)
        elif chart_type == "树状图":
            chart = draw_treemap(filtered_word_freq)

        if chart:
            try:
                chart_html = chart.render_embed()
                components.html(chart_html, height=600)
            except Exception as e:
                st.error(f"图表渲染失败: {e}")
                st.write("尝试使用备用方法显示图表:")
                st.write(chart.render_notebook())
        else:
            st.write("没有足够的数据来生成图表。请尝试调整参数或选择其他图表类型。")

if __name__ == "__main__":
    main()