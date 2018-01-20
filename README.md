# First Order Logic Resolution

This python program takes input as given below and resolves Query using Resolution algorithm.<br/>
n: number of predicates<br/>
n-lines: n predicates, each per line<br/>
q: numebr of queries<br/>
q-lines: q quries, each per line<br/>

where
* Each query will be a single literal of the form Predicate(Constant) or ~Predicate(Constant).
* Variables are lowercase letters.
* All predicates and constants are case-sensitive that starts with an uppercase letter.

__Sample input:__
1<br/>
B(John, Mike)<br/>
3<br/>
~A(John)<br/>
~A(Mike)<br/>
A(x) | A(y) | B(x, y)<br/>
