# times-dash
Dashboard for visualisation of TIMES model data, built using plotly-dash

The interactive dashboard features a drag and drop section where users can upload TIMES data outputs in a standard format, the code can be adapted to different formats but the current required structure is an Excel file with several sheets for each dataset. The names of the sheets and the columns of interest must then be changed in the code. Once updated the code will create a dictionary of dataframes from each of the sheets, which are then used to plot the graphs.

The code itself is quite fluid such that the types of graph, the data for the graphs and the positioning of the graphs are all easily adaptable, areas that are particularly adaptable are signposted in the commenting of the code.

Note that the current code has several filters and data cleaning features specific to the data set that it was developed for, these are clearly commented and thus easily adaptable, deletable or replaceable.

This repository also features a previous prototype which also takes CSV inputs and has several features such as the generation of tabs and dropdowns to toggle units and scenarios. These features can be easily adapted for the most recent version, so the older version has been left for reference and adaptation to upgrade the current working version.

If you have any queries feel free to contact me.
