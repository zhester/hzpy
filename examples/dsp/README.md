Python Data Visualization
=========================

I work a lot with digital signal processing. The typical tools for working in
signal processing include the ubiquitous [MATLAB][1] and the very capable
[Octave][2].

However, as I've been working with Python quite a bit lately, I decided to
look into Python's capability as a signal analysis tool. The benefits of using
Python for this kind of task aren't immediately obvious, but here are a few
I've found:

* Like Octave, Python is open source, and free to use.
* The Python interpretor is more likely to be installed than specialized
  signal processing applications.
* Python has a larger community of users (and number of use cases) than
  individual signal processing applications.
* Unlike signal processing applications which are, almost always, stand-alone
  applications, Python is embedded in many popular applications. Therefore,
  implementing signal processing in Python allows you to implement non-trival
  solutions within these applications.

Of course not everything is sunshine and puppy dogs.

Currently, Python's implementation of numerical analysis presents a bit of a
barrier considering its slogan: _batteries included_. While you can accomplish
a lot of discrete math and numerical analysis using core Python, the
_Pythonic_ way to do it is to reuse existing implementations. This means
installing one or more addons.

Downloading and installing the addons is no big deal, but it really hurts the
portability of any scripts that depend on these addons. Additionally, these
addons don't quite track the current state-of-the-art for Python releases.
For example, in my target application, the plugin API is implemented in Python
3. I can implement Python addons in the plugin architecture, but installing a
non-trivial Python addon to this installation is frought with difficulties.
Furthermore, the particular addons I used are not yet widely deployed for
Python 3. I'll only briefly mention that these particular addons are only
officially released for 32bit interpretors, meaning I have to keep extra
installations of Python around.

If these addons ever get integrated into Python, and can keep up with the
needs of Python developers, the arguments for needing a stand-alone signal
processing application become moot in all but a few corner cases (assuming the
user isn't bound to a preferred syntax).

Nuts and Bolts
--------------

The two addons I used to implement the example script shown were [NumPy][3]
(for stronger array support and a good set of math and numerical analysis
tools) and [matplotlib][4] (for data visualization).

Example Plot
------------
![DSP Plot Display][5]


[1]: http://www.mathworks.com/products/matlab/
[2]: http://www.gnu.org/software/octave/
[3]: http://numpy.scipy.org/
[4]: http://matplotlib.sourceforge.net/
[5]: pyplot.png
