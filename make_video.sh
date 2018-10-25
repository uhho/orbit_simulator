echo "Reading frames from ${1}"
echo "Writing to ${2}"
cat $1 | ffmpeg -r 16 -f image2pipe -i - -b:v 1000k -c:v mpeg4 $2
