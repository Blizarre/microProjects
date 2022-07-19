use better_int_parser::{parseint, parseint_sse};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn various_values() {
        let test_values = [
            (
                b"815083965\n455586725\n1527793702".to_vec(),
                2_798_464_392u64,
            ),
            (b"1 10 100 1000 10000 100000".to_vec(), 111111),
            (b"0 10 100 1000 10000 100000".to_vec(), 111110),
            (b"333".to_vec(), 333),
            (
                b"333                   4                     0             3".to_vec(),
                340,
            ),
        ];
        for (data, res) in test_values.iter() {
            assert_eq!(parseint(data), *res);
            assert_eq!(parseint_sse(data), *res);
        }
    }
}
