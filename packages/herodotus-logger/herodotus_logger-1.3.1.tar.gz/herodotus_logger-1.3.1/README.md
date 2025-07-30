<a name="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![PyPi][pypi-shield]][pypi-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Twitter][twitter-shield]][twitter-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/EmadHelmi/herodotus">
    <img src="static/imgs/logo.png" alt="Logo">
  </a>

<h3 align="center">Herodotus</h3>

  <p align="center">
    An awesome enhanced python logger
    <br />
    <a href="#"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/EmadHelmi/herodotus/tree/main/examples">Examples</a>
    ·
    <a href="https://github.com/EmadHelmi/herodotus/issues">Report Bug</a>
    ·
    <a href="https://github.com/EmadHelmi/herodotus/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#the-history-behind-the-project">The history behind the project</a></li>
        <li><a href="#the-naming-convention">The naming convention</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#basic-usage">Basic usage (no formatter)</a></li>
        <li><a href="#use-with-a-formatter">Use with a Formatter</a></li>
        <li><a href="#using-the-colorizer">Using the colorizer</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->

## About The Project

### The history behind the project

The Python [`logging`][python-logging-url] package
is a powerful tool for logging messages to various streams,
ranging from files to third-party services like [Elasticsearch][elastic-url].

However, there was a particular instance in a project
where I needed to log messages through multiple streams
with varying levels of severity.
To illustrate, I aimed to create a logger object
equipped with three handlers:
one for a rotating file, one for standard output (stdout), and one for Elasticsearch.

My objective was to route each severity level to a specific stream.
Additionally, I intended to apply colorization to
the logs displayed in stdout, while omitting colorization for logs saved in the file.

When I employed code similar to the following:

```python
import logging
import some_colorizer_function

my_logger = logging.getLogger("my_logger")
my_logger.debug(
    some_colorizer_function("some message with %s"),
    "args"
)
```

It yielded a visually appealing colorized output on stdout.
However, when directed to Elasticsearch or written to a file,
the output appeared unattractive due to the presence of ANSI color symbols.
Consequently, I embarked on refining the logging package
and subsequently contemplated making these improvements available for public use.
If you're interested, I welcome you to contribute to this endeavor.

### The naming convention

[Herodotus][Herodotus-wiki] stands as an ancient Greek historian acclaimed as the "Father of History."
Renowned for penning the book "The Histories,"
he holds a position among the earliest contributors
to historical literature.
This opus spans an array of topics encompassing history, geography, cultures, civilizations, and conflicts.
Notably, he adeptly merged meticulous event accounts with captivating narratives.
His opus presents a fusion of historical scrutiny and cultural storytelling,
rendering him a pivotal influencer in the evolution of historical writing.

<!-- GETTING STARTED -->

## Getting Started

I've also created a pypi package for this library. So you can easily use and install it with pip or clone the project.

### Installation

    pip install herodotus_logger --upgrade

<!-- USAGE EXAMPLES -->

## Usage

### Basic usage

1. To begin, it's essential to instantiate a logger object with a designated severity level.
   This configuration dictates that the logger will transmit all severities equal to
   or surpassing the specified level.
   Further insight into severity numbers can be found [here][severity-url].
   For instance, if a logger object is established with a `WARNING` level,
   it will refrain from dispatching `INFO`, `DEBUG`, or `NOTSET` levels to its associated handlers.

   ```python
   import logging
   from herodotus import logger
    
   lg = logger.Logger(
        name="test_logger",
        level=logging.WARNING
   )
   ```
2. You also should give it some handlers. You have two main options to do so:
    1. Use some basic provided handlers in the `herodotus.handlers` which are starting with `Enhanced*`
        - Note that all provided handlers' arguments are as the main one.
          They just accept some
          more arguments I'll explain.
    2. Use any custom or other handlers which are of type `Handler` in python.

    ```python
    import logging
    from sys import stdout
    
    from herodotus import logger
    from herodotus import handlers
    
    lg = logger.Logger(
        name="test_logger",
        level=logging.WARNING,
        handlers=[
            handlers.EnhancedStreamHandler(
                stream=stdout,
                level=logging.WARNING
            ),
            handlers.EnhancedFileHandler(
                filename="logs/test_logfile.log",
                mode="a",
                encoding="utf-8",
                level=logging.CRITICAL
            )
        ]
    )
    ```

