#!/bin/bash
set -e

SRC=/mnt/data/timelapse
DST=~/public_html
SIZE=1280
WATERMARK=markfickett.com

if [ "$1" = "daily" ]
then
  # If SLICE is specified, only process the input from this offset to the end of
  # the input. 5.76s = 24 hours lapsed (25fps playback of 10m interval photos).
  SLICE="-sseof -5.76"
  VIDEONAME=daily
else
  VIDEONAME=full
fi

for project in `ls $SRC`
do
  echo $project
  if [ $project = 'var' -o $project = 'archive' ]
  then
    continue
  fi
  RESIZED_DIR=${SRC}/var/${project}_${SIZE}
  mkdir -p $RESIZED_DIR
  for full_res in `ls -1 $SRC/$project/*/*/*/*`
  do
    LOCAL=`echo ${full_res#$SRC/$project/} | tr '/' '_'`
    RESIZED=${RESIZED_DIR}/$LOCAL
    if [ -s $full_res -a ! -f $RESIZED ]
    then
      # sudo apt-get install imagemagick
      convert \
          -resize ${SIZE}x${SIZE} \
          -background '#0008' -fill white \
          -gravity west -size ${SIZE}x20 \
          caption:"${WATERMARK} ${LOCAL}" \
          $full_res \
          +swap \
          -gravity south \
          -composite \
          ${RESIZED}
    fi
  done

  OUT_VIDEO=$DST/$project/${VIDEONAME}.mp4

  if [ ! -f $OUT_VIDEO -o \( $full_res -nt $OUT_VIDEO \) ]
  then
    ffmpeg -r 15 -y $SLICE \
        -pattern_type glob -i $RESIZED_DIR/'*'.jpg \
        -c:v libx264 $OUT_VIDEO
  fi
done
