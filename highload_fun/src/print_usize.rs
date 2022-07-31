pub const MAX_U64_LENGTH: usize = 20;

pub fn print_usize_naive(value: usize) -> String {
    format!("{}", value)
}

pub fn print_usize_fast(mut value: usize, buffer: &mut [u8]) -> &[u8] {
    let mut max_idx = buffer.len() - 1;
    for (idx, val) in buffer.iter_mut().enumerate().rev() {
        let remainder = (value % 10) as u8;
        *val = remainder + b'0';
        if remainder > 0 {
            max_idx = idx;
        }
        value /= 10;
    }
    &buffer[max_idx..]
}

pub fn print_usize_different(mut value: usize, buffer: &mut [u8]) -> &[u8] {
    let mut max_idx = buffer.len() - 1;
    for idx in (0..buffer.len()).rev() {
        let remainder = (value % 10) as u8;
        buffer[idx] = remainder + b'0';
        if remainder > 0 {
            max_idx = idx;
        }
        value /= 10;
    }
    &buffer[max_idx..]
}
