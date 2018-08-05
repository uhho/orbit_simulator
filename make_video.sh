echo "Reading frames from ${1}"
echo "Writing to ${2}"
cat $1 | ffmpeg -r 16 -f image2pipe -vcodec mjpeg -analyzeduration 100M -probesize 109M -i - -vcodec libx264 $2