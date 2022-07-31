use std::arch::x86_64::__m256i;
use std::arch::x86_64::_mm256_extracti128_si256;
use std::arch::x86_64::_mm256_mullo_epi32;
use std::arch::x86_64::_mm256_testz_si256;
use std::arch::x86_64::_mm_add_epi32;
use std::arch::x86_64::_mm_cvtsi128_si32;
use std::arch::x86_64::_mm_hadd_epi32;

use std::arch::x86_64::_mm256_castsi256_si128;
use std::arch::x86_64::_mm256_cmpgt_epi32;
use std::arch::x86_64::_mm256_set1_epi32;
use std::arch::x86_64::_mm256_set_epi32;
use std::arch::x86_64::_mm256_sub_epi32;

pub fn parse_int(buffer: &[u8]) -> u64 {
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

pub fn parse_int_simple(buffer: &[u8]) -> u64 {
    let mut number = 0u32;
    let mut accumulator = 0u64;
    let mut idx = 0;

    while idx < buffer.len() {
        let val = *unsafe { buffer.get_unchecked(idx) };
        if val == b'\n' {
            accumulator += number as u64;
            number = 0;
        } else {
            number *= 10;
            number += (val - b'0') as u32;
        }
        idx += 1;
    }
    if number > 0 {
        accumulator += number as u64;
    }
    accumulator
}

// Based on https://stackoverflow.com/questions/49941645/get-sum-of-values-stored-in-m256d-with-sse-avx
// and https://stackoverflow.com/questions/6996764/fastest-way-to-do-horizontal-sse-vector-sum-or-other-reduction
unsafe fn hsum_double_avx(v: __m256i) -> i32 {
    let vlow128 = _mm256_castsi256_si128(v);
    let vhigh128 = _mm256_extracti128_si256(v, 1); // high 128
    let vlow128 = _mm_add_epi32(vlow128, vhigh128); // reduce down to 128

    // Apparently not optimal, see doc for more information
    let vlow128 = _mm_hadd_epi32(vlow128, vlow128);
    let vlow128 = _mm_hadd_epi32(vlow128, vlow128);

    _mm_cvtsi128_si32(vlow128)
}

/// Get a single value from the buffer and cast it as 32
///
/// # Safety
/// Won't check for array boundaries
pub unsafe fn get_val_unchecked(buffer: &[u8], index: usize) -> i32 {
    *buffer.get_unchecked(index) as i32
}

pub fn parse_int_avx(buffer: &[u8]) -> u64 {
    let mut number = 0i32;
    let mut accumulator = 0u64;

    let zero_ascii = unsafe { _mm256_set1_epi32(b'0' as i32) };
    let not_digit_ascii = unsafe { _mm256_set1_epi32((b'0' - 1) as i32) };
    let multiplier =
        unsafe { _mm256_set_epi32(10_000_000, 1_000_000, 100_000, 10_000, 1000, 100, 10, 1) };

    if buffer.len() < 8 {
        panic!("Invalid buffer length");
    }

    let mut index = 0;
    while index < buffer.len() - 8 {
        if buffer[index] == b'\n' {
            accumulator += number as u64;
            index += 1;
            // Now we will try to parse the beginning of the next number using AVX
            unsafe {
                let avx_number = _mm256_set_epi32(
                    get_val_unchecked(buffer, index),
                    get_val_unchecked(buffer, index + 1),
                    get_val_unchecked(buffer, index + 2),
                    get_val_unchecked(buffer, index + 3),
                    get_val_unchecked(buffer, index + 4),
                    get_val_unchecked(buffer, index + 5),
                    get_val_unchecked(buffer, index + 6),
                    get_val_unchecked(buffer, index + 7),
                );
                // Checking which chars are >= '0' (or in that case > '0' - 1)
                // It will be 0xFFFFFFFF is they are digits
                let mask = _mm256_cmpgt_epi32(not_digit_ascii, avx_number);
                // Checking that they are all digits (0xFFFFFFFF)
                let is_good = _mm256_testz_si256(mask, mask);
                if is_good == 1 {
                    // We can use AVX, we have 8 digits
                    let sse_number = _mm256_sub_epi32(avx_number, zero_ascii);
                    let sse_number = _mm256_mullo_epi32(sse_number, multiplier);
                    number = hsum_double_avx(sse_number);
                    index += 8;
                    continue;
                } else {
                    // We cannot, revert back to the old system
                    number = (buffer[index] - b'0') as i32;
                }
            }
        // Then we carry on as usual for the rest of the number
        } else {
            number *= 10;
            number += (buffer[index] - b'0') as i32;
        }
        // If we are on a new number, then we need to check if we can process it using AVX
        index += 1;
    }

    // The bytes that remains will always be done without SSE. That way we don't need to do any array
    // bound checking in the above code
    for val in buffer[index..buffer.len()].iter() {
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
