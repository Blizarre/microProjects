use std::arch::x86_64::__m256i;
use std::arch::x86_64::_mm256_cmpeq_epi8;
use std::arch::x86_64::_mm256_load_si256;
use std::arch::x86_64::_mm256_movemask_epi8;
use std::arch::x86_64::_mm256_set1_epi8;
use std::arch::x86_64::_mm256_testz_si256;

pub fn count_uint8(data: &[u8]) -> usize {
    let mut count = 0usize;
    for i in data.iter() {
        if *i == 127 {
            count += 1;
        }
    }
    count
}

pub fn count_uint8_avx(data: &[u8]) -> usize {
    let all_127 = unsafe { _mm256_set1_epi8(127) };
    // We just assume that the data is aligned
    let mut count = 0usize;
    for c in data.chunks_exact(32) {
        unsafe {
            let chunk_register = _mm256_load_si256(c.as_ptr() as *const __m256i);
            // equal? set to 0xFF
            let equal = _mm256_cmpeq_epi8(chunk_register, all_127);

            // One of the values is NOT zero
            if _mm256_testz_si256(equal, equal) == 0 {
                for val in c.iter() {
                    if *val == 127 {
                        count += 1;
                    }
                }
            }
        }
    }
    for val in data.rchunks_exact(32).remainder() {
        if *val == 127 {
            count += 1;
        }
    }
    count
}

pub fn count_uint8_avx_full(data: &[u8]) -> usize {
    let all_127 = unsafe { _mm256_set1_epi8(127) };
    // We just assume that the data is aligned
    let mut count = 0usize;
    for c in data.chunks_exact(32) {
        unsafe {
            let chunk_register = _mm256_load_si256(c.as_ptr() as *const __m256i);
            // equal? set to 0xFF
            let equal = _mm256_cmpeq_epi8(chunk_register, all_127);
            let mask = _mm256_movemask_epi8(equal);
            count += mask.count_ones() as usize;
        }
    }
    for val in data.rchunks_exact(32).remainder() {
        if *val == 127 {
            count += 1;
        }
    }
    count
}
