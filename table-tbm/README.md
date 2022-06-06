## Files
- `main.py`: A main python file which can be used to call the generator / create testcases
- `tbm_generator.py`: A file that generates P4 code to implement IP lookup based on tree bit map.
- `sample-8bit.p4`: Sample P4 code that implements tree bit map lookup on 8-bit keys

Run `main.py` to generate a P4 file. Then, you can import that code into the P4 sandbox (or run locally). The first four bytes of the input packet represent the IP address to lookup; the next four bytes represent the next hop determined by the IP lookup.

The `main.py` file also defines the prefixes used in the generated P4 code and has a function for generating random IP addresses to test on.
