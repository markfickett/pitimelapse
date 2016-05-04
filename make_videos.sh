#!/bin/bash
set -e

SRC=/mnt/data/timelapse
DST=~/public_html
SIZE=1280
WATERMARK=markfickett.com

for project in `ls $SRC`
do
  echo $project
  if [ $project = 'var' ]
  then
    continue
  fi
  RESIZED_DIR=${SRC}/var/${project}_${SIZE}
  mkdir -p $RESIZED_DIR
  for full_res in `ls -1 $SRC/$project/*/*/*/*`
  do
    LOCAL=`echo ${full_res#$SRC/$project/} | tr '/' '_'`
    RESIZED=$RESIZED_DIR/$LOCAL
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
          $RESIZED
    fi
  done

  OUT_VIDEO=$DST/$project/full.mp4
  if [ ! -f $OUT_VIDEO -o \( $full_res -nt $OUT_VIDEO \) ]
  then
    ffmpeg -r 15 -y \
        -pattern_type glob -i $RESIZED_DIR/'*'.jpg \
        -c:v libx264 $OUT_VIDEO
  fi
done
