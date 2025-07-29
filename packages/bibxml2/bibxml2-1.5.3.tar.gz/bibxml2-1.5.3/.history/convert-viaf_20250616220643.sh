mkfifo viaf.pipe
exec 3>viaf.pipe # open file descriptor 3 writing to the pipe
marcxml2 -o viaf.parquet viaf.pipe &
wait %1
echo '<foo>' > viaf.pipe
gzcat viaf-20240804-clusters-marc21.xml.gz | head -n 3 | sed 's|^[^<]*||' >> viaf.pipe
echo '<foo>' > viaf.pipe
exec 3>&- # close file descriptor 3
rm viaf.pipe