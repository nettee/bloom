extern crate clap;
extern crate toml;

use std::error::Error;
use std::fs;

use clap::{App};
use toml::Value;
use std::path::{Path, PathBuf};

#[derive(Debug)]
enum ArticleType {
    Post,
    Draft,
}

#[derive(Debug)]
struct Article<'a> {
    path: &'a Path,
    article_type: ArticleType,
}

fn fetch_files(path: PathBuf) -> Vec<PathBuf> {
    path.read_dir().expect("read directory failed")
        .map(|entry| entry.unwrap() )
        .map(|entry| entry.path() )
        .filter(|path| path.is_file())
        .collect()
}

fn import_hexo(hexo_path: &str) -> Result<(), Box<dyn Error>> {
    let hexo_path = Path::new(hexo_path);
    let source_path = hexo_path.join("source");
    let posts_path = source_path.join("_posts");
    let drafts_path = source_path.join("_drafts");
    let posts = fetch_files(posts_path);
    let posts: Vec<Article> = posts.iter()
        .map(|path| Article{ path, article_type: ArticleType::Post })
        .collect();
    let drafts = fetch_files(drafts_path);
    let drafts: Vec<Article> = drafts.iter()
        .map(|path| Article { path, article_type: ArticleType::Draft })
        .collect();
    println!("posts:");
    for post in &posts {
        println!("{:?}", post);
    }
    println!("drafts:");
    for draft in &drafts {
        println!("{:?}", draft);
    }

    Ok(())
}

fn import(config_file: &str) -> Result<(), Box<dyn Error>> {
    let file_content = fs::read_to_string(config_file)?;
    let config: Value = toml::from_str(&file_content)?;

    let hexo_path = config["hexo"]["path"].as_str().ok_or("no hexo path config")?;
    println!("hexo path = {}", hexo_path);
    import_hexo(hexo_path)
}

fn main() {
    println!("Welcome to bloom!");

    let name = env!("CARGO_PKG_NAME");
    let version = env!("CARGO_PKG_VERSION");
    let author = env!("CARGO_PKG_AUTHORS");
    let description = env!("CARGO_PKG_DESCRIPTION");

    let _matches = App::new(name)
        .version(version)
        .author(author)
        .about(description)
        .get_matches();

    import("bloom.toml").expect("import failed");
}
