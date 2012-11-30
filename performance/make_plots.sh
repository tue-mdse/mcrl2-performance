#!/bin/bash

DATADIR=data
CASEDIR=cases
PLOTDIR=plots

PLOTSTYLE=plotstyle.plt
PLOTCMD=plotcmd.plt
PLOTHEADER=plotheader.plt

source common.sh

function generate_plot_cmd
{
  # Generate the plot command for the Gnuplot script
  # An array of file names is given in FILE_ARRAY
  # An array of titles is given in TITLE_ARRAY
  FIRST=1
  for (( I=0 ; I < ${#FILE_ARRAY[*]} ; ++I )) ; do
      if (( $FIRST )) ; then
        echo -ne "plot \"${FILE_ARRAY[I]}\" title \"${TITLE_ARRAY[I]}\"" > $PLOTCMD
        FIRST=0
      else
        echo -ne ", \"${FILE_ARRAY[I]}\" title \"${TITLE_ARRAY[I]}\"" >> $PLOTCMD
      fi
  done
}

function fill_arrays_tool
{
  if [ "$RANGE" == "all" ] ; then
    # data for plots includes all measurements
    FILE_ARRAY=( )
    TITLE_ARRAY=( )
    I=0
    for CASE in `ls $CASEDIR/*.mcrl2` ; do
      CASE=${CASE#$CASEDIR/}
      CASE=${CASE%.mcrl2}
      FILE_ARRAY[$I]="$DATADIR/$DIM1/$DIM2/$CASE.$EXT"
      TITLE_ARRAY[$I]="$CASE"
      let "++I"
    done
  elif [ "$RANGE" == "recent" ] ; then
    # data for plots includes most recent measurements only
    FILE_ARRAY=( )
    TITLE_ARRAY=( )
    I=0
    for CASE in `ls $CASEDIR/*.mcrl2` ; do
      CASE=${CASE#$CASEDIR/}
      CASE=${CASE%.mcrl2}
      FILE=$DATADIR/$DIM1/$DIM2/$CASE.$EXT
      
      tail -n 100 $FILE > $FILE.rec
      FILE_ARRAY[$I]="$FILE.rec"
      TITLE_ARRAY[$I]="$CASE"
      let "++I"
    done
  fi
}

function fill_arrays_case
{
  if [ "$RANGE" == "all" ] ; then
    # data for plots includes all measurements
    FILE_ARRAY=( `find $DATADIR/$DIM2 -name $DIM1.$EXT` )
    TITLE_ARRAY=( )
    for (( I=0 ; I < ${#FILE_ARRAY[*]} ; ++I )) ; do
      # $FILE is of the form: $DATADIR/DIM2/OPTIONS/DIM1.EXT
      # $OPTS will contain just OPTIONS
      OPTS=${FILE_ARRAY[I]#$DATADIR/$DIM2/} # remove "$DATADIR/DIM2/"
      OPTS=${OPTS%/$DIM1.$EXT} # remove "/DIM1.EXT"
      OPTS=${OPTS//__/ } # replace every "__" by " "
      TITLE_ARRAY[$I]="${OPTS//\// }" # replace all slashes by spaces
    done
  elif [ "$RANGE" == "recent" ] ; then
    # data for plots includes most recent measurements only
    # Ignore the innerc results for the recent plots. This rewriter is not available anymore.
    FILE_ARRAY=( `find $DATADIR/$DIM2 -path "$DATADIR/$DIM2/-rinnerc" -prune -o -path "$DATADIR/$DIM2/-pquantifier-all__-rinnerc" -prune -o -name $DIM1.$EXT -print` )
    TITLE_ARRAY=( )
    for (( I=0 ; I < ${#FILE_ARRAY[*]} ; ++I )) ; do
      # $FILE is of the form: $DATADIR/DIM2/OPTIONS/DIM1.EXT
      # $OPTS will contain just OPTIONS
      OPTS=${FILE_ARRAY[I]#$DATADIR/$DIM2/} # remove "$DATADIR/DIM2/"
      OPTS=${OPTS%/$DIM1.$EXT} # remove "/DIM1.EXT"
      OPTS=${OPTS//__/ } # replace every "__" by " "
      TITLE_ARRAY[$I]="${OPTS//\// }" # replace all slashes by spaces

      tail -n 100 ${FILE_ARRAY[I]} > ${FILE_ARRAY[I]}.rec
      FILE_ARRAY[$I]="${FILE_ARRAY[I]}.rec"
    done
  fi
}

function make_plots
{
  DIM1_TYPE="$1"
  DIM1="$2"
  if [ "$DIM1_TYPE" == "tool" ] ; then
    LIST=`ls $DATADIR/$DIM1`
  elif [ "$DIM1_TYPE" == "case" ] ; then
    LIST=`ls $DATADIR`
  else
    return
  fi

  for DIM2 in $LIST ; do
    ensure_dir $OUTDIR/$DIM1
    ensure_dir $OUTDIR/$DIM1/$DIM2

    for EXT in perf mem ; do
  
      if [ "$EXT" == "perf" ] ; then
        OUTBASE="time"
        YLAB="User + Sys time (sec)"
        TITLE="Time consumption"
      else # "$EXT" == "mem"
        OUTBASE="memory"
        YLAB="Heap peak memory (MB)"
        TITLE="Memory usage"
      fi

      for RANGE in recent all ; do
        ensure_dir $OUTDIR/$DIM1/$DIM2/$RANGE

        if [ "$DIM1_TYPE" == "tool" ] ; then
          fill_arrays_tool
          echo -e "set title \"$TITLE of $DIM1 ${DIM2//__/ }\"" > $PLOTHEADER
        else
          fill_arrays_case
          echo -e "set title \"$TITLE of $DIM2 on $DIM1\"" > $PLOTHEADER
        fi
        echo -e "set ylabel \"$YLAB\"" >> $PLOTHEADER

        generate_plot_cmd

        for OUTEXT in png svg ; do
          OUTFILE="$OUTDIR/$DIM1/$DIM2/$RANGE/$OUTBASE.$OUTEXT"
          TMPFILE="tmp.$OUTEXT"
          if [ "$OUTEXT" == "svg" ] ; then
            GNUPLOT_HDR="set terminal svg size $PLOTSIZE fsize 10"
          else # "$OUTEXT" == "png"
            GNUPLOT_HDR="set terminal png small size $PLOTSIZE"
          fi

          ( echo -e "$GNUPLOT_HDR\nset output \"$TMPFILE\"" ; cat $PLOTHEADER $PLOTSTYLE $PLOTCMD ) > tmp.plt
          gnuplot tmp.plt

          if [ "$OUTEXT" == "png" ] ; then
            mv $TMPFILE $OUTFILE
          else # $OUTEXT == "svg"
            generate_awk_script "../../../../.."
            
            awk -f tmp.awk $TMPFILE > $OUTFILE

            rm -f tmp.awk $TMPFILE
          fi
          rm -f tmp.plt
        done # for OUTEXT
      done # for RANGE
    done # for EXT
  done # for DIM2
}

ensure_dir $PLOTDIR

OUTDIR=$PLOTDIR/cases
ensure_dir $OUTDIR
for c in `ls $CASEDIR/*.mcrl2` ; do
  c=${c#$CASEDIR/}
  make_plots "case" ${c%.mcrl2}
done

OUTDIR=$PLOTDIR/tools
ensure_dir $OUTDIR
for TOOL in `ls $DATADIR` ; do
  if [ -d "$DATADIR/$TOOL" ] ; then
    make_plots "tool" $TOOL
  fi
done

# Clean up
rm -f $PLOTCMD $PLOTHEADER `find $DATADIR -name *.rec`
