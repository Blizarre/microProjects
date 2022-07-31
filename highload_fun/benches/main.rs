use criterion::{black_box, criterion_group, criterion_main, Criterion};
use highload_fun::count_uint8::count_uint8;
use highload_fun::count_uint8::count_uint8_avx;
use highload_fun::count_uint8::count_uint8_avx_full;
use highload_fun::count_uint8::count_uint8_avx_full_2;
use highload_fun::parse_int::{parse_int, parse_int_avx, parse_int_simple};
use highload_fun::print_usize::print_usize_different;
use highload_fun::print_usize::MAX_U64_LENGTH;
use highload_fun::print_usize::{print_usize_fast, print_usize_naive};
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
    group.bench_function("Full AVX v2", |b| {
        b.iter(|| count_uint8_avx_full_2(black_box(aligned)))
    });
}

fn print_usize_group(c: &mut Criterion) {
    let mut group = c.benchmark_group("Print usize number");
    let test_number = 1234567890123456789;
    let mut test_buffer = [0u8; MAX_U64_LENGTH];
    group.bench_function("Naive", |b| {
        b.iter(|| black_box(print_usize_naive(black_box(test_number))))
    });
    group.bench_function("fast", |b| {
        b.iter(|| {
            black_box(print_usize_fast(black_box(test_number), &mut test_buffer));
        })
    });
    group.bench_function("different", |b| {
        b.iter(|| {
            black_box(print_usize_different(
                black_box(test_number),
                &mut test_buffer,
            ));
        })
    });
}

criterion_group!(
    benches,
    parse_int_group,
    count_uint8_group,
    print_usize_group
);
criterion_main!(benches);
