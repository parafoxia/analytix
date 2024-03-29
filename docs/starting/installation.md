# Installation

## With pip

You can install analytix using the pip package manager using the following command:

```sh
pip install analytix
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration:

You can also install the latest development version if you wish:

=== "Prereleases"

    ```sh
    pip install analytix --pre
    ```

=== "From GitHub"

    ```sh
    pip install git+https://github.com/parafoxia/analytix
    ```

## With git

if you don't want to use pip for whatever reason, you can install directly from GitHub instead:

```sh
git clone https://github.com/parafoxia/analytix
python setup.py install
```

## With the intention to contribute

If you wish to contribute to analytix, you also need to install the development dependencies:

```sh
git clone https://github.com/<username>/analytix
cd analytix
pip install -r requirements/dev.txt
```

where `<username>` is your GitHub username.
