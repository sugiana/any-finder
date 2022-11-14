import os
import sys
from math import ceil
import numpy as np
import pandas as pd
import streamlit as st
from annotated_text import annotated_text


def price(n):
    s = '{:0,}'.format(int(n))
    s = s.replace(',', '.')
    return f'Rp {s}'


def to_annotated_text(s, keywords):
    r = []
    keywords = keywords.lower()
    length = len(keywords)
    while True:
        pos = s.lower().find(keywords)
        if pos < 0:
            if s:
                r += [s]
            break
        r += [s[:pos]]
        r += [(s[pos:pos+length],)]
        s = s[pos+length:]
    annotated_text(*r)


csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'all.csv',
            'http://warga.web.id/files/dijual/all.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = ['title', 'price', 'image', 'description', 'url']
DEFAULT = dict(price=10000)
HOSTS = [
    'www.bukalapak.com',
    'www.tokopedia.com']


@st.cache(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()

price_step = 10000
price_min = int(orig_df.price.min() / price_step + 1) * price_step
price_max = int(orig_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df = df.sort_values(by=['price'])

# Sembunyikan nomor dan price
css = """
    <style>
    .block-container {max-width: 100rem}
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

st.title('Temukan')
search = st.text_input('Cari')
df = df[
        df.title.str.contains(search, na=False, case=False) |
        df.description.str.contains(search, na=False, case=False)]

if st.checkbox('Harga tertinggi'):
    price_choice = st.slider(
            'Rp', price_min, price_max, DEFAULT['price'], price_step)
    df = df[df.price <= price_choice]

if st.checkbox('Sumber'):
    host_choice = st.selectbox('Situs', HOSTS)
    df = df[df.url.str.contains(host_choice, na=False)]

limit = 20
row_count = len(df)
page_count = ceil(row_count / limit)
if page_count > 99:
    page_count = 99
page_list = [x+1 for x in range(page_count)]
page_choice = st.selectbox('Halaman', page_list) or 1

df = df.sort_values(by=['price', 'title'], ascending=[True, True])
df = df.replace(np.nan, '', regex=True)
st.write(f'Ketemu {row_count}')

offset = (page_choice - 1) * limit
df = df[offset:offset+limit]

for i in df.index:
    title = df['title'][i]
    url = df['url'][i]
    price_rp = price(df['price'][i])
    col1, mid, col2 = st.columns([3, 1, 17])
    with col1:
        st.image(df['image'][i], width=200)
    with col2:
        st.write(f'[{title}]({url})')
        st.write(f'{price_rp}')
        if search:
            to_annotated_text(df['description'][i], search)
        else:
            st.write(df['description'][i])
