mysqlcmd="mysql"

which $mysqlcmd > /dev/null
if [ $? -ne 0 ] ; then
       mysqlcmd="/usr/local/mysql/bin/mysql"
fi

echo $mysqlcmd

tmpsqlfile="/tmp/mysql_clear_tables.sql"
touch $tmpsqlfile
echo "use palaranlocal; \n drop table if exists histogram;" > $tmpsqlfile
$mysqlcmd -u root -p < $tmpsqlfile
rm $tmpsqlfile


