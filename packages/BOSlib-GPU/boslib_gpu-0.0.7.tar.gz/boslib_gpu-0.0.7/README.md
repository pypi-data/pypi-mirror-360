# BOSlib-GPU
This library is the extra pacage for [BOSlib](https://github.com/ogayuuki0202/BOSlib) that makes GPU parallel processing available.

## Key Features
- Short, concise code for 3D reconstruction and quantification
- GPU parallel processing 

## Warning

The BOSlib-GPU is still in its *beta* state. This means that
it still might have some bugs and the API may change. However, testing and contributing
is very welcome, especially if you can contribute with new algorithms and features.

## Installing
### 1. Install PyTorch
Please install Pytorch 2.x .
Make sure that CUDA  is available on your PC.
<https://pytorch.org/get-started/locally/>
### 2. Install torch_radon
Please install torch_radon　<https://torch-radon.readthedocs.io/en/latest/getting_started/install.html>

    git clone https://github.com/matteo-ronchetti/torch-radon.git
    cd torch-radon
    python setup.py install
or

    docker pull matteoronchetti/torch-radon
or if you are running Linux 

    wget -qO- https://raw.githubusercontent.com/matteo-ronchetti/torch-radon/master/auto_install.py  | python -

### 3. Install BOSlib
Use PyPI: <https://pypi.org/project/BOSlib-GPU>:

    pip install BOSlib-GPU 

Or compile from source

Download the package from the Github: https://github.com/ogayuuki0202/BOSlib-GPU/archive/refs/heads/main.zip
or clone using git

    git clone https://github.com/ogayuuki0202/BOSlib-GPU.git
    cd BOSlib-GPU
    python setup.py install 

## Methods

Please see our Documentation below.
[Documentation](https://foamy-trilby-a77.notion.site/BOSlib-Documentation-1b2338a536ad8050ac53ee2d606b68e5?pvs=4)

## Contributors
Pleae refer original [BOSlib]((https://github.com/ogayuuki0202/BOSlib)