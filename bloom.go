package main

import (
	"errors"
	"github.com/nettee/bloom/core"
	"github.com/nettee/bloom/model"
	"github.com/urfave/cli/v2"
	"log"
	"os"
)

func main() {

	app := &cli.App{
		Name:    "bloom",
		Version: "0.0.1",
		Authors: []*cli.Author{
			{
				Name:  "nettee",
				Email: "nettee.liu@gmail.com",
			},
		},
		Usage: "Markdown article manager",
		Commands: []*cli.Command{
			{
				Name:    "create",
				Aliases: []string{"c", "new", "n"},
				Usage:   "create article or collection",
				Flags: []cli.Flag{
					&cli.StringFlag{
						Name:  "en",
						Value: "",
						Usage: "The article's English name",
					},
					&cli.StringFlag{
						Name:  "cn",
						Value: "",
						Usage: "The article's Chinese name",
					},
				},
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					en := c.String("en")
					cn := c.String("cn")
					if en == "" {
						return errors.New("english name required")
					}
					if cn == "" {
						return errors.New("chinese name required")
					}
					return core.CreateArticle(en, cn)
				},
			},
			{
				Name:    "update",
				Aliases: []string{"u"},
				Usage:   "update meta data",
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					articlePath := c.Args().First()
					article, err := model.NewArticle(articlePath)
					if err != nil {
						return err
					}
					return core.UpdateArticleMeta(article)
				},
			},
			{
				Name:    "list",
				Aliases: []string{"l"},
				Usage:   "list articles and collections",
				Action: func(c *cli.Context) error {
					return core.ListItems()
				},
			},
			{
				Name: "show",
				Aliases: []string{"s"},
				Usage: "show article details",
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					articlePath := c.Args().First()
					article, err := model.NewArticle(articlePath)
					if err != nil {
						return err
					}
					return core.ShowArticle(article)
				},
			},
			{
				Name: "upload",
				Aliases: []string{"u"},
				Usage: "upload images",
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					articlePath := c.Args().First()
					article, err := model.NewArticle(articlePath)
					if err != nil {
						return err
					}
					return core.UploadImages(article)
				},
			},
			{
				Name:    "publish",
				Aliases: []string{"pub", "p", "deploy", "d"},
				Usage:   "publish an article to (possibly) different platforms",
				Flags: []cli.Flag{
					&cli.StringFlag{
						Name:    "platform",
						Aliases: []string{"to"},
						Value:   "",
						Usage:   "The article's English name",
					},
				},
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					articlePath := c.Args().First()
					article, err := model.NewArticle(articlePath)
					if err != nil {
						return err
					}
					return core.PublishArticle(article, c.String("platform"))
				},
			},
		},
	}

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}
