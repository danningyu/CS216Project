# CS 216 Project

## Files
- `test.p4`: A file that implements a unibit trie with 3 prefixes: `0*`, `1*`, and `111*`.
- `trie.py`: A file that generates P4 code for a unibit tree. The prefixes contained in the script were taken from the file.
- `code_gen.p4`: A file that uses the output of `trie.p4` to generate a P4 file. It's like `test.p4`, but the trie isn't hardcoded into the file.

The idea is look at `test.p4` first to get a basic understanding of how to implement a unibit trie, using a simpler example of only 3 prefixes. Then, `trie.py` and `code_gen.p4` extend that to infinitely many prefixes.

To create `code_gen.p4`, run the following commands:  
`python3 trie.py`  
`p4c code_gen.p4`

The first command will create some `.p4gen` files, which will be incorporated into `code_gen.p4` by the compiler. The second command will output a file called `code_gen.p4i`. You can then copy paste the contents into the [P4 sandbox](https://p4.org/sandbox-page/) to test the code.

## Header format
The header format currently used is:
- 8 bit source address
- 8 bit destination address
- 8 bit output face (to check for correctness)
- Everything after that is considered payload

We currently forward based on **source**, not destination address. Yes, this is wrong, but I'm too lazy to fix it.
