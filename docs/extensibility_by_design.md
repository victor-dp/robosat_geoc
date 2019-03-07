# How to extend RoboSat.pink: 

RoboSat.pink extensibility allows to custom or enhance only the components you need, and keep everything else as-is.


## Alternate Web UI Templates ##
- Several RoboSat.pink tools can generate, on demand, a Web UI, with `--web_ui` parameter.
- To switch to your own template, just use `--web_ui_template` extra parameter.


## Add a tool ###
- Retrieve RoboSat.pink sources: `git clone https://github.com/datapink/robosat.pink.git`
- Create a new file, in `robosat.pink/robosat_pink/tools` directory, with at least:
  - `add_parser(subparser)`
  - `main(args)`
- Then in `robosat.pink` launch `make install`
 

## Add a model ##
- Retrieve RoboSat.pink sources: `git clone https://github.com/datapink/robosat.pink.git`
- In `robosat.pink/robosat_pink/models` dir, create a new file: `your_model_name.py`.
- The file must contains at least one `Model_name` class.
- These class must itself contains at least `__init__` and `forward` methods.
- Then in `robosat.pink` launch `make install`
- Update config file value: `["model"]["name"]`


## Add a Loss function ##
- Retrieve RoboSat.pink sources: `git clone https://github.com/datapink/robosat.pink.git`
- In `robosat.pink/robosat_pink/losses` dir, create a new file: `your_loss_name.py`.
- The file must contains at least one `Loss_name` class.
- These class must itself contains at least `__init__` and `forward` methods.
- If your loss computation is not auto-differentiable by PyTorch, a related `backward` method, will be needed too.
- Then in `robosat.pink` launch `make install`
- Update config file value: `["model"]["loss"]`
