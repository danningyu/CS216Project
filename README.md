# CS 216 Project

## How to use
- **All relevant code is in `table-tbm/` folder.**
- Consult the README in that folder for more details.


## Useful commanands (all in mininet)
- Ping all hosts: `pingall`
- Set up a host to receive packets: `<host> python receive.py`
- Send packet: `<host> python send.py <dest_host> <msg>`
- Open terminals in hosts: `xterm <host_name>`


## Old Code Folders
### unibit_trie Folder
- `simple_unibit.p4`: A file that implements a unibit trie with 3 prefixes: `0*`, `1*`, and `111*`.
- `unibit_trie.py`: A file that generates P4 code for a unibit tree. The prefixes contained in the script were taken from the file.
- `unibit_code_gen.p4`: A file that uses the output of `trie.p4` to generate a P4 file. It's like `test.p4`, but the trie isn't hardcoded into the file.

The idea is look at `test.p4` first to get a basic understanding of how to implement a unibit trie, using a simpler example of only 3 prefixes. Then, `trie.py` and `code_gen.p4` extend that to infinitely many prefixes.

To create `code_gen.p4`, run the following commands:  
`python3 trie.py`  
`p4c code_gen.p4`

The first command will create some `.p4gen` files, which will be incorporated into `code_gen.p4` by the compiler. The second command will output a file called `code_gen.p4i`. You can then copy paste the contents into the [P4 sandbox](https://p4.org/sandbox-page/) to test the code.

### tbm_prototype Folder
- This folder contains tree bitmap files created during the prototyping phase.

- `treebitmap.p4`: A file that implements a hard coded tree bitmap example. Uses some C syntax, so it does not compile.
- `trie_tbm.py`: A file that generates variable declarations for a tree bitmap P4 program in a file called `var_decls.p4gen`.
- `code_gen_tbm.p4`: A file that takes in the output created by `trie_tbm.py` to create an incomplete P4 program. The ingress block is missing.
- `sample-8bit.p4`: A file that implements a tree bitmap with a simple example.

