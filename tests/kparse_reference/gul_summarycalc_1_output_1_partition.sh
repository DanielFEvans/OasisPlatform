#!/bin/bash

rm -R -f output/*
rm -R -f fifo/*
rm -R -f work/*

mkfifo fifo/gul_P1

mkfifo fifo/gul_S1_summary_P1
mkfifo fifo/gul_S1_summarysummarycalc_P1
mkfifo fifo/gul_S1_summarycalc_P1



# --- Do insured loss kats ---


# --- Do ground up loss kats ---

kat fifo/gul_S1_summarycalc_P1 > output/gul_S1_summarycalc.csv & pid1=$!

# --- Do insured loss computes ---


# --- Do ground up loss  computes ---

summarycalctocsv < fifo/gul_S1_summarysummarycalc_P1 > fifo/gul_S1_summarycalc_P1 &

tee < fifo/gul_S1_summary_P1 fifo/gul_S1_summarysummarycalc_P1  > /dev/null & pid2=$!
summarycalc -g -1 fifo/gul_S1_summary_P1  < fifo/gul_P1 &

eve 1 1 | getmodel | gulcalc -S100 -L100 -r -c - > fifo/gul_P1  &

wait $pid1 $pid2 


rm fifo/gul_P1

rm fifo/gul_S1_summary_P1
rm fifo/gul_S1_summarysummarycalc_P1
rm fifo/gul_S1_summarycalc_P1