3. You're all set! Lean back and simply instruct your logger object to start logging!
    1. Create the `logs` directory:

       ```bash
       mkdir logs
       ```
    2. Call the `logger` logs functions (ex debug, info,...)
       ```python
       lg.logger.info("Hello")
       ```

   However, at this juncture, no action will transpire.
   This outcome arises due to the fact that the log level `lg` is established as `logging.WARNING`, while we endeavor to
   initiate logging with the info level. Evidently, the hierarchy dictates that `log.INFO` holds a lesser value than
   `log.WARNING`.

   Let's try another one:
   ```python
   lg.logger.warning("Hello")
   ```
   and the bash output is:
   ```bash
   2023-08-09T10:39:05|test_logger|WARNING|Hello
   ```
   However, no logs have been recorded in the log file,
   and the rationale behind this outcome is evident.

   Let's run another example:
   ```python
   lg.logger.critical("Hello")
   ```
   and the bash output is:
   ```bash
   2023-08-09T10:45:45|test_logger|CRITICAL|Hello
   ```
   Consequently, the log file located at `logs/test_logfile.log` mirrors the identical output.

### Use strict levels

What should we do If we want strict logging levels. I mean that
I want to log to the stream **JUST** the `warning` level and not higher (ex. `error`.)
It's also simple. You can use `strict_level` parameter and set it `True`:

```python
import logging
from sys import stdout

from herodotus import logger
from herodotus import handlers

lg = logger.Logger(
    name="test_logger",
    level=logging.WARNING,
    formatter=logging.Formatter(
        datefmt="%Y-%m-%dT%H:%M:%S",
        fmt="%(asctime)s %(levelname)s: %(message)s"
    ),
    handlers=[
        handlers.EnhancedStreamHandler(
            stream=sys.stdout,
            level=logging.ERROR,
            strict_level=True
        ),
        handlers.EnhancedFileHandler(
            filename="logs/test_log.log",
            mode="a",
            encoding="utf-8",
            level=logging.WARNING,
            strict_level=True
        )
    ]
)

lg.logger.error("hello, world")
```

If you don't set the `strict_level` parameter, you will see the log message
both in the stdout and the file. But with set it to `True` you don't see the message
in the file.

### Use with a Formatter

I define a default formatter for the logger as follow:

```python
self.formatter = formatter or logging.Formatter(
    datefmt="%Y-%m-%dT%H:%M:%S",
    fmt="%(asctime)s|%(name)s|%(levelname)s|%(message)s"
)
```

But you can change it when you create the logger:

```python
import logging
from sys import stdout

from herodotus import logger
from herodotus import handlers

lg = logger.Logger(
    name="test_logger",
    level=logging.WARNING,
    formatter=logging.Formatter(
        datefmt="%Y-%m-%dT%H:%M:%S",
        fmt="%(asctime)s %(levelname)s: %(message)s"
    ),
    handlers=[
        handlers.EnhancedStreamHandler(
            stream=stdout,
            level=logging.WARNING
        ),
        handlers.EnhancedFileHandler(
            filename="logs/test_logfile.log",
            mode="a",
            encoding="utf-8",
            level=logging.CRITICAL
        )
    ]
)
```

The most important thing to note is that you can also set a different formatter for each handler.
However, if you don't specify a formatter for your handler,
the logger will fall back to using its own default formatter.

```python
import logging
from sys import stdout

from herodotus import logger
from herodotus import handlers

lg = logger.Logger(
    name="test_logger",
    level=logging.WARNING,
    formatter=logging.Formatter(
        datefmt="%Y-%m-%dT%H:%M:%S",
        fmt="%(asctime)s %(levelname)s: %(message)s"
    ),
    handlers=[
        handlers.EnhancedStreamHandler(
            stream=stdout,
            level=logging.WARNING
        ),
        handlers.EnhancedFileHandler(
            filename="logs/test_logfile.log",
            mode="a",
            encoding="utf-8",
            level=logging.CRITICAL,
            formatter=logging.Formatter(
                datefmt="%H:%M:%S",
                fmt="%(asctime)s: %(message)s"
            )
        )
    ]
)
```

### Using the colorizer

Incorporating colors throughout undoubtedly provides a distinctive perspective,
and this holds true in the context of logging as well.
One approach is to leverage the [`colored`][colored-pip-url].
Additionally, I've included user-friendly functions that facilitate the inclusion of colors within your logs.

Let's see some examples:

```python
import logging
from sys import stdout

from herodotus import logger
from herodotus import handlers
from herodotus.utils import colorizer

lg = logger.Logger(
    name="test_logger",
    level=logging.WARNING,
    formatter=logging.Formatter(
        datefmt="%Y-%m-%dT%H:%M:%S",
        fmt="%(asctime)s %(levelname)s: %(message)s"
    ),
    handlers=[
        handlers.EnhancedStreamHandler(
            stream=stdout,
            level=logging.WARNING
        )
    ]
)

lg.logger.critical(colorizer.colorize("Hello", foreground="green"))
```

and the output will be something like this:

![colorizer ex1](static/imgs/colorizer-ex1.png)

