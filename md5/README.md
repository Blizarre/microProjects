# Naive md5 implementation

A simple implementation of the md5 algorithm based on the original [RFC 1321](https://tools.ietf.org/html/rfc1321) from _1992_!

I tried to stay as close as possible to the RFC description, so the resulting program is around 15% slower than the `md5sum` implementation from coreutils, which is not that bad.

Even if I spent quite some time on a test harness (`testtools`) including a python script to generate the test data, it is **not** production-ready, the error-handling system is very primitive and has not been tested thoroughly. It was only a weekend project to have a bit of fun learning about this venerable algorithm.

## Build

```
$ make md5
$ ./md5 test.data
28584a85d2a4b5df9e170042fb5f25ed  test.data
```

You can switch from debug to release flags in the Makefile.