use rand::prelude::*;
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut file = File::create("testdata.dat").expect("Cannot open file");
    for _ in 0..1000000 {
        writeln!(file, "{}", random::<u64>() % 2147483647).expect("Cannot write to file");
    }
}
