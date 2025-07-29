Luminance and Contrast
======================

Definitions
-----------

Ideal Luminance:

	This means the intensity of a pixel expressed on a scale from 0 to 1, where 0 is the
	lowest intensity the visual display hardware can produce, and 1 is the highest. It is
	often convenient to work with ideal luminances because they allow you to express stimulus
	characteristics in a hardware-independent way.  However you would need to convert them
	to physical luminances (perhaps using the function `IdealToPhysicalLuminance()`) before
	reporting them in a publication.

	In Shady, the carrier content of a `Stimulus` is generally expressed on this ideal
	0-to-1 scale: this includes its `.signalAmplitude`, the pixel values in its floating-point
	texture array (if any), its `.noiseAmplitude` and its `.backgroundColor`.  The only
	exception is when texture content is expressed as an 8-bit integer array (values
	ranging from 0 to 255) - for example when it is loaded directly from an image file.


Physical Luminance:

	This means the intensity of a stimulus patch in real physical units such as candela / m^2.
	Given accurate gamma-correction, we assume that physical luminance is proportional to
	ideal luminance, with an additive offset.  The offset is a consequence of the fact that
	a screen's minimum intensity is never truly zero (either due to reflected ambient light,
	or the imperfect black level of most current screen technologies).   An OLED screen in
	an otherwise perfectly dark room may achieve close to 0 - this is currently the only
	setup in which you can ask how much more black the screen could be and the answer is
	none. None more black.


Ideal Contrast Ratio:

	By "ideal contrast ratio", we mean "a contrast ratio computed from ideal luminance
	values", independent of whether this is computed by the RMS method or the Michelson
	method.  Since ideal luminances go down to zero, ideal contrast ratios can reach 1.0,
	unlike *physical* contrast ratios.
	
	It is sometimes convenient to work with an ideal contrast ratio because it can be
	computed without having to perform actual photometer measurements, and can provide
	an approximation to the corresponding true physical contrast ratio. But you would
	need to convert it to a physical contrast ratio (perhaps with the function
	`IdealToPhysicalContrastRatio()` ) before reporting it in a publication.


Physical Contrast Ratio:

	By "physical contrast ratio", we mean "a contrast ratio computed from physical
	luminance values", independent of whether this is computed by the RMS method or the
	Michelson method.  Since the physical luminance at the location of a "black" pixel
	is never actually zero, a physical contrast ratio will never reach 1.0  (though it
	may come very close, depending on the screen technology and ambient light control).
	

RMS Contrast Ratio:

	This is a method of computing a contrast ratio according to
	:math:`\frac{\sqrt{\frac{1}{N}\sum_x\sum_y (L(x,y) - L_{\mu})^2}}{L_{\mu}}`,
	or in plain text::
	
		 average_over_x_and_y(  (luminance(x,y) - background_luminance) ** 2  ) ** 0.5
		 ----------------------------------------------------------------------------
		                         background_luminance
	
	If `luminance` :math:`L(x,y)` and `background_luminance` :math:`L_{\mu}` are both
	ideal luminances, then the result is an ideal contrast ratio.  If they are both
	physical luminances, then the result is a physical contrast ratio.


Michelson Contrast Ratio:

	This is a method of computing a contrast ratio according to
	:math:`\frac{L_{\max} - L_{\min}}{L_{\max} + L_{\min}}`, or in plain text::
	
				L_max - L_min
				-------------
				L_max + L_min
	
	If `L_max` and `L_min` are both ideal luminances, then the result is an ideal
	contrast ratio.  If they are both physical luminances, then the result is a
	physical contrast ratio.
	
	The Michelson method is best suited to simple periodic stimuli whose luminance
	varies equally above and below the background luminance. For visual noise or
	natural stimuli you would probably want to use an RMS contrast ratio instead.


Normalized Contrast:
	
	This may be a somewhat misleading name, but we use it anyway, as do other
	psychophysical software packages.  To mitigate confusion, we are careful always
	to include the word "ratio" when talking about RMS and Michelson contrast ratios,
	and to omit it here when talking about normalized contrast, which is *not* a
	ratio.
	
	By "normalized contrast", as in the property `Stimulus.normalizedContrast`, we
	mean a straightforward scaling factor that acts as a multiplier on deviations
	of luminance from the background, regardless of absolute luminance level::
	
		 luminance = background_luminance + signal * normalized_contrast
	
	So, for example, if our `background_luminance` is 0.5, in ideal units, and our
	signal is `0.5 * sin(x)`,  a `normalized_contrast` of 1.0 would allow this
	sine-wave signal to span the full luminance range of the screen (note that the
	`background_luminance` could not be anything other than 0.5, otherwise the
	signal would go out of range).   A `normalized_contrast` of 0.2 would mean
	that the same signal spans one fifth of the full intensity range of the
	screen (so now you could set the ideal `background_luminance` to anything from
	0.1 to 0.9).


Conversion utility functions
----------------------------

* `Shady.Contrast.IdealToPhysicalLuminance()`
* `Shady.Contrast.PhysicalToIdealLuminance()`
* `Shady.Contrast.IdealToPhysicalContrastRatio()`
* `Shady.Contrast.PhysicalToIdealContrastRatio()`
* `Shady.Contrast.IdealContrastRatioToNormalizedContrast()`
* `Shady.Contrast.NormalizedContrastToIdealContrastRatio()`

Contrast-ratio computation functions (ideal or physical)
--------------------------------------------------------

* `Shady.Contrast.RMSContrastRatio()`
* `Shady.Contrast.MichelsonContrastRatio()`
