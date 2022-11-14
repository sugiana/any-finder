Any Finder
==========

Ini adalah *web crawler* berbagai marketplace. Mulai pemasangan::

    $ python3.10 -m venv ~/env
    $ ~/env/bin/pip install --upgrade pip wheel
    $ ~/env/bin/pip install -r requirements.txt
    $ cp development.ini live.ini

Buat database-nya dan sesuaikan file konfigurasi ``live.ini``. Kemudian buat
tabelnya::

    $ ~/env/bin/python init_db.py live.ini


Crawler
-------

Untuk situs yang tidak menggunakan AJAX maka bisa diunduh menggunakan Scrapy::

    $ bash crawler.bash live.ini "pupuk cair" www.bukalapak.com

Hasilnya bisa dilihat di tabel ``product``.

Sedangkan situs yang menggunakan AJAX maka diunduh menggunakan Selenium, ini butuh
antarmuka grafis karena Google Chrome akan dipanggil::

    $ ~/env/bin/python selenium_crawler.py --tmp-dir=/tmp --keywords="pupuk cair" --hostname=www.tokopedia.com

Proses tersebut sebatas unduh file HTML saja. Untuk pemilahan (*parsing*) tetap
menggunakan Scrapy::

    $ ~/env/bin/python helper_parser.py live.ini --tmp-dir=/tmp --keywords="pupuk cair"


Web dengan Streamlit
--------------------

Kita bisa menampilkan seluruh file CSV menggunakan
`Streamlit <https://streamlit.io>`_. Pasang paket yang dibutuhkan::

    $ ~/env/bin/pip install -r streamlit-requirements.txt

Lalu satukan seluruh file CSV menjadi ``all.csv``::

    $ ~/env/bin/python csv_concat.py

Aktifkan web server Streamlit::

    $ ~/env/bin/streamlit run web.py

Selamat mencoba.
