use rand::prelude::*;
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut file_parse_int = File::create("bench_parse_int.dat").expect("Cannot open file");
    for _ in 0..1000000 {
        writeln!(file_parse_int, "{}", random::<u64>() % (2147483647 + 1))
            .expect("Cannot write to file");
    }

    let mut file_count_uint8 = File::create("bench_count_uint8.dat").expect("Cannot open file");
    let mut data = [0; 1000000];
    for c in data.iter_mut() {
        *c = random();
    }
    file_count_uint8
        .write_all(&data)
        .expect("Cannot write to file");
}
