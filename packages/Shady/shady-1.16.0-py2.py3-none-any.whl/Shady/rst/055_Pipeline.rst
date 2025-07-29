Shader Pipeline Details
=======================

The heart of Shady is a customizable, specialized "fragment shader" program written
in GLSL.  It is designed to ensure that the GPU takes on nearly all of the burden of
frame-by-frame pixel processing, including signal generation, animation, spatial
windowing, contrast modulation in time and space, gamma correction, quantization, and
dynamic-range enhancement tricks.

Specifically, the steps in the shader pipeline are as follows:


1. Compute a *carrier* pattern. Depending on the settings of the `Stimulus`, this may
   be (a) a patch of solid color, (b) a pre-determined *texture* (i.e. an array of
   discrete pixel values), (c) a *signal function* that generates patterns
   procedurally at run-time, or (d) a combination of these options.
   
   The rules for combining different carrier types are as follows:
   
   * Texture and |signalFunction| are additive.
   * If you omit the texture, solid |backgroundColor| is used as the signal
     baseline instead.
   * If you omit the |signalFunction|, it looks the same as a signal function that
     outputs 0 everywhere.
   * |color|, if supplied, is a multiplier for both texture and |signalFunction|
     (though often with qualitatively different effects, because texture values are
     always in the range 0 to 1 whereas signal functions can go negative).
   * An exception to all the above rules is if you omit both texture and
     |signalFunction|, but specify a |color|: then it is assumed you want a
     solid patch of the specified |color|, independent of the |backgroundColor|.
  
   The table below summarizes the possible outcomes:
   
   +-------------------------+--------------------------------------+---------------------+
   |                         |           |signalFunction|           | no |signalFunction| |
   +=========================+======================================+=====================+
   | texture, |color|:       | texture * |color| + signal * |color| | texture * |color|   |
   +-------------------------+--------------------------------------+---------------------+
   | texture, no |color|:    | texture           + signal           | texture             |
   +-------------------------+--------------------------------------+---------------------+
   +-------------------------+--------------------------------------+---------------------+
   | no texture, |color|:    | |backgroundColor| + signal * |color| |      |color|        |
   +-------------------------+--------------------------------------+---------------------+
   | no texture, no |color|: | |backgroundColor| + signal           | |backgroundColor|   |
   +-------------------------+--------------------------------------+---------------------+

2. Translate, rotate or scale the carrier pattern if requested. Carriers are treated
   as infinitely, cyclically repeating patterns for this purpose. In the case of
   procedurally-generated signals, the transformations are actually applied to the
   coordinate system **before** the |signalFunction| is evaluated.

3. Apply contrast effects.  This may include (a) a |windowingFunction| that attenuates
   the edges of the stimulus, (b) another more arbitrary procedural |modulationFunction|
   (for example, sinusoidal contrast modulation), (c) an overall |contrast| scaling
   factor, or (d) a multiplicative combination of these options.
   
   For linearized, psychophysically-accurate stimuli, the `.backgroundAlpha` property
   should be 1.0, in which case contrast effects cause the carrier to be blended with
   the specified `.backgroundColor`. On the other hand, if the `Stimulus` has
   `.backgroundAlpha < 1.0`, contrast effects are mediated through alpha blending with
   other stimuli (and you should not expect the composite result to be accurately
   linearized).
   
4. Translate, rotate or scale the complete stimulus if requested. (Note that scaling,
   and any rotation except a multiple of 90 degrees, will compromise the pixel-perfect
   accuracy of the stimulus content due to interpolation artifacts. As for translations:
   under normal circumstances Shady automatically rounds to the nearest pixel, to avoid
   such interpolation artifacts in ordinary stimulus repositioning.)
    
5. Add noise, if requested. A two-dimensional uniform or Gaussian pixel noise pattern
   can be added to the stimulus at this stage. It is useful at very low amplitudes if
   we intend to apply a bit-stealing lookup-table in the next step, or at higher
   amplitudes if we actually want a visible noise effect.

6. Apply :doc:`gamma-correction and dynamic-range enhancement <PreciseControlOfLuminance>` effects.
   This is done by one of the following procedures:

   DEFAULT OPTION:
       transform each channel's pixel values through the inverse of the screen
       non-linearity, then dither each color-channel independently between the
       DAC values immediately above and immediately below the transformed target
       level, according to the noisy-bit algorithm of Allard & Faubert (2008); 

   OR:
       transform each channel's pixel values through the inverse of the screen
       non-linearity, then re-express the resulting values as 16-bit integers,
       distributing the more- and less-significant bytes either between color
       channels or between adjacent pixels in video memory: specialized
       hardware such as the ViewPixx or Bits# can then reinterpret the video
       content as a high-dynamic-range pattern at the expense of either color
       or resolution;
       
   OR:
       quantize pixel values according to the size of a large (say, 16-bit)
       pre-generated lookup table, then use the table to look up a triplet of
       (red,green,blue) DAC values---for monochromatic stimuli this can
       simultaneously accomplish linearization, bit-stealing (after Tyler, 1997)
       if desired, and further quantization down to the native precision of the
       video hardware;
    
7. If not already accomplished in the previous step, quantize down to 8 bits per
   color channel (or however many bits are supported natively in video memory).

.. |color|               replace:: :py:obj:`.color               <Shady.Stimulus.color>`
.. |backgroundColor|     replace:: :py:obj:`.backgroundColor     <Shady.Stimulus.backgroundColor>`
.. |signalFunction|      replace:: :py:obj:`.signalFunction      <Shady.Stimulus.signalFunction>`
.. |modulationFunction|  replace:: :py:obj:`.modulationFunction  <Shady.Stimulus.modulationFunction>`
.. |windowingFunction|   replace:: :py:obj:`.windowingFunction   <Shady.Stimulus.windowingFunction>`
.. |contrast|            replace:: :py:obj:`.contrast            <Shady.Stimulus.normalizedContrast>`
