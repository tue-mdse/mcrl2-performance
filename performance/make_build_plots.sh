#!/bin/bash

DATADIR=build_data
BDATAFILE=$DATADIR/build.perf
CDATAFILE=$DATADIR/cbuild.perf
PLOTDIR=build_plots
PLOTSTYLE=plotstyle.plt

source common.sh

ensure_dir $PLOTDIR

for RANGE in recent all ; do
  OUTDIR="$PLOTDIR/$RANGE"
  ensure_dir $OUTDIR

  if [ "$RANGE" == "all" ] ; then
    BINFILE=$BDATAFILE
    CINFILE=$CDATAFILE
  else
    CINFILE=ctmp.perf
    tail -n 100 $CDATAFILE > $CINFILE
  fi    

  for OUTEXT in png svg ; do
    OUTFILE="$OUTDIR/build.$OUTEXT"
    TMPFILE="tmp.$OUTEXT"

    # Generate Gnuplot script
    if [ "$OUTEXT" == "svg" ] ; then
      echo -e "set terminal svg size $PLOTSIZE fsize 10" > tmp.plt
    else # "$OUTEXT" == "png"
      echo -e "set terminal png font luxisr 10 size $PLOTSIZE" > tmp.plt
    fi
    echo -e "set output \"$TMPFILE\"
    set title \"Time needed for building the toolset\"
    set ylabel \"User + Sys time (sec)\"" >> tmp.plt
    cat $PLOTSTYLE >> tmp.plt
    if [ "$RANGE" == "all" ] ; then
      echo -e "plot \"$BINFILE\" title \"bjam\", \"$CINFILE\" title \"cmake\"" >> tmp.plt
    else
      echo -e "plot \"$CINFILE\" title \"cmake\"" >> tmp.plt
    fi

    # Run Gnuplot
    gnuplot tmp.plt

    # Install generated image in right directory
    if [ "$OUTEXT" == "png" ] ; then
      mv $TMPFILE $OUTFILE
    else # $OUTEXT == "svg"
      FILE_ARRAY=( $BINFILE $CINFILE )
      TITLE_ARRAY=( "bjam" "cmake" )
      generate_awk_script "../.."
      
      awk -f tmp.awk $TMPFILE > $OUTFILE

      rm -f tmp.awk $TMPFILE
    fi

    rm -f tmp.plt
  done # for OUTEXT

  rm -f {b,c}tmp.perf
done # for RANGE