You can also add styles (as noted in the [`colored`][colored-style-documentation]).
To do so, just pass your desired styles as a list to the `colorize` function:

```python
lg.logger.critical(colorizer.colorize("Hello", foreground="green", styles=['bold', 'underline']))
```

And the output will be something like this:

![colorizer ex2](static/imgs/colorizer-ex2.png)

But what happens if we add a file handler to a logger which uses the `colorize` function? Let's see:

```python
import logging
from sys import stdout

from herodotus import logger
from herodotus import handlers
from herodotus.utils import colorizer

lg = logger.Logger(
    name="test_logger",
    level=logging.WARNING,
    formatter=logging.Formatter(
        datefmt="%Y-%m-%dT%H:%M:%S",
        fmt="%(asctime)s %(levelname)s: %(message)s"
    ),
    handlers=[
        handlers.EnhancedStreamHandler(
            stream=stdout,
            level=logging.WARNING
        ),
        handlers.EnhancedFileHandler(
            filename="logs/test_logfile.log",
            mode="a",
            encoding="utf-8",
            level=logging.CRITICAL,
            formatter=logging.Formatter(
                datefmt="%H:%M:%S",
                fmt="%(asctime)s: %(message)s"
            )
        )
    ]
)

lg.logger.critical(colorizer.colorize("Hello", foreground="green"))
```

In the log file, you will probably see something like this (If you don't have any plugin or extension to convert ansii
chars to the colors):

![colorize ex3](static/imgs/colorizer-ex3.png)

Finding the appearance unappealing?
Wondering what steps to take next?
No need to fret.
I've got a solution for you.

You can make use of the `msg_func` argument within each of the `Enhanced*` handlers.
This argument expects a function as its type,
so you should provide it with a suitable function.
As an illustration, I've authored a `decolorize` function
in the `herodotus.utils.colorize` package.
This function takes a string containing ANSI color codes and effectively eliminates them:

```python
handlers.EnhancedFileHandler(
    filename="logs/test_logfile.log",
    mode="a",
    encoding="utf-8",
    level=logging.CRITICAL,
    msg_func=colorizer.decolorize,
    formatter=logging.Formatter(
        datefmt="%H:%M:%S",
        fmt="%(asctime)s: %(message)s"
    )

lg.logger.critical(colorizer.colorize("Hello", foreground="green"))
```

Finally, in the log file you will see something like this:

![colorize ex4](static/imgs/colorizer-ex4.png)

<!-- ROADMAP -->


See the [open issues](https://github.com/EmadHelmi/herodotus/issues) for a full list of proposed features(
and known issues).



<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement."
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.



<!-- CONTACT -->

## Contact

Emad Helmi | Find me on Twitter [@EmadHelmi](https://twitter.com/emadhelmi)

Or send me Email [s.emad.helmi@gmail.com](mailto://s.emad.helmi@gmail.com)

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/EmadHelmi/herodotus?style=for-the-badge

[contributors-url]: https://github.com/EmadHelmi/herodotus/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/EmadHelmi/herodotus?style=for-the-badge

[forks-url]: https://github.com/EmadHelmi/herodotus/network/members

[stars-shield]: https://img.shields.io/github/stars/EmadHelmi/herodotus?style=for-the-badge

[stars-url]: https://github.com/EmadHelmi/herodotus/stargazers

[issues-shield]: https://img.shields.io/github/issues/EmadHelmi/herodotus?style=for-the-badge

[issues-url]: https://github.com/EmadHelmi/herodotus/issues

[pypi-shield]: https://img.shields.io/pypi/v/herodotus-logger?style=for-the-badge

[pypi-url]: https://pypi.org/project/herodotus-logger/

[license-shield]: https://img.shields.io/github/license/EmadHelmi/herodotus?style=for-the-badge

[license-url]: https://github.com/EmadHelmi/herodotus/blob/master/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

[linkedin-url]: https://www.linkedin.com/in/emad-helmi-1aa321135/

[twitter-shield]: https://img.shields.io/twitter/follow/EmadHelmi?style=for-the-badge

[twitter-url]: https://twitter.com/EmadHelmi

[python-logging-url]: https://docs.python.org/3/library/logging.html

[elastic-url]: https://www.elastic.co/

[Herodotus-wiki]: https://en.wikipedia.org/wiki/Herodotus

[Python.badge]: https://img.shields.io/badge/Python-20233A?style=for-the-badge&logo=python&logoColor=61DAFB

[Python-url]: https://python.org

[severity-url]: https://docs.python.org/3/library/logging.html#logging-levels

[colored-pip-url]: https://pypi.org/project/colored/

[colored-style-documentation]: https://dslackw.gitlab.io/colored/api/functions/#formatting
