mysqlcmd="mysql"

which $mysqlcmd > /dev/null
if [ $? -ne 0 ] ; then
       mysqlcmd="/usr/local/mysql/bin/mysql"
fi

echo $mysqlcmd

echo "${VURVE_SOPHIE_BASE}/sophie/lib/bigbrother/pickles"
cd  "${VURVE_SOPHIE_BASE}/sophie/lib/bigbrother/pickles"
if [ $? -eq 1 ] ; then
	echo "Either the folder does not exist or VURVE_SOPHIE_BASE points to the wrong place"
	exit 1
else 
	#Remove the pickes
	echo "Will delete "
	ls
	read
	rm * 
fi

tmpsqlfile="/tmp/mysql_clear_tables.sql"
touch $tmpsqlfile
echo "use palaranlocal; \n drop table if exists ClickSession; \n drop table if exists SessionMkg; \n drop table if exists Histogram; \n drop table if exists StoreMap;" > $tmpsqlfile
$mysqlcmd -u root -p < $tmpsqlfile
rm $tmpsqlfile


