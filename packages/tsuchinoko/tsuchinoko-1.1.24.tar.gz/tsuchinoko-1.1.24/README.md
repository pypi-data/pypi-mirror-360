# Tsuchinoko
[![PyPI](https://badgen.net/pypi/v/tsuchinoko)](https://pypi.org/project/tsuchinoko/)
[![License](https://badgen.net/pypi/license/tsuchinoko)](https://github.com/lbl-camera/tsuchinoko)
[![Build Status](https://github.com/lbl-camera/tsuchinoko/actions/workflows/main.yml/badge.svg)](https://github.com/lbl-camera/tsuchinoko/actions/workflows/main.yml)
[![Documentation Status](https://readthedocs.org/projects/tsuchinoko/badge/?version=latest)](https://tsuchinoko.readthedocs.io/en/latest/?badge=latest)
[![Test Coverage](https://img.shields.io/codecov/c/github/lbl-camera/tsuchinoko/master.svg)](https://codecov.io/github/lbl-camera/tsuchinoko?branch=master)
[![Slack Status](https://img.shields.io/badge/slack-gpCAM-yellow.svg?logo=slack)](https://nikea.slack.com/messages/U7Q1N42F6)

Tsuchinoko is a Qt application for adaptive experiment execution and tuning. Live visualizations show details of 
measurements, and provide feedback on the adaptive engine's decision-making process. The parameters of the adaptive 
engine can also be tuned live to explore and optimize the search procedure.

While Tsuchinoko is designed to allow custom adaptive engines to drive experiments, the 
[gpCAM](https://gpcam.readthedocs.io/en/latest/) engine is a featured inclusion. This tool is based on a flexible and 
powerful Gaussian process regression at the core.

A Tsuchinoko system includes 4 distinct components: the GUI client, an adaptive engine, and execution engine, and a
core service. These components are separable to allow flexibility with a variety of distributed designs.

![Tsuchinoko running simulated measurements](docs/source/_static/running-score.PNG)

## Standard Installation

The latest stable Tsuchinoko version is available on PyPI, and is installable with `pip`. It is recommended that you
use Python 3.12 for this installation.

```bash
pip install tsuchinoko
```

For more information, see the [installation documentation](https://tsuchinoko.readthedocs.io/en/latest/quickstart.html).

## Easy Installation

For Mac OSX and Windows, pre-packaged installers are available. These do not require a base Python installation. See the [installation documentation](https://tsuchinoko.readthedocs.io/en/latest/installers.html) for more details.

- [Latest Windows Installer](https://github.com/lbl-camera/tsuchinoko/releases/latest/download/Tsuchinoko-amd64.exe)
- [Latest Mac OSX Installer](https://github.com/lbl-camera/tsuchinoko/releases/latest/download/Tsuchinoko.app.tgz)

## Resources

* Documentation: https://tsuchinoko.readthedocs.io/en/latest
* Report an issue in Tsuchinoko: [New Bug Report](https://github.com/lbl-camera/tsuchinoko/issues/new?labels=bug)

## About the name

Japanese folklore describes the [Tsuchinoko](https://cryptidz.fandom.com/wiki/Tsuchinoko) as a wide and short snake-like creature living in the mountains of western
Japan. This creature has a cultural following similar to the Bigfoot of North America. Much like the global optimum of a
non-convex function, its elusive nature is infamous.
