**Raymond Hawkins - CZ Biohub - ML Science Coding Challenge**

### Installation Instructions ###

The following installation instructions were used to set up the environment in WSL (Ubuntu 24.04.2).

    conda create -y --name 06_image_translation python=3.10
    conda activate 06_image_translation
    conda install -y ipykernel nbformat nbconvert black jupytext ipywidgets
    pip install viscy[metrics,visual]==0.2.0rc1 jupyterlab
    pip install torchmetrics==1.4.0
    pip install ipyfilechooser ipympl ttach
    pip install --upgrade jupyter

### Part 1 ###

- I worked through the notebook solution.ipynb in Windows Subsystem for Linux running Ubuntu with a single
NVIDIA RTX 6000 Ada generation, changing paths where necessary
- In the notebook, I visualized the trained models outputs following the cells where the pretrained models outputs
were visualized. 
- To implement an interactive gui, I used ipywidgets to create a user interface that allows one to:

a. Select a .zarr file to load

b. Select a .ckpt VS model to load

c. Select and update the position in the zarr store to use as input to the model

d. Apply the model, and,

e. Visualize input, target, output and all encoder/decoder featuremaps using matplotlib.

The virtual stain viewer (and thus visualizing the trained model feature maps) can be demo'ed in demo_virtual_stain_viewer.ipynb

The interactive gui was inspired by JuNkIE (https://bitbucket.org/rfg_lab/junkie/src/master/junkie.py) a Jupyter
Notebook image exploration package developed by our lab. Parts of the code were generated using PyCharm's AI assist autofill.

To run the gui, please ensure that you have IPython and IPyWidgets correctly configured to work with matplotlib. You
will also need to install ipyfilechooser (https://pypi.org/project/ipyfilechooser/) and ipympl
(https://www.npmjs.com/package/jupyter-matplotlib). Afterwards, you may need to reinstall Jupyter for changes to take effect:

    pip install ipyfilechooser ipympl
    pip install --upgrade jupyter

### Part 2 ###

- I wrote a script (predict_vs.py) based on the solution.ipynb file to infer membrane and nuclei from a phase video in time
- The script works with the associated dataset, although further work would need to be done to generalize it to all data
  (e.g. the script assumes the XY dimensions are 2046x2003 and pads accordingly, but this could be generalized to any
  possible dimension)
- To get rid of intensity fluctuations I have implemented naive gaussian smoothing in the temporal dimension and
  test-time augmentation (TTA). TTA reduces intensity fluctuations by ensembling the predictions from 24 randomly
  augmented versions of the input image. The result is a reduction in intensity fluctuations without phantom artifacts
  that are caused by the gaussian filter (at the cost of longer inference time)
  - TTA requires the ttach package (https://github.com/qubvel/ttach/tree/master) which can be installed with


    pip install ttach


- I have implemented the script as a CLI using an argparser (written by copilot and editted by myself) which takes the
  following arguments:
  - "--model" or "-m": the path to the .ckpt model checkpoint.
  - "--input" or "-i": the path to the ome zarr dataset.
  - "--output" or "-o": the path to save the output ome zarr predictions.
  - "--smoothing": the type of regularization for temporal intensity fluctuations (None, "gaussian", or "tta")


