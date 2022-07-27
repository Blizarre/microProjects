#[cfg(test)]
mod tests {
    use highload_fun::count_uint8::count_uint8;
    use highload_fun::count_uint8::count_uint8_avx;
    use std::arch::x86_64::__m256i;

    #[test]
    fn various_values() {
        let mut large_array = [0u8; 4096];
        // This is ugly, but the data loaded into the register must e aligned on 32 BYTES boundaries
        let aligned = unsafe {
            let (_before, aligned_mm256, _after) = large_array.align_to_mut::<__m256i>();
            let final_len = 256;
            assert!(aligned_mm256.len() * 8 >= final_len);
            std::slice::from_raw_parts_mut(aligned_mm256.as_ptr() as *mut u8, final_len)
        };
        let test_values = [
            ([0x00, 0x34, 0x56, 0x78, 0x12, 0x34].as_ref(), 0usize),
            ([0x12, 0x34, 0x56, 0x78, 0x12, 0x7f].as_ref(), 1usize),
            (
                [
                    0x12, 0x34, 0x56, 0x78, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f, 0x12,
                    0x7f, 0x12, 0x7f, 0x12, 0x34, 0x56, 0x78, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f,
                    0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x34, 0x56, 0x78, 0x12, 0x7f, 0x12,
                    0x2f, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x7f, 0x12, 0x34, 0x56, 0x78,
                    0x12, 0x7f, 0x12, 0x3f, 0x12, 0x3f, 0x12, 0x3f, 0x12, 0x7f, 0x12, 0x73, 0x12,
                    0x34, 0x56, 0x78, 0x12, 0x7f, 0x12, 0x4f, 0x12, 0x4f, 0x12, 0x4f, 0x12, 0x6f,
                    0x12, 0x79, 0x12, 0x34, 0x56, 0x78, 0x12, 0x7a, 0x12, 0x5f, 0x12, 0x75, 0x12,
                    0x7f, 0x12, 0x2f, 0x12, 0x7f, 0x12, 0x34, 0x56, 0x78, 0x12, 0xaf, 0x12, 0x6f,
                    0x12, 0x6e, 0x12, 0x74, 0x12, 0x75, 0x12, 0x3f, 0x12, 0x34, 0x56, 0x78, 0x12,
                    0x7a, 0x12, 0x8f, 0x12, 0xaa, 0x12, 0x70, 0x12, 0x74, 0x12, 0x5f, 0x12, 0x34,
                    0x56, 0x78, 0x12, 0x6f, 0x12, 0x9f, 0x12, 0xfa, 0x12, 0x78, 0x12, 0x9f, 0x12,
                    0x0f, 0x12, 0x34, 0x56, 0x78, 0x12, 0x6f, 0x12, 0x9f, 0x12, 0xfa, 0x12, 0x78,
                    0x12, 0x9f, 0x12, 0x0f,
                ]
                .as_ref(),
                22usize,
            ),
        ];

        for (idx, (data, res)) in test_values.iter().enumerate() {
            let length = data.len();
            aligned[..length].copy_from_slice(data);
            let aligned_data = &aligned[..length];
            println!("Test short {} count_uint8", idx);
            assert_eq!(count_uint8(aligned_data), *res);
            println!("Test short {} count_uint8_sse", idx);
            assert_eq!(count_uint8_avx(aligned_data), *res);
        }
    }
}
