conf=$1
keywords=$2
hostname=$3

if [[ -z "${conf}" || -z "${keywords}" || -z "${hostname}" ]]; then
    echo "Contoh: $0 live.ini \"pupuk cair\" www.bukalapak.com"
    exit 1
fi

prefix_file="${keywords/ /-}_${hostname}"
csv_file="${prefix_file}.csv"
log_file="${prefix_file}.log"

~/env/bin/scrapy runspider crawler.py \
    -a keywords="${keywords}" \
    -a hostname=$hostname \
    -O $csv_file \
    --logfile=$log_file

~/env/bin/python csv2db.py $conf --csv-file=$csv_file
