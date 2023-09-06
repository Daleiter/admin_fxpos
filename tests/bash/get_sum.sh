#!/bin/bash

#clear
echo  "Date (YYYY-mm-dd) " $1
#read DATE
DATE=$1
echo "ID shop" $2
id_shop=$2
#read id_shop

#check date $1 is date format $2 is date from input
datecheck() {
    local format="$1" d="$2"
    [[ "$(date "+$format" -d "$d" 2>/dev/null)" == "$d" ]]
}

if ! datecheck "%Y-%m-%d" $DATE; then
    echo "Формат дати не відповідає РРРР-ММ-ДД"; exit 1
fi
name=`psql -U postgres db_admin -At -c "select name from t_trade_point where trade_point=$id_shop;"`

echo $name" id shop - "$id_shop

ip_dpos='192.168.1.139'

#create date for db request
date_start=$DATE' 00:00:00'
date_stop=$DATE' 23:59:59'
outpos='каса||Z звіт по касі|POS Сума по чеках|POS Сума по позиціях\n'
ips=`psql -U postgres db_admin -At -c 'select ip from t_kassa where trade_point = '$id_shop' ;'`

for ip in $ips
do
tradepoint=`psql -U postgres db_admin -At -c "select trade_point from t_kassa where ip='$ip' and exist='1';"`
#ip_server=`psql -U postgres db_admin -At -c "select ip from t_server  where trade_point=$tradepoint and exist='1';"`
cashbox=`psql -U postgres db_admin -At -c "select cash_box from t_kassa where ip='$ip' and exist='1';"`


#test
#echo $date_start
#echo $date_stop

#function for get sum from dpos
get_sum_dpos(){
    dpos_sum_report=`psql -U postgres -d db_server -h $ip_dpos -At -c "select sum(sum_ready_money + sum_ready_credit) from pos.t_cash_register_report where id_shop = '$tradepoint' and id_workplace = '$cashbox' and report_time > '$date_start' and report_time < '$date_stop';"`
    dpos_sum_by_checks=`psql -U postgres -d db_server -h $ip_dpos -At -c "select sum(sum) from pos.t_check where date_operation = '$DATE' and id_workplace = '$cashbox' and id_shop = '$tradepoint' and dtype  = 0"`
    dpos_sum_by_check_articles=`psql -U postgres -d db_server -h $ip_dpos -At -c "select sum(sum) from pos.t_check_articles where id_check in (select id_check from pos.t_check where date_operation = '$DATE' and id_workplace = '$cashbox' and id_shop = '$tradepoint' and dtype  = 0) and id_shop = '$tradepoint' and id_workplace = '$cashbox';"`
    }

#function for get sum from kassa
get_sum_pos(){
    pos_sum_report=`psql -U postgres -d db_client -h $ip -At -c "select sum(sum_ready_money+sum_ready_credit) from pos.t_cash_register_report where date_trunc('day', date_change)='$DATE 00:00:00';"`
    pos_sum_by_checks=`psql -U postgres -d db_client -h $ip -At -c "select sum(sum) from pos.t_check where date_operation = '$DATE' and id_workplace = '$cashbox' and id_shop = '$tradepoint' and dtype  = 0"`
    pos_sum_by_check_articles=`psql -U postgres -d db_client -h $ip -At -c "select sum(sum) from pos.t_check_articles where id_check in (select id_check from pos.t_check where date_operation = '$DATE' and id_workplace = '$cashbox' and id_shop = '$tradepoint' and dtype  = 0) and id_shop = '$tradepoint' and id_workplace = '$cashbox';"`
}

get_sum_dpos

echo '========{ '$tradepoint'-'$cashbox' } - ( '$ip' )========'
echo 'Z звіт по dpos -        '$dpos_sum_report
echo 'DPOS Сума по чеках -    '$dpos_sum_by_checks
echo 'DPOS Сума по позиціях - '$dpos_sum_by_check_articles

ping -c3 $ip > /dev/null
        if [ $? -eq 0 ]; then

get_sum_pos
#outpos=$outpos'|'$cashbox'|'$pos_sum_report'|'$pos_sum_by_checks'|'$pos_sum_by_check_articles'\n'
#echo '========{ '$tradepoint'-'$cashbox' } - ( '$ip' )========'
echo 'Z звіт по касі -        '$pos_sum_report
echo 'POS Сума по чеках -     '$pos_sum_by_checks
echo 'POS Сума по позиціях -  '$pos_sum_by_check_articles
#outpos=`echo $outpos | column -s "|" -t`
#echo $outpos
else

echo "Каса без звʼязку"

fi
done
#echo -e $outpos | column -s "|" -t
#echo $outpos