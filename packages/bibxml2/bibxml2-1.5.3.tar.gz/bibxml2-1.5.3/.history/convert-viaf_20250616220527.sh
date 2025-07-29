mkfifo viaf.pipe
exec 3>viaf.pipe # open file descriptor 3 writing to the pipe
marcxml2 -o viaf.parquet viaf.pipe &

# < P tail -n +1 -f | program
echo some stuff > P
cat more_stuff.txt > P
exec 3>&- # close file descriptor 3

mkfifo -m 0666 viaf.pipe
python 
echo  