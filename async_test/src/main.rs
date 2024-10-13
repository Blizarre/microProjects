use clap::Parser;
use log::{self, LevelFilter};
use reqwest::{Client, Url};
use simple_logger::SimpleLogger;
use std::path::PathBuf;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;
use tokio_stream::StreamExt;

#[derive(Parser, Debug, Clone)]
struct Opts {
    directory: String,
    urls: Vec<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    SimpleLogger::new().with_level(LevelFilter::Info).init()?;

    log::info!("Booting");

    let options = Opts::parse();
    let mut promises = vec![];

    let path = PathBuf::from(options.directory);

    log::info!("Starting the requests");
    for url in options.urls {
        println!("00");
        promises.push(fetch_file(Url::parse(&url)?, path.clone()));
    }

    log::info!("Waiting for the responses");
    for promise in promises {
        promise.await?;
    }

    log::info!("All done");
    Ok(())
}

async fn fetch_file(url: Url, path: PathBuf) -> Result<(), Box<dyn std::error::Error>> {
    println!("aa");
    let file_name = path.join(
        url.path_segments()
            .and_then(|x| x.last())
            .and_then(|x| if x.is_empty() { None } else { Some(x) })
            .unwrap_or("unknown.txt"),
    );

    log::info!("Fetching {:?} into {:?}", url, file_name);

    let client = Client::new();
    println!("bb");
    let mut file = File::create(file_name).await?;
    println!("cc");

    let response = client.get(url.clone()).send().await?;

    let mut stream = response.bytes_stream();

    while let Some(item) = stream.next().await {
        let bytes = item?;
        file.write_all(&bytes).await?;
    }

    Ok(())
}
