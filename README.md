# First Order Logic Resolution

This python program takes input as given below and resolves Query using Resolution algorithm.
n: number of predicates
n-lines: n predicates, each per line
q: numebr of queries
q-lines: q quries, each per line

where
• Each query will be a single literal of the form Predicate(Constant) or ~Predicate(Constant).
• Variables are lowercase letters.
• All predicates and constants are case-sensitive that starts with an uppercase letter.

Sample input:
1
B(John, Mike)
3
~A(John)
~A(Mike)
A(x) | A(y) | B(x, y)

