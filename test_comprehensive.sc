// Comprehensive test for LintSc formatter

/*
This is a multi-line block comment.
It should NOT be formatted or indented.
Block comments preserve their original formatting.
*/

// Variable declarations
(
var synths = [];
var current = 0;

// Helper function with nested brackets
{
|freq=440, amp=0.1|
var sig = SinOsc.ar(freq) * amp;
Out.ar(0, sig);
}.play;

// Array with function
[
{ "array item 1" },
{ "array item 2" },
{
// Nested line comment inside function
"array item 3"
}
].do { |item| item.postln };

// Dictionary
(
a: 1,
b: (
inner: 2,
another: 3
),
c: 4
);

).add;

