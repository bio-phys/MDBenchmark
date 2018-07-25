Updated plotting interface. `mdbenchmark analyze --plot` is not deprecated. Use `mdbenchmark plot` instead.

The new workflow for plotting data is as follows:

1) Use `mdbenchmark analyze` to generate a CSV output file.
2) Use `mdbenchmark plot --csv name_of_generated_file.csv` to plot the data.

Consult `mdbenchmark <command> --help` for options to filter your data accordingly.