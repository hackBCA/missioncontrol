# hackBCA III Website

## Development

### Installation
**Make sure you are using Python 3.4.x when running this.**

(Using `virtualenv` is recommended. Call your virtual environment folder `venv`; otherwise make sure to add the folder name in the `.gitignore`.)

Clone this repository onto your machine.

#### Requirements
Requirements can be installed all at once through `pip` using the requirements file:

`pip install -r requirements.txt`

Install Sass in order to compile the `.scss` files to `.css`.

Once Sass is installed, run the following command to compile to `css` to the right folder:

`sass --watch /path/to/css/sass/:/path/to/css/ --style compressed`

The path will be different depending on the Blueprint the `.scss` files need to be compiled for.

#### Configuration
There are 3 different configurations for this website:

- `default_config.cfg` (default values)
- `dev_config.cfg` (development values)
- `prod_config.cfg` (production values)

`dev_config.cfg` will override `default_config.cfg`, and `prod_config.cfg` will override `dev_config.cfg`.

Obtain one of these files from an authorized person and place one of these configuration files with all of the configuration values in the root of the project.

**IMPORTANT: Make sure none of the configuration files are committed into Git or publicly available!**

### Running
Run the application with Python 3:

`python run.py`

Visit the website at `localhost:5000`.