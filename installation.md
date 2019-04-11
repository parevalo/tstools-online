# Step 1: Get miniconda

You need a working Python installation to use the tool. The easiest way to
install the tool and dependencies is through the use of a conda virtual
environment. If you don’t have conda installed, you can get a minimum version
(miniconda). You can download the installers for your platform here:

https://docs.conda.io/en/latest/miniconda.html

Choose the bash installer for python 3.7, 64-bits
and follow the following instructions depending on your OS:

- For macOS/Unix systems: Use bash installer. If asked to initialize miniconda,
  answer 'yes'. Once the installation is finished, you will need to log out
  of your operating system's user session and then log back in.
- For Windows: run the executable. Leave the advanced options as they are and
  proceed with the installation.


# Step 2: Clone the repo

Issue the following command in your Anaconda prompt:

`git clone https://github.com/parevalo/tstools-online`

If you get an error indicating that git is not installed, run:

`conda install git`

Then cd into the tstools-online folder.

# Step 3: Create a conda environment

Inside the newly created folder, locate the requirements.yml file. Then
create a new conda environment using that file with the following command:

`conda env create -f requirements.yml`

The newly created environment will contain all the requirements, including
the Google Earth Engine (GEE) API and its dependencies.

Activate the conda environment: `conda activate tst_online`

# Step 4: Set up GEE credentials

If you've never used Google Earth Engine through the python API
in your computer, you will need to set up credentials. For that,
type:

`earthengine authenticate`

It will open a web page where you must sign in with the Google
account associated with GEE. Once authorized, the page will provide an
authorization code. Copy and paste it in the terminal where
the script is running. If done properly, it should say
"Successfully saved authorization token".

More details can be found
[here.](https://developers.google.com/earth-engine/python_install_manual#setting-up-authentication-credentials)

# Step 5: Test the GEE installation

Start a python session (just type python), then run the following code
(lines that start with # are comments, you don't need to run those):

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

# Step 6: Run the notebook

Start a jupyter notebook (or lab):

`jupyter notebook`

Once open, click on `ts_explorer.ipynb`. Then click Cell > Run all.
If you enabled appmode, you can just click on the "App Mode" button.
Once you're done, you can close the browser window and the terminal
window were you typed all the commands.

# TO RUN THE NOTEBOOK AGAIN:

If you want to re-run the notebook at another time, you don't need to
re-run the installation steps (1 to 6). You will only need to:

- Open a new terminal (macOS, linux) or the Anaconda prompt (Windows)
- Activate the conda environment: `conda activate tst_online`
- cd to the repository folder (the tstools-online folder)
- Start a jupyter notebook: `jupyter notebook`
