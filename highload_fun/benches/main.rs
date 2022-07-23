use criterion::{black_box, criterion_group, criterion_main, Criterion};
use highload_fun::parse_int::{parse_int, parse_int_avx, parse_int_simple};
use std::fs::File;
use std::io::prelude::*;

fn criterion_benchmark(c: &mut Criterion) {
    let mut group = c.benchmark_group("Integer parsing");

    let mut testfile = File::open("testdata.dat").unwrap();
    let mut contents = String::new();
    testfile.read_to_string(&mut contents).unwrap();
    let data = contents.as_bytes();
    assert_eq!(parse_int(data), parse_int_simple(data));
    assert_eq!(parse_int(data), parse_int_avx(data));

    group.bench_function("small sample Naive", |b| {
        b.iter(|| parse_int(black_box(data)))
    });
    group.bench_function("small sample AVX", |b| {
        b.iter(|| parse_int_avx(black_box(data)))
    });
    group.bench_function("small sample Naive 2", |b| {
        b.iter(|| parse_int_simple(black_box(data)))
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
