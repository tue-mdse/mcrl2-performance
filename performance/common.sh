# needed by gnuplot for finding the font file
PLOTSIZE="800,480"

function ensure_dir
{
  if [ ! -d $1 ] ; then
    rm -f $1
    mkdir $1
  fi
}

function generate_awk_script
{
  # Generate the AWK script that improves the SVG file
  # An array of file names is given in FILE_ARRAY
  # An array of titles is given in TITLE_ARRAY
  # The first argument of this script is the relative path from the
  # target SVG file to the CSS style sheet perf.css

  echo "BEGIN { BC = 0; flag = 0}" > tmp.awk

  # Fix SVG style errors introduced by Gnuplot
  echo "/color:rgb/ { sub(/color:rgb/, \"stroke:rgb\") }" >> tmp.awk

  for (( I=0 ; I < ${#FILE_ARRAY[*]} ; ++I )) ; do
    PREFIX=""
    if [ "${TITLE_ARRAY[I]}" != "" ] ; then
      PREFIX="${TITLE_ARRAY[I]}: "
    fi
    echo "
      BC == $I && /<use xlink:href='[^']*' transform='[^']*' style='[^']*'\/>/ {
        if ((getline line < \"${FILE_ARRAY[I]}\") > 0) {
          sub(/\\t/, \", \", line)
          sub(/\/>/, sprintf(\" title='$PREFIX%s'/>\", line))
        } else {
          flag = 1
        }
      }" >> tmp.awk
  done

  echo "
    { print }

    FNR == 1 { 
      print \"<?xml-stylesheet href=\\\"$1/perf.css\\\" type=\\\"text/css\\\"?>\"
    }

    flag == 1 {
      flag = 0
      BC++
    }" >> tmp.awk
}
