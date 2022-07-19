pub fn parseint(buffer: &[u8]) -> u64 {
    let mut number = -1i32;
    let mut accumulator = 0u64;

    for val in buffer.iter() {
        if number >= 0 {
            if val.is_ascii_digit() {
                number *= 10;
                number += (val - b'0') as i32;
            } else {
                accumulator += number as u64;
                number = -1;
            }
        } else if val.is_ascii_digit() {
            number = (val - b'0') as i32;
        }
    }
    if number > 0 {
        accumulator += number as u64;
    }
    accumulator
}

pub fn parseint_sse(buffer: &[u8]) -> u64 {
    let mut number = -1i32;
    let mut accumulator = 0u64;

    for val in buffer.iter() {
        if number >= 0 {
            if val.is_ascii_digit() {
                number *= 10;
                number += (val - b'0') as i32;
            } else {
                accumulator += number as u64;
                number = -1;
            }
        } else if val.is_ascii_digit() {
            number = (val - b'0') as i32;
        }
    }
    if number > 0 {
        accumulator += number as u64;
    }
    accumulator
}
