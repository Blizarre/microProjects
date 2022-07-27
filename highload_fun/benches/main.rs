use criterion::{black_box, criterion_group, criterion_main, Criterion};
use highload_fun::count_uint8::count_uint8;
use highload_fun::count_uint8::count_uint8_avx;
use highload_fun::count_uint8::count_uint8_avx_full;
use highload_fun::parse_int::{parse_int, parse_int_avx, parse_int_simple};
use std::arch::x86_64::__m256i;
use std::fs::File;
use std::io::prelude::*;

fn parse_int_group(c: &mut Criterion) {
    let mut group = c.benchmark_group("Integer parsing");

    let mut testfile = File::open("bench_parse_int.dat").unwrap();
    let mut contents = String::new();
    testfile.read_to_string(&mut contents).unwrap();
    let data = contents.as_bytes();
    assert_eq!(parse_int(data), parse_int_simple(data));
    assert_eq!(parse_int(data), parse_int_avx(data));

    group.bench_function("Naive", |b| b.iter(|| parse_int(black_box(data))));
    group.bench_function("AVX", |b| b.iter(|| parse_int_avx(black_box(data))));
    group.bench_function("Streamlined", |b| {
        b.iter(|| parse_int_simple(black_box(data)))
    });
}

fn count_uint8_group(c: &mut Criterion) {
    let mut group = c.benchmark_group("Count uint8");

    let mut contents = Vec::new();
    let mut test_file = File::open("bench_count_uint8.dat").unwrap();
    test_file.read_to_end(&mut contents).unwrap();
    let mut large_array = vec![0u8; 1024 * 1024 * 10].into_boxed_slice();

    // This is ugly, but the data loaded into the register must e aligned on 32 BYTES boundaries
    let aligned = unsafe {
        let (_before, aligned_mm256, _after) = large_array.align_to_mut::<__m256i>();
        assert!(aligned_mm256.len() * 8 > contents.len());
        std::slice::from_raw_parts_mut(aligned_mm256.as_ptr() as *mut u8, contents.len())
    };
    // This will fail if the file is too large
    aligned.copy_from_slice(&contents);

    group.bench_function("Naive", |b| b.iter(|| count_uint8(black_box(aligned))));
    group.bench_function("AVX", |b| b.iter(|| count_uint8_avx(black_box(aligned))));
    group.bench_function("Full AVX", |b| {
        b.iter(|| count_uint8_avx_full(black_box(aligned)))
    });
}

criterion_group!(benches, parse_int_group, count_uint8_group);
criterion_main!(benches);
