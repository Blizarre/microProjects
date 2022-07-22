#[cfg(test)]
mod tests {
    use better_int_parser::parseint;
    use better_int_parser::parseint_avx;
    use better_int_parser::parseint_simple;

    #[test]
    fn various_values() {
        let test_values = [
            (
                b"815083965\n455586725\n1527793702".to_vec(),
                2_798_464_392u64,
            ),
            (b"1\n10\n100\n1000\n10000\n100000".to_vec(), 111111),
            (b"100000\n10000\n1000\n100\n10\n1".to_vec(), 111111),
            (b"1\n1\n1\n1\n1\n9".to_vec(), 14),
            (b"0\n10\n100\n1000\n10000\n100000".to_vec(), 111110),
            (b"333222111".to_vec(), 333222111),
            (b"333\n4\n0\n3".to_vec(), 340),
        ];
        for (data, res) in test_values.iter() {
            println!("{}", std::str::from_utf8(data).expect("Invalid test data"));
            assert_eq!(parseint(data), *res);
            assert_eq!(parseint_avx(data), *res);
            assert_eq!(parseint_simple(data), *res);
        }
    }
}
