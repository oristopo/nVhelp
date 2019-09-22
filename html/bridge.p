# gnuplot commands to generate log(2) plot of im vs R2 for impedance bridge
set xrange [0:1000]
set yrange [-4:2.5]
set xtics 50
set ytics 0.5
set grid xtics ytics
set ylabel "arbitrarily scaled 50 Ohm response"
set xlabel "unknown R2 in Ohms"
set title "unbalanced 50 Ohm bridge"
p (x<50)?8*sqrt((50-x)/(600 + 4*x)) : -8*sqrt((x-50)/(600 + 4*x)) title "meter current i_m"
