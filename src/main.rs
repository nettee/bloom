extern crate clap;
extern crate toml;

use std::error::Error;
use std::fs;

use clap::{App, Arg, SubCommand};
use toml::Value;

//#[derive(Deserialize)]
//struct Config {
//    hexo: Option<HexoConfig>,
//}
//
//#[derive(Deserialize)]
//struct HexoConfig {
//    path: String,
//}

fn import(config_file: &str) {
    let file_content = fs::read_to_string(config_file).unwrap();
    let config: Value = toml::from_str(&file_content).unwrap();

    println!("config = {:?}", config);
}

fn main() {
    let name = env!("CARGO_PKG_NAME");
    let version = env!("CARGO_PKG_VERSION");
    let author = env!("CARGO_PKG_AUTHORS");
    let description = env!("CARGO_PKG_DESCRIPTION");

    let matches = App::new(name)
        .version(version)
        .author(author)
        .about(description)
        .get_matches();

    import("bloom.toml");

    println!("Welcome to bloom!");
}
