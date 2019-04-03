# Step 1: Get miniconda

You need a working Python installation to use the tool. The easiest way to 
install the tool and dependencies is through the use of a conda virtual 
environment. If you don’t have conda installed, you can get a minimum version 
(miniconda). You can download the installers for your platform here: 

https://docs.conda.io/en/latest/miniconda.html

Choose the bash installer for python 3.7, 64-bits (unless you have a 32-bit system) 
and follow the following instructions depending on your OS:

- For macOS/Unix systems: Use bash installer
- For Windows: run the executable 

If you are asked if you want to append the conda installation to your PATH, 
answer 'Yes'.

In windows, once the installation finishes, open the 
‘Anaconda prompt’. Then issue the command:

conda install git

# Step 2: Clone the repo

Issue the following command in your Anaconda prompt:

`git clone https://github.com/parevalo/tstools-online`

Then cd into the tstools-online folder.

# Step 3: Create a conda environment

Inside the newly created folder, locate the requirements.yml file. Then
create a new conda environment using that file with the following command:

`conda env create -f requirements.yml`

The newly created environment will contain all the requirements, including
the Google Earth Engine (GEE) API and its dependencies.

Activate the conda environment: `source activate tst_online`

# Step 4: Set up GEE credentials

After activating the environment, set up the credentials using the following 
command:
`python -c "import ee; ee.Initialize()"`

If no credentials are found (if you've never done this before)
an error will appear with the instructions on how to create the
new credentials. The steps involve opening a web page where
you must sign in with the Google Account associated with GEE.
You will authorize access and the page will provide an
authorization code. You will copy and paste it in the terminal where
the script is running. More details can be found 
[here.](https://developers.google.com/earth-engine/python_install_manual#setting-up-authentication-credentials)

# Step 5: Test the GEE installation

Start a python session (just type python), then run the following code:

```
# Import the Earth Engine Python Package
import ee

# Initialize the Earth Engine object, using the authentication credentials.
ee.Initialize()

# Print the information for an image asset.
image = ee.Image('srtm90_v4')
print(image.getInfo())
```

You should see the metadata for an image. To exit the python session
hit Ctrl+d in your keyboard or type exit().

# Step 7: Run the notebook

Start a jupyter notebook (or lab) and open the notebook you need

`jupyter notebook`


