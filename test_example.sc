// This is a test file for the LintSc formatter
/* Block comment - should not be formatted */

SynthDef(\test, {
arg freq=440, amp=0.1;
var sig;
sig = SinOsc.ar(freq) * amp;
Out.ar(0, sig);
}).add;


// Example with brackets
(
var array = [1, 2, 3];
var dict = (a: 1, b: 2);
{
// nested comment
var x = 100;
[x, x+1, x+2]
}.value;
)

