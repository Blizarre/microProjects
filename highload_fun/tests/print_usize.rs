#[cfg(test)]
mod tests {
    use highload_fun::print_usize::print_usize_different;
    use highload_fun::print_usize::{print_usize_fast, print_usize_naive, MAX_U64_LENGTH};

    #[test]
    fn various_values() {
        let test_values = [0, 1, 2345678, 111118886666666, 12345678901234567890usize];
        for value in test_values.iter() {
            let reference = format!("{}", value);

            let mut test_buffer = [0u8; MAX_U64_LENGTH];
            let test_buffer = print_usize_fast(*value, &mut test_buffer);
            assert_eq!(
                String::from_utf8(test_buffer.to_vec()).expect("Invalid utf8 string"),
                format!("{}", value)
            );

            let mut test_buffer = [0u8; MAX_U64_LENGTH];
            let test_buffer = print_usize_different(*value, &mut test_buffer);
            assert_eq!(
                String::from_utf8(test_buffer.to_vec()).expect("Invalid utf8 string"),
                format!("{}", value)
            );

            assert_eq!(print_usize_naive(*value), reference);
        }
    }
}
