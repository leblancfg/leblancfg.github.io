Title: Notes on installing CUDA, CuDNN and Tensorflow on Manjaro
Date: 2018-08-24
Category: Linux
Tags: linux, manjaro, cuda, cudnn, tensorflow, GPU, nvidia, GTX960
Slug: installing-cuda-cudnn-tensorflow-nvidia-gtx960
Authors: François Leblanc
Summary: An in-depth, step-by-step guide to installing CUDA, CuDNN and Tensorflow on Linux with an NVIDIA GeFORCE GTX960 graphics card.

I've finally done it. After 50+ hours spent trying to install GPU support for Tensorflow over the span of a year and a half, I have finally done it. I'm happy to say that I have CUDA 9.2, CuDNN 7.2, and compiled Tensorflow from source well enough that I can train a Resnet on Imagenet-100 in a barely decent amount of time. Take that, cloud!

Now, NVIDIA has had a notoriously bad driver support for Linux, which famously led to Mr Torvalds flipping a finger directed at them in a 2012 interview. And even today it is exceedingly hard to not pull your hair out trying to do so. Having spent many, many days configuring it and getting a collection of black screens, consoles and no-boots, here's what it took to install tensorflow on my machine.

I ended up using the Manjaro distribution, as it was the only one between Ubuntu, Linux Mint, Scientific Linux and Debian to just work out of the box. After further experimentation, I have to say I've grown quite used to using `pacman` instead of `apt`. They also support a community edition that comes bundled with the i3 window manager, which greatly fits my obsession for the last year to go mouseless (as possible). But that's another blog post.

I assume that many people have gone through the same steps as I have, and I would blame none of them for having given up before reaching the end. If there's one lesson to learn from this situation, it's that your calculated ROI on purchasing a (or many) GPUs for training neural networks should consider the possible time it will take to troubleshoot their installation.

## Research
Before you buy anything, do your research. At the time of purchase, the GeFORCE 10xx series was still far away, and the 960 was at the top of the chart for performance / price ratio. I've spent a few dozen hours using Keras since, but as I am still a novice, this suits my needs quite nicely. As of writing, the new 20xx series is slated to be released any day now, but it's still unclear whether the tensor cores they'll be packing are going to make much difference in terms of performance.

By default, most distributions will install and use the open source GPU drivers called `nouveau`, which won't cut it with what we've got in mind for this GPU. The hardest and most frustrating part of the installation process is to get the NVIDIA drivers running. I was met with a lot of black screens, flashing cursor bars, and giving up trying to back-fix things from the GRUB console.

Lots of resources exist out there, but the following have been the most useful in finally making things run:

* [Nvidia CUDA Toolkit driver Install Ubuntu Mint Linux 16.04](https://www.youtube.com/watch?v=_fj4YISX3bw) by [Librebowski](https://www.youtube.com/channel/UCCX3ZAfic1j7BMH-MA2LLbg), specifically his blurb at the beginning about Manjaro
* [Deep Learning Setup in Arch Linux: From Start To Finish with PyTorch + TensorFlow + Nvidia CUDA + Anaconda](https://medium.com/@k_efth/deep-learning-in-arch-linux-from-start-to-finish-with-pytorch-tensorflow-nvidia-cuda-9a873c2252ed) by [Kyriakosi Efthymiadis](https://medium.com/@k_efth?source=post_header_lockup)
* The official [Tensorflow documentation](https://www.tensorflow.org/install/install_sources) for how to install it from source. Great guide, but some sections are already dated. Take instructions with a grain of salt.

## Specs

* **CPU**: Intel(R) Core(TM) i5-6500 CPU @ 3.20GH
* **GPU**: NVIDIA Corporation GM206 [GeForce GTX 960]
* **Monitor**: Asus 24" HDMI

*Notes: I cannot be 100% sure, but I believe that connecting by HDMI sold part of my problems. YMMV*

## Steps

### Install Manjaro from Live USB
I was getting a blank screen when trying to boot with the Non-Free Drivers option, so went with Free Drivers.

### Update system

    sudo pacman -Syyu

### Install NVIDIA drivers
In my case, I wasn't able to make the regular `nvidia` package work, but had to go with the `390xx` series. This step just worked from the GUI. Go to Manjaro Settings > Drivers and simply install that one.

Reboot and cross your fingers.

### Install CUDA and CuDNN

    sudo pacman -S cuda cudnn

This next one may or may not be useful:

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64

Reboot and cross your fingers.

### Install Anaconda
Next up, we download the latest Anaconda release. Since we'll be compiling TF right after, we'll grab bazel while we're at it.

    sudo pacman -S anaconda bazel

### Compile Tensorflow from source
There are no handy CUDA 9.2 wheels for tensorflow available for Linux, so you'll need to compile from source. Don't worry, it'll put hair on your chest. I also ran into r1.10 asking for the `keras_applications` Python module to be installed, so according to [this SO post](https://stackoverflow.com/questions/51771039/error-compiling-tensorflow-from-source-no-module-named-keras-applications) I also pip-installed the following:

    conda install keras
    pip install keras_applications==1.0.4 --no-deps
    pip install keras_preprocessing==1.0.2 --no-deps
    pip install h5py==2.8.0

Then:

    git clone https://github.com/tensorflow/tensorflow
    cd tensorflow
    git branch r1.10
    bash configure

You'll then be asked a series of questions you'll probably want to Google before you answer. In my case, I did:

* All default until
* CUDA Support: Y
* CUDA 9.2
* CUDNN 7.2
* TensorRT: default
* NCCL: 1.3 (only one GPU on this box anyhow)
* CUDA compute capabilities: 3.5,5.2
	- Get this from [here](https://developer.nvidia.com/cuda-gpus)
* compile w/ clang: default
* Bazel compiler flags: -mavx -mavx2 -mfma -msse4.2
* Android: default 

And finally:

    bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg

And finally, installing with pip (the exact filename might change in your case):

    sudo pip install /tmp/tensorflow_pkg/tensorflow-1.10.0-cp36-cp36m-linux_x86_64.whl

### Test your build

    cd ~
    python -c "import tensorflow as tf;hello = tf.constant('Hello, TensorFlow!');\
    sess = tf.Session();print(sess.run(hello));'

