use better_int_parser::{parseint, parseint_sse};
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use std::fs::File;
use std::io::prelude::*;

fn criterion_benchmark(c: &mut Criterion) {
    let mut testfile = File::open("testdata.dat").unwrap();
    let mut contents = String::new();
    testfile.read_to_string(&mut contents).unwrap();
    let data = contents.as_bytes();
    assert_eq!(parseint(data), parseint_sse(data));

    c.bench_function("small sample", |b| b.iter(|| parseint(black_box(data))));
    c.bench_function("small sample", |b| b.iter(|| parseint_sse(black_box(data))));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
