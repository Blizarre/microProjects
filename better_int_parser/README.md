# Small helper project to help me solve https://highload.fun/tasks/1 

Always compare a semi-naive implementation with a fast one, and run tests to make sure that it is valid. 

## Generate some test data (1MB):
```
cargo run
```

## Code quality checks
```
cargo fmt; cargo clippy
```

## Test and run the benchmarks
```
cargo test
cargo bench --profile release
```