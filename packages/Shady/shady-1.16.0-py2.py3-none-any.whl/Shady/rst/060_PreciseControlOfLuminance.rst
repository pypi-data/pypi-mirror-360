Gamma Correction, Dynamic Range Enhancement, and the Canvas
===========================================================

.. contents:: :local:

Overview
--------

One good way to start a visual psychophysics experiment might be::

	world = Shady.World( canvas=True, backgroundColor=0.5, gamma=2.2 )

This automatically creates a `canvas`_, and configures its background color
and `gamma correction`_.  "Noisy-bit" dithering, for `dynamic range
enhancement`_, is also turned on by default: the default value of
`.ditheringDenominator`, for the `World` and all `Stimulus` instances, will
be automatically set to 255 for most graphics cards, or the appropriate
larger `2 ** n - 1` value if your graphics card offers `n>8` bits per DAC).

Now, when you create another stimulus (let's say, a Gabor patch), you'll
most likely want it to have the same `.backgroundColor`, `.gamma`,
`.ditheringDenominator`, `.noiseAmplitude` and `look-up table`_ as the
`World` and its canvas.  One way of ensuring that these properties always
match the surrounding `World` is to use :doc:`property sharing <PropertySharing>`, and one
powerful shortcut is to share the virtual property `.atmosphere` which
encompasses all of these linearization- and dynamic-range-related properties.
So::

	gabor = world.Stimulus(
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		plateauProportion = 0,
		atmosphere = world,       # matched and linked until further notice
	)

That's equivalent to, but easier to type than::

	gabor = world.Stimulus(
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		plateauProportion = 0,
		
		backgroundColor = world,
		gamma = world,
		ditheringDenominator = world,
		noiseAmplitude = world,
		lut = world,
	)

...and that in turn is equivalent to, but easier to type than::

	gabor = world.Stimulus(
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		plateauProportion = 0,
	).LinkPropertiesWithMaster( world,
		'backgroundColor', 'gamma', 'ditheringDenominator', 'noiseAmplitude',
		'lookupTableTextureSize', 'lookupTableTextureSlotNumber', 'lookupTableTextureID',
	)

In the following sections, we'll unpack some of the issues covered above.

Gamma Correction
----------------

The mapping from pixel intensity values to physical luminance is not
necessarily linear. Instead, it often appears to take the shape of an
exponential "gamma" function. Display software must usually correct for
this by applying the inverse gamma function to pixel intensities before
displaying them: this cancels out the non-linearity and causes pixel
luminance to be linear again.

You can apply gamma correction to each Shady `Stimulus` instance by setting
its `.gamma` property, either during construction or subsequently::

    # ...
    stim = world.Stimulus( gamma=2.2 )   # a scalar works, for setting
                                         # all three color channels the same
    
    # ...
    stim.gamma = (2.3, 2.2, 2.1)         # a sequence also works


The standard gamma correction that modern displays are supposed to adopt is
the sRGB profile, which is a standard piecewise function that follows the
`gamma=2.2` exponential curve quite closely (although the exponent
it uses in its exponential portion is actually slightly higher). You can
tell Shady to use the sRGB correction instead of an exponential function
by setting `.gamma` to -1::

    # ...
    stim.gamma = 1.7    # (1.7, 1.7, 1.7)
    stim.gamma = -1     # sRGB

Note that gamma correction will depend on the resolution of your monitor.
Displays will only be configured to the sRGB profile at their native resolution,
and there will likely be a profile in your monitor's settings for sRGB
specifically. For more about gamma correction, see the 
`Wikipedia article <https://en.wikipedia.org/wiki/Gamma_correction>`_.

Dynamic Range Enhancement
-------------------------

Monitors have a limited dynamic range, which determines how precisely they
can present small variations in luminance: close to threshold contrast (not
coincidentally) the monitor's ability to display very small contrasts breaks
down due to the discrete number of available pixel intensities. 

The limitations on maximum contrast are innate to the display hardware, but 
there are tricks to work around the constraints on minimum contrast. Shady
provides two such techniques: "noisy bit" dithering (which is the recommended
approach, enabled by default) and additive noise. Both of these techniques
apply spatiotemporal noise to the drawn pixel values of whichever `Stimulus`
objects you apply them to (including the `World`'s `canvas`_).

"Noisy-bit" dithering (Allard & Faubert 2008) applies a simple stochastic
algorithm before converting floating-point RGB pixel intensity values to the
discrete integer DAC values that are passed to the monitor hardware.
Floating-point RGB values that map to non-integer DAC values are rounded with
a weighted probability inversely proportional to their distance from the
integer values. For example, every time Shady is instructed to draw a pixel
with intensity `(0.5, 0.5, 0.5)`, the desired DAC value on an 8-bit graphics
card is 127.5, half-way between two integer values: with noisy-bit dithering
on, each color channel will then have a 50% chance of being rounded down to
DAC value 127 and a 50% chance of being rounded up to DAC value 128. Similarly,
every time Shady is instructed to draw a pixel with intensity 0.25, the target
value is 63.75, so the pixel will have a 25% chance of being rounded down to 63
and a 75% chance of being rounded up to 64. This probabilistic conversion is
done independently for every color channel in every pixel in every frame, and
the resulting noise causes the luminance values to perceptually average to the
desired between-DAC value. Noisy-bit dithering is enabled by default. The only
property needed to control it is `.ditheringDenominator`, which will be
automatically set to the highest DAC value your monitor can produce (usually
255). Other positive values will cause levels of rounding granularity that
are not suited to your hardware, and should be avoided. You can negate the
value, or set it to 0, to turn dithering off.

Additive noise follows a similar principle to "noisy bit" dithering, but
simply adds random noise to the floating-point value of each pixel
before it is linearized, looked up in a look-up table, or converted to a
discrete DAC value. The resulting noise should again cause the luminance values
to perceptually average to the desired luminance and/or color. You can
control the strength of this noise by setting the `.noiseAmplitude` property
(or its alias, `.noise`). Use negative values for uniform noise, or positive
values for Gaussian noise. Noise is computed once for all color channels of the
same pixel, but may be scaled separately per channel, so you can set
`.noiseAmplitude` to an RGB triplet if you want to tint the noise (or a single
value to set all three channels' noise amplitude the same). Additive noise is
useful if you want to perform "bit stealing" (Tyler 1997), which can be
accomplished using a `look-up table`_: the bit-stealing technique introduces
small-amplitude step changes in chroma which can sometimes become perceptible
if their spatial extent is large: noise can effectively break these areas up.

The differences between the two properties are summarized in the table below:

+---------------------------------------+---------------------------------------+
| |      `.noiseAmplitude` ...          | |    `.ditheringDenominator` ...      |
+=======================================+=======================================+
| | is added before gamma correction    | | is applied after gamma correction;  |
| | (or look-up table lookup);          | |                                     |
+---------------------------------------+---------------------------------------+
| | may be scaled differently in        | | has the same amplitude on average   |
| | different color channels;           | | in all color channels;              |
+---------------------------------------+---------------------------------------+
| | creates noise that is otherwise     | | creates independent noise in each   |
| | perfectly correlated across color   | | color channel;                      |
| | channels;                           | |                                     |
+---------------------------------------+---------------------------------------+
| | is useful in combination with a     | | is recommended for most purposes    |
| | bit-stealing `look-up table`_, or   | | (including when visible noise is    |
| | when you actually want visible      | | used) but is disabled automatically |
| | noise;                              | | when a look-up table is in use;     |
+---------------------------------------+---------------------------------------+
| | can be scaled arbitrarily, and may  | | only dithers between two nearest    |
| | be uniform (when property value is  | | DAC values; the correct property    |
| | negative) or Gaussian (when         | | value (which will be found auto-    |
| | positive).                          | | matically) is `2 ** bits - 1` where |
| |                                     | | `bits` is the bit depth of your     |
| |                                     | | graphics card (usually 8).          |
+---------------------------------------+---------------------------------------+

The following demos may provide further insight:

* :doc:`examples/dynamic-range.py<examples_dynamic-range>` allows you to visualize and interactively explore
  various dynamic-range-enhancement options.

* :doc:`examples/dithering.py<examples_dithering>` performs a numerical sanity-check of our noisy-bit
  dithering implementation. 

* :doc:`examples/precision.py<examples_precision>` performs a quantitative analysis of the effective
  precision achieved by noisy-bit dithering. 

* :doc:`examples/noise.py<examples_noise>` allows you to examine the distribution of random values
  created by the additive noise effect.

* :doc:`examples/fancy-hardware.py<examples_fancy-hardware>` illustrates Shady's support for rendering
  on specialized vision-science hardware, such as the Bits# or ViewPixx,
  that can achieve high dynamic range without dithering (see also the
  `.bitCombiningMode` property of the `Shady.World` class).


Look-up Table
-------------

Instead of using the `.gamma` property to perform automatic gamma-correction,
and allowing the `.ditheringDenominator` to perform automatic noisy-bit
dithering, you can disable both of these features and take control of
linearization and dynamic-range enhancement issues directly yourself, by
specifying a look-up table (LUT).

A look-up table is a discrete series of entries corresponding to a discrete
(usually large, like 65536) number of ideal-luminance ranges that equally
divide up the complete range from 0 to 1.  Each entry is a triplet of integers,
corresponding to the red, green and blue DACs (for most graphics cards, these
will be 8-bit integers).

This is useful only for stimuli whose intensity is one-dimensional (e.g.
monochromatic stimuli). In fact, Shady only uses the first color channel (red)
to compute indices into the LUT.  The output of the LUT will be RGB or RGBA,
however. This means that using a LUT is a form of "indexed color" image
rendering.

Here is a trivially small example of a 2-bit LUT (i.e. 4 entries) for an 8-bit
graphics card (i.e. DAC values go up to 255)::

	   stim.lut = [
	     [   0,   0,   0 ],   # ideal luminances 0    - 0.25 map to black
	     [ 255,   0,   0 ],   #                  0.25 - 0.5  map to red
	     [ 255, 255,   0 ],   #                  0.5  - 0.75 map to yellow
	     [ 255, 255, 255 ],   #                  0.75 - 1.0  map to white
	   ]

To attach a LUT to a `Stimulus`, the easiest way is to call the `SetLUT()` method
or, equivalently, assign to the `.lut` property.  You can assign either a
`Shady.LookupTable` instance, or a valid argument to the `Shady.LookupTable` class
constructor (in which case, such an instance will be constructed automatically).
This means that in practice you can assign:

	- an existing `Shady.LookupTable` instance
	- an `n`-by-3 (or `m`-by-`n`-by-3) array of integers (or a nested list that
	  `numpy` can automatically convert into such an array, as in the example above)
	- a filename of a `.npy`, `.npz` or `.png` file in which you have previously
	  saved a LUT array with `Shady.Linearization.SaveLUT()`

When you then query the `.lut` property, you will see that its value is a
`Shady.LookupTable` instance. Note that creation of such an instance allocates a
texture in OpenGL, so the most efficient use of resources would be to re-use
`Shady.LookupTable` instances wherever appropriate.

Remember that assigning a look-up table *disables* automatic gamma-correction
and noisy-bit dithering.  Assigning `stim.lut = None` or calling `stim.SetLUT(None)`
removes the look-up table and re-enables automatic gamma-correction and noisy-bit
dithering.

It is up to you to specify appropriate values for the LUT entries, although Shady
does provides a utility for computing them according to one particular strategy:
`Shady.Linearization.BitStealingLUT()` which implements a version of the
"bit-stealing" technique (after Tyler 1997).

Bit-stealing allows monochromatic stimuli to be rendered at higher effective dynamic
range, by allowing very small chromatic variations: these create luminance levels
between the existing strictly-gray levels, while hopefully keeping the chromatic
information itself well below the subject's threshold.  The latter point can fail
in some circumstances where there is a very gradual change as a function of distance
(such as at the outer edges of a Hann window): then it is sometimes possible to see
a small step-change in color between large adjacent areas.  To break up this effect,
it is sometimes useful to add a little noise to the signal (as in the dithering
approach, the effect of this noise will be perceptually averaged away over small
spatial and temporal scales).  We've found `noiseAmplitude=1e-4` works well.

The :doc:`examples/dynamic-range.py<examples_dynamic-range>` demo has look-up-table and additive-noise
options, and illustrates some of these points.

Canvas
------

If you create a ``World``::

	world = Shady.World()

it starts off filled with a uniform color.  You can specify this color in
in the constructor call, or manipulate it after construction, via the
`.clearColor` attribute::

	world.clearColor = [ 1, 0.3, 0.5 ]
	
Yeesh. Now, this may be sufficient for some purposes.  But `.clearColor`
is a very simple property that does not change according to your linearization
or dynamic-range-enhancement parameters: it is never gamma-corrected, and is
always applied completely uniformly, so there can be no dithering.

However, if you're doing vision science, you'll probably want both
gamma-correction and dynamic-range enhancement in your stimuli.  And if
you have those things in your *stimuli*, you'll probably need them in the
*backdrop* as well---for example, you may need to eliminate the risk that
a keen-eyed subject can detect the edge of your stimulus bounding-box because
of a just-visible artifact at the boundary between dithered and un-dithered
gray regions.

The solution is to create a "canvas", which is simply a rectangular `Stimulus`
that fills your `World`.  This can be done during `World` construction::

	world = Shady.World( canvas=True )
	
...or after the fact::

	world = Shady.World()
	world.MakeCanvas()

Either way, what you get is a `Stimulus` object with no foreground color,
the name `'canvas'`, and a `.z` value of `+1` (i.e. as far as possible away
from the camera).   In addition, various properties of the canvas are
:doc:`linked <PropertySharing>` to those of the `World` itself.  So if you specify or change any of 
the following properties of `world`:

	- :py:obj:`world.backgroundColor <Shady.World.backgroundColor>`
	- :py:obj:`world.gamma <Shady.World.gamma>`
	- :py:obj:`world.ditheringDenominator <Shady.World.ditheringDenominator>`
	- :py:obj:`world.noiseAmplitude <Shady.World.noiseAmplitude>`
	- :py:obj:`world.lut <Shady.World.lut>`
	- :py:obj:`world.outOfRangeColor <Shady.World.outOfRangeColor>`
	- :py:obj:`world.outOfRangeAlpha <Shady.World.outOfRangeAlpha>`

you will actually be affecting the corresponding properties of
`world.stimuli['canvas']`.  Indeed, these properties of the `World` are only
placeholders and are ignored during rendering of the empty `World` itself at
the start of each frame. Changes in their values *only* cause visible effects
to the extent that they change `Stimulus` instances, such as the canvas, that
are linked in this way.

Avoiding image artifacts
------------------------

For all stimuli:

	Be aware that you may introduce artifacts due to your graphics card's
	linear interpolation between pixel values, whenever you use:
	
	- `.envelopeRotation` values that are not divisible by 90,
	- `.envelopeScaling` values other than 1.0,
	- or non-integer values in the first two coordinates of `.envelopeOrigin`
	  (but if you stick to using `.envelopeTranslation` instead of
	  `.envelopeOrigin`, your stimulus position on screen will always be
	  rounded to an integer number of pixels, avoiding this pitfall).

	For similar reasons, you should always run your display screen at its
	native resolution.

For textured stimuli:

	Transformations of the *carrier* signal (via `.carrierTranslation`,
	`.carrierRotation` and `.carrierScaling`) will also lead to interpolation
	artifacts as above, *if* the carrier content comes from a texture, i.e.
	it is defined by a discrete array of pixels.

For untextured (functionally-generated) stimuli:

	If, on the other hand, the carrier content is entirely functionally
	generated on the GPU functions using the `.signalFunction`,
	`.modulationFunction` and `.windowingFunction` properties, then you do
	not need to worry about interpolation artifacts from carrier
	transformations, because the carrier transformations are applied to
	the coordinate system before the functions are even evaluated.
	
	You should also check whether a carrier transformation pushes your signal
	beyond any spatial or spatio-temporal aliasing limits. For example, if you
	have created an antialiased square-wave signal function as in the
	:doc:`examples/custom-functions.py <examples_custom-functions>` demo, you may think that the
	function automatically avoids components with fewer than 2 pixels per
	cycle. But if you then shrink it with a `.carrierScaling` factor < 1.0,
	you may be back in trouble. 

For moving stimuli:

	Remember that speed (pixels per second or degrees per second) multiplied
	by spatial frequency (cycles per pixel or cycles per degree) gives you
	the flicker frequency of a pixel in Hz (cycles per second). If that is
	greater than half your screen's refresh rate (i.e. > 30Hz, for most
	commercial screens) then you're into spatio-temporal aliasing territory
	(that parallel universe where helicopter blades slow down to a standstill
	and car wheels spin backwards).
	
	