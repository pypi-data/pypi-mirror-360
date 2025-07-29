# kzleet

- HomePage: https://github.com/kzhu2099/KZ-leet
- Issues: https://github.com/kzhu2099/KZ-leet/issues

[![PyPI Downloads](https://static.pepy.tech/badge/kzleet)](https://pepy.tech/projects/kzleet)

Author: Kevin Zhu, with code that may be from others (credit given).

This is a library with solutions of LeetCode everyday that is updated as quickly as possible. If I am unable to create a solution, it may not be there.

If you have a solution or would like to contribute a different one email me at kzhu2099@gmail.com. If I use yours, I will make sure to give credit!!

Note: dates follow the UTC date as does LeetCode.
Important: please visit the disclaimer below.

## Features

- a (hopefully) long list of (hopefully) unique LeetCode Solutions
- ability to contribute

## Installation

To install kzleet, use pip: ```pip install kzleet```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install kzleet
source .venv/bin/activate
pip install kzleet

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install kzleet
.venv\Scripts\activate
pip install kzleet

deactivate # when you are completely done
```

## Usage

You may look at the problems by importing like so:

`from kzleet import Solution_####` where `####` is the problem number of the problem. They are also sorted by the LeetCode given difficulty in different files.

There may be multiple implementations: just add a letter after (`_A, _B`) for different ones.

## License

The License is an MIT License found in the LICENSE file.

## Disclaimer

This library provides personal / community solutions from LeetCode.
They are not the Editorial solutions that you find there, and are in no means as good as theirs.
This is for educational purposes to provide a different perspective on problems.
also, I will try my best to answer all problems. If I can't, I may ask AI (due to not having time) or it having a significantly improved solution. I will always write if it uses AI.