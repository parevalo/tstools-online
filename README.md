# tstools-online
Visualize time series obtained from Google Earth Engine and run pyccd on them.

In order to use the Google Earth Engine API you need to have an active account. 
Check the installation instructions to set up the environment and authentication credentials.

Widget and map interaction should work right away with a classic jupyter notebook. 
In order to use them with a JupyterLab notebook, four extensions are required. 
They can be installed with the commands below.

    jupyter labextension install jupyter-leaflet
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    jupyter labextension install bqplot
    jupyter labextension install qgrid


This repo has similar requirements to the 
[measures_collection](https://github.com/parevalo/measures_collector), so if 
you created a conda environment using that project's requirements file, you
don't need to create a new one.
